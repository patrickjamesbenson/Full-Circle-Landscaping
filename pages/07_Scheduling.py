import streamlit as st
import pandas as pd
from datetime import date
from utils.ui import bootstrap, section
from utils.db import get_conn

conn = bootstrap()
section("Scheduling", "Assign jobs, dates, and crew; keep 1–2 weeks ahead")

st.subheader("Jobs (Scheduled/All)")
df = pd.read_sql_query("""
SELECT j.id, j.scheduled_date, j.start_time, j.end_time, j.crew, j.status, q.id as quote_id, l.name as customer, l.suburb
FROM jobs j
LEFT JOIN quotes q ON j.quote_id=q.id
LEFT JOIN leads l ON q.lead_id=l.id
ORDER BY COALESCE(j.scheduled_date, '9999-12-31') ASC, j.start_time ASC
""", conn)
st.dataframe(df, use_container_width=True, height=350)

st.subheader("Update / Assign Job")
jid = st.number_input("Job ID", min_value=1, step=1)
col1, col2, col3 = st.columns(3)
with col1:
    d = st.date_input("Date", value=date.today())
with col2:
    start = st.text_input("Start (HH:MM)", value="08:00")
with col3:
    end = st.text_input("End (HH:MM)", value="11:00")
crew = st.text_input("Crew (semicolon-separated)", value="Tony;Sam")
status = st.selectbox("Status", ["Scheduled","In Progress","Done","Invoiced"], index=0)
if st.button("Save scheduling"):
    conn.execute("""UPDATE jobs SET scheduled_date=?, start_time=?, end_time=?, crew=?, status=? WHERE id=?""",
                 (d.isoformat(), start, end, crew, status, jid))
    conn.commit()
    st.success("Job updated.")
