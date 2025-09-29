import streamlit as st, pandas as pd
from datetime import date
from utils.ui import bootstrap, section
from utils.xldb import read, write, next_id

bootstrap(); section("Scheduling","Assign jobs, dates, crew; keep 1–2 weeks ahead")
quotes = read("Quotes"); jobs = read("Jobs")
with st.expander("Create Job from Quote", expanded=False):
    qid = st.number_input("Quote ID", min_value=1, step=1); d = st.date_input("Date", value=date.today())
    s = st.text_input("Start (HH:MM)", value="08:00"); e = st.text_input("End (HH:MM)", value="11:00")
    crew = st.text_input("Crew", value="Tony;Sam")
    if st.button("Create Job"):
        jid = next_id(jobs); row = {"id":jid,"quote_id":qid,"scheduled_date":d.isoformat(),"start_time":s,"end_time":e,"crew":crew,"status":"Scheduled"}
        jobs = pd.concat([jobs, pd.DataFrame([row])], ignore_index=True); write("Jobs", jobs); st.success("Job created.")
with st.expander("Jobs (schedule)", expanded=False):
    jf = jobs.copy()
    if "scheduled_date" not in jf.columns: jf["scheduled_date"]=None
    jf["scheduled_date"] = pd.to_datetime(jf["scheduled_date"], errors="coerce")
    st.dataframe(jf.sort_values("scheduled_date", na_position="last"), use_container_width=True, hide_index=True)
