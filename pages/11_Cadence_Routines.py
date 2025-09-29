import streamlit as st, pandas as pd
from utils.ui import bootstrap, section
from utils.xldb import read, write, next_id

bootstrap(); section("Cadence — Daily / Weekly / Monthly","Internal routines")

with st.expander("Add task", expanded=False):
    df = read("Cadence_Tasks")
    with st.form("tform"):
        name = st.text_input("Task"); freq = st.selectbox("Frequency", ["daily","weekly","monthly"])
        col1,col2,col3,col4 = st.columns(4)
        with col1: dow = st.number_input("Day of week (0=Mon)", 0,6,0) if freq=="weekly" else None
        with col2: dom = st.number_input("Day of month", 1,31,1) if freq=="monthly" else None
        with col3: hour = st.number_input("Hour", 0,23,9)
        with col4: minute = st.number_input("Minute", 0,59,0)
        owner = st.text_input("Owner", value="Tony"); active = st.checkbox("Active", value=True)
        notes = st.text_input("Notes", value="")
        if st.form_submit_button("Add task") and name:
            nid = next_id(df)
            row = {"id":nid,"name":name,"frequency":freq,"day_of_week":dow,"day_of_month":dom,"hour":hour,"minute":minute,"owner":owner,"active":1 if active else 0,"notes":notes}
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True); write("Cadence_Tasks", df); st.success("Added.")
with st.expander("Tasks table", expanded=False):
    st.dataframe(read("Cadence_Tasks"), use_container_width=True)
