# SQL Student Management Demo — Supabase/PostgreSQL

## Stack
- Streamlit
- PostgreSQL hosted on Supabase
- psycopg2

## Local setup
1. Create `.streamlit/secrets.toml` by copying `.streamlit/secrets.toml.example`.
2. Replace placeholders with the Supabase **Session pooler** connection parameters.
3. Never commit `secrets.toml`.
4. Install dependencies:
   `pip install -r requirements.txt`
5. Run:
   `streamlit run app.py`

## Streamlit Community Cloud
Upload the project to GitHub. In Streamlit Community Cloud, paste the contents of your real
`.streamlit/secrets.toml` into the app's Secrets settings, then deploy `app.py`.

## Classroom safety
The Custom SQL Query Lab intentionally accepts only SELECT/WITH queries. Use Supabase SQL Editor
when demonstrating INSERT, UPDATE, DELETE, DDL, transactions, triggers, etc.
