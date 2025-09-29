import streamlit as st, pandas as pd
from utils.ui import bootstrap, section

conn = bootstrap()
section("Services (Seasonal & Ongoing)", "Add/edit services and tag by season")

with st.form("add_service"):
    name = st.text_input("Service name")
    desc = st.text_area("Description", height=80)
    season = st.selectbox("Season", ["summer","winter","all"])
    ongoing = st.checkbox("Ongoing (maintenance)")
    submitted = st.form_submit_button("Add service")
    if submitted and name:
        conn.execute("INSERT INTO services(name, description, season, is_ongoing) VALUES (?,?,?,?)",
                     (name, desc, season, 1 if ongoing else 0))
        conn.commit()
        st.success("Service added.")

with st.expander("All services", expanded=False):
    df = pd.read_sql_query("SELECT id, name, description, season, is_ongoing FROM services", conn)
    if not df.empty:
        df["is_ongoing"] = df["is_ongoing"].map({0:"No",1:"Yes"})
        st.dataframe(df, width='stretch')
    else:
        st.info("No services yet.")
