import streamlit as st
import pandas as pd
from utils.ui import bootstrap, section
from utils.db import get_conn

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

df = pd.DataFrame(conn.execute("SELECT id, name, description, season, is_ongoing FROM services").fetchall())
if not df.empty:
    df["is_ongoing"] = df["is_ongoing"].map({0:"No",1:"Yes"})
    st.dataframe(df, use_container_width=True)
else:
    st.info("No services yet.")
