import streamlit as st
import psycopg2
import pandas as pd

def get_connection():
    cfg = st.secrets["postgres"]
    return psycopg2.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 5432)),
        dbname=cfg.get("database", "postgres"),
        user=cfg["user"],
        password=cfg["password"],
        sslmode=cfg.get("sslmode", "require"),
    )

def fetch_df(query, params=None):
    conn = get_connection()
    try:
        return pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()

def execute(query, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

