import streamlit as st, pandas as pd
from utils.ui import bootstrap, section

conn = bootstrap()
section("Cadence — Daily / Weekly / Monthly", "Schedule your internal routines")

with st.form("add_task"):
    name = st.text_input("Task name")
    freq = st.selectbox("Frequency", ["daily","weekly","monthly"])
    col1, col2, col3, col4 = st.columns(4)
    with col1: dow = st.number_input("Day of week (0=Mon)", 0, 6, 0) if freq=="weekly" else None
    with col2: dom = st.number_input("Day of month (1-28)", 1, 28, 1) if freq=="monthly" else None
    with col3: hour = st.number_input("Hour (0-23)", 0, 23, 9)
    with col4: minute = st.number_input("Minute (0-59)", 0, 59, 0)
    owner = st.text_input("Owner", value="Tony")
    notes = st.text_input("Notes", value="")
    if st.form_submit_button("Add task") and name:
        conn.execute("""INSERT INTO cadence_tasks(name, frequency, day_of_week, day_of_month, hour, minute, owner, active, notes)
                        VALUES (?,?,?,?,?,?,?,?,?)""", (name, freq, dow if freq=="weekly" else None, dom if freq=="monthly" else None, hour, minute, owner, 1, notes))
        conn.commit()
        st.success("Task added.")

with st.expander("Cadence tasks", expanded=False):
    df = pd.read_sql_query("SELECT id, name, frequency, day_of_week, day_of_month, hour, minute, owner, active FROM cadence_tasks", conn)
    st.dataframe(df, width='stretch')

st.subheader("Mark as Done")
tid = st.number_input("Task ID", 1, step=1)
if st.button("Done today"):
    conn.execute("INSERT INTO cadence_log(task_id, done_date, done) VALUES (?, date('now'), 1)", (tid,))
    conn.commit()
    st.success("Done logged.")
