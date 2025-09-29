import streamlit as st
import pandas as pd
from utils.ui import bootstrap, section

conn = bootstrap()
section("Business Essentials", "Insurance, regos, subscriptions — costs & due dates")

with st.form("add_ess"):
    name = st.text_input("Name")
    provider = st.text_input("Provider")
    cost = st.number_input("Cost", 0.0, 100000.0, 0.0)
    cycle = st.selectbox("Billing cycle", ["monthly","quarterly","yearly","once"])
    next_due = st.date_input("Next due")
    notes = st.text_input("Notes", value="")
    if st.form_submit_button("Add item") and name:
        conn.execute("""INSERT INTO essentials(name, provider, cost, billing_cycle, next_due, notes) VALUES (?,?,?,?,?,?)""",
                     (name, provider, cost, cycle, next_due.isoformat(), notes))
        conn.commit()
        st.success("Added.")

df = pd.read_sql_query("SELECT id, name, provider, cost, billing_cycle, next_due, notes FROM essentials ORDER BY date(next_due) ASC", conn)
st.dataframe(df, width='stretch')

st.subheader("Upcoming (next 60 days)")
df2 = pd.read_sql_query("""SELECT name, provider, cost, billing_cycle, next_due FROM essentials
WHERE date(next_due) BETWEEN date('now') AND date('now','+60 day')
ORDER BY date(next_due) ASC""", conn)
st.dataframe(df2, width='stretch')
