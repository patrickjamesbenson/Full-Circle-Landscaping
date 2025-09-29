import streamlit as st
import pandas as pd
from utils.ui import bootstrap, section
from utils.db import get_conn

conn = bootstrap()
section("Price Book", "Define items and rates (used by quotes)")

with st.form("add_item"):
    name = st.text_input("Item name")
    category = st.text_input("Category", value="General")
    unit = st.selectbox("Unit", ["hour","m2","m3","unit"])
    unit_rate = st.number_input("Unit rate", 0.0, 100000.0, 100.0)
    notes = st.text_input("Notes", value="")
    submitted = st.form_submit_button("Add item")
    if submitted and name:
        conn.execute("INSERT INTO price_items(name, category, unit, unit_rate, notes) VALUES (?,?,?,?,?)",
                     (name, category, unit, unit_rate, notes))
        conn.commit()
        st.success("Item added.")

df = pd.read_sql_query("SELECT id, name, category, unit, unit_rate, notes FROM price_items ORDER BY category, name", conn)
st.dataframe(df, use_container_width=True)
