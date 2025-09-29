import streamlit as st, pandas as pd
from utils.ui import bootstrap, section

conn = bootstrap()
section("Price Book", "Costs and sell rates (used by quotes)")

with st.form("add_item"):
    name = st.text_input("Item name")
    category = st.text_input("Category", value="General")
    unit = st.selectbox("Unit", ["hour","m2","m3","unit"])
    unit_cost = st.number_input("Unit cost (your cost)", 0.0, 100000.0, 0.0)
    unit_rate = st.number_input("Unit sell rate", 0.0, 100000.0, 100.0)
    notes = st.text_input("Notes", value="")
    if st.form_submit_button("Add item") and name:
        conn.execute("INSERT INTO price_items(name, category, unit, unit_cost, unit_rate, notes) VALUES (?,?,?,?,?,?)",
                     (name, category, unit, unit_cost, unit_rate, notes))
        conn.commit()
        st.success("Item added.")

with st.expander("Price book", expanded=False):
    df = pd.read_sql_query("SELECT id, name, category, unit, unit_cost, unit_rate, notes FROM price_items ORDER BY category, name", conn)
    st.dataframe(df, width='stretch')
