import streamlit as st
import pandas as pd
from utils.ui import bootstrap, section
from utils.db import get_conn

conn = bootstrap()
section("Roles & Responsibilities (Stub)", "Add role descriptions; we can expand later")

with st.form("add_role"):
    role = st.text_input("Role name")
    desc = st.text_area("Description", height=80)
    resp = st.text_area("Responsibilities (bullets, one per line)", height=120)
    if st.form_submit_button("Add role") and role:
        conn.execute("INSERT INTO roles(role_name, description, responsibilities) VALUES (?,?,?)", (role, desc, resp))
        conn.commit()
        st.success("Role added.")

df = pd.read_sql_query("SELECT id, role_name, description, responsibilities FROM roles", conn)
st.dataframe(df, use_container_width=True)
