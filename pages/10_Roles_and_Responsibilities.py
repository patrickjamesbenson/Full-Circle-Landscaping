import streamlit as st, pandas as pd
from utils.ui import bootstrap, section

conn = bootstrap()
section("Roles & Responsibilities (RACI)", "Adapted UI using editable tables")

st.subheader("Roles")
with st.form("add_role"):
    role = st.text_input("Role name")
    desc = st.text_area("Description", height=80)
    resp = st.text_area("Responsibilities (bullets, one per line)", height=120)
    if st.form_submit_button("Add role") and role:
        conn.execute("INSERT INTO roles(role_name, description, responsibilities) VALUES (?,?,?)", (role, desc, resp))
        conn.commit()
        st.success("Role added.")
with st.expander("Roles table", expanded=False):
    df = pd.read_sql_query("SELECT id, role_name, description, responsibilities FROM roles", conn)
    st.dataframe(df, width='stretch')

st.subheader("RACI Matrix")
with st.expander("Edit RACI (Task, R, A, C, I)", expanded=False):
    raci = pd.read_sql_query("SELECT id, task, R, A, C, I FROM raci ORDER BY id", conn)
    edited = st.data_editor(raci, num_rows="dynamic", key="raci_editor", width='stretch')
    if st.button("Save RACI"):
        conn.execute("DELETE FROM raci")
        for _, r in edited.iterrows():
            if (r.get("task") or "").strip():
                conn.execute("INSERT INTO raci(task,R,A,C,I) VALUES (?,?,?,?,?)", (r.get("task",""), r.get("R",""), r.get("A",""), r.get("C",""), r.get("I","")))
        conn.commit()
        st.success("RACI saved.")
