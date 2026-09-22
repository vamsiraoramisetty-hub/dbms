import streamlit as st
import pandas as pd
from database import fetch_df, execute

st.set_page_config(page_title="SQL Student Management", page_icon="🎓", layout="wide")
st.title("🎓 SQL Student Management System")
st.caption("PostgreSQL / Supabase classroom demo")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Students", "Courses", "Enrollment", "SQL Query Lab"]
)

if page == "Dashboard":
    st.subheader("Dashboard")
    try:
        students = int(fetch_df("SELECT COUNT(*) AS n FROM student").iloc[0]["n"])
        courses = int(fetch_df("SELECT COUNT(*) AS n FROM course").iloc[0]["n"])
        enrollments = int(fetch_df("SELECT COUNT(*) AS n FROM enrollment").iloc[0]["n"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Students", students)
        c2.metric("Courses", courses)
        c3.metric("Enrollments", enrollments)
        st.subheader("Recent enrollments")
        st.dataframe(fetch_df("""
            SELECT e.enrollment_id, s.name, c.course_name, e.enroll_date, e.grade
            FROM enrollment e
            JOIN student s ON s.student_id=e.student_id
            JOIN course c ON c.course_id=e.course_id
            ORDER BY e.enrollment_id DESC LIMIT 10
        """), use_container_width=True)
    except Exception as e:
        st.error(f"Database connection error: {e}")

elif page == "Students":
    st.subheader("Student Management")
    action = st.radio("Action", ["View", "Add", "Update", "Delete"], horizontal=True)

    if action == "View":
        st.code("SELECT * FROM student ORDER BY student_id;", language="sql")
        st.dataframe(fetch_df("SELECT * FROM student ORDER BY student_id"), use_container_width=True)

    elif action == "Add":
        with st.form("add_student"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            department = st.text_input("Department")
            semester = st.number_input("Semester", 1, 12, 1)
            submitted = st.form_submit_button("Add Student")
        if submitted:
            try:
                execute("""INSERT INTO student(name,email,department,semester)
                           VALUES (%s,%s,%s,%s)""",
                        (name, email, department, semester))
                st.success("Student added.")
            except Exception as e:
                st.error(str(e))

    elif action == "Update":
        df = fetch_df("SELECT student_id, name FROM student ORDER BY student_id")
        if df.empty:
            st.info("No students found.")
        else:
            options = {f'{r.student_id} - {r.name}': int(r.student_id) for _, r in df.iterrows()}
            selected = st.selectbox("Student", list(options))
            sid = options[selected]
            current = fetch_df("SELECT * FROM student WHERE student_id=%s", (sid,)).iloc[0]
            with st.form("update_student"):
                name = st.text_input("Name", current["name"])
                email = st.text_input("Email", current["email"])
                department = st.text_input("Department", current["department"] or "")
                semester = st.number_input("Semester", 1, 12, int(current["semester"] or 1))
                submitted = st.form_submit_button("Update")
            if submitted:
                try:
                    execute("""UPDATE student SET name=%s,email=%s,department=%s,semester=%s
                               WHERE student_id=%s""",
                            (name,email,department,semester,sid))
                    st.success("Student updated.")
                except Exception as e:
                    st.error(str(e))

    else:
        df = fetch_df("SELECT student_id, name FROM student ORDER BY student_id")
        if df.empty:
            st.info("No students found.")
        else:
            options = {f'{r.student_id} - {r.name}': int(r.student_id) for _, r in df.iterrows()}
            selected = st.selectbox("Student to delete", list(options))
            if st.button("Delete Student", type="primary"):
                try:
                    execute("DELETE FROM student WHERE student_id=%s", (options[selected],))
                    st.success("Student deleted. Related enrollments are deleted by ON DELETE CASCADE.")
                except Exception as e:
                    st.error(str(e))

elif page == "Courses":
    st.subheader("Course Management")
    action = st.radio("Action", ["View", "Add"], horizontal=True)
    if action == "View":
        st.code("SELECT * FROM course ORDER BY course_id;", language="sql")
        st.dataframe(fetch_df("SELECT * FROM course ORDER BY course_id"), use_container_width=True)
    else:
        with st.form("add_course"):
            course_name = st.text_input("Course name")
            credits = st.number_input("Credits", 1, 10, 4)
            submitted = st.form_submit_button("Add Course")
        if submitted:
            try:
                execute("INSERT INTO course(course_name,credits) VALUES (%s,%s)", (course_name,credits))
                st.success("Course added.")
            except Exception as e:
                st.error(str(e))

elif page == "Enrollment":
    st.subheader("Enrollment")
    action = st.radio("Action", ["View", "Enroll Student"], horizontal=True)
    if action == "View":
        query = """
        SELECT e.enrollment_id, s.name, c.course_name, e.enroll_date, e.grade
        FROM enrollment e
        JOIN student s ON s.student_id=e.student_id
        JOIN course c ON c.course_id=e.course_id
        ORDER BY e.enrollment_id;
        """
        st.code(query, language="sql")
        st.dataframe(fetch_df(query), use_container_width=True)
    else:
        students = fetch_df("SELECT student_id,name FROM student ORDER BY name")
        courses = fetch_df("SELECT course_id,course_name FROM course ORDER BY course_name")
        if students.empty or courses.empty:
            st.warning("Add students and courses first.")
        else:
            smap = {f'{r.name} ({r.student_id})': int(r.student_id) for _,r in students.iterrows()}
            cmap = {r.course_name: int(r.course_id) for _,r in courses.iterrows()}
            with st.form("enroll"):
                s = st.selectbox("Student", list(smap))
                c = st.selectbox("Course", list(cmap))
                grade = st.text_input("Grade", "")
                submitted = st.form_submit_button("Enroll")
            if submitted:
                try:
                    execute("""INSERT INTO enrollment(student_id,course_id,grade)
                               VALUES (%s,%s,%s)""",
                            (smap[s],cmap[c],grade or None))
                    st.success("Enrollment created.")
                except Exception as e:
                    st.error(str(e))

else:
    st.subheader("SQL Query Lab")
    demos = {
        "Simple SELECT": "SELECT * FROM student ORDER BY student_id;",
        "WHERE": "SELECT * FROM student WHERE semester = 2 ORDER BY name;",
        "INNER JOIN": """SELECT s.name, c.course_name, e.grade
FROM student s
JOIN enrollment e ON s.student_id = e.student_id
JOIN course c ON e.course_id = c.course_id
ORDER BY s.name;""",
        "GROUP BY": """SELECT department, COUNT(*) AS number_of_students
FROM student
GROUP BY department
ORDER BY number_of_students DESC;""",
        "Aggregate": """SELECT semester, COUNT(*) AS students
FROM student
GROUP BY semester
ORDER BY semester;""",
        "Subquery": """SELECT name, email
FROM student
WHERE student_id IN (
    SELECT student_id FROM enrollment
    WHERE course_id = (
        SELECT course_id FROM course
        WHERE course_name = 'Database Management Systems'
    )
)
ORDER BY name;"""
    }
    choice = st.selectbox("Demonstration query", list(demos))
    query = demos[choice]
    st.code(query, language="sql")
    if st.button("Run Demonstration Query"):
        st.dataframe(fetch_df(query), use_container_width=True)

    st.divider()
    st.subheader("Custom read-only query")
    st.warning("For classroom safety, this box accepts only SELECT or WITH queries.")
    custom = st.text_area("SQL", "SELECT * FROM student ORDER BY student_id;", height=150)
    if st.button("Run Custom Query"):
        cleaned = custom.strip().lower()
        if not (cleaned.startswith("select") or cleaned.startswith("with")):
            st.error("Only SELECT or WITH queries are allowed here.")
        elif ";" in custom.rstrip(";"):
            st.error("Please run one statement at a time.")
        else:
            try:
                st.dataframe(fetch_df(custom), use_container_width=True)
            except Exception as e:
                st.error(str(e))

