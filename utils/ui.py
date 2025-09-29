import streamlit as st
from .db import get_conn, init_db
from .seed import ensure_seed

def bootstrap():
    """Initialise DB and seed on first run."""
    conn = get_conn()
    init_db(conn)
    ensure_seed(conn)
    return conn

def section(title, subtitle=None):
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)

def success(msg):
    st.success(msg)

def error(msg):
    st.error(msg)
