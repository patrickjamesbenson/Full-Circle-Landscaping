import streamlit as st, pandas as pd
from datetime import date, timedelta
from utils.ui import bootstrap, section

conn = bootstrap()
section("Scheduling", "Assign jobs, dates, and crew; keep 1–2 weeks ahead")

st.subheader("Next 7 Days — Calendar")
start = date.today(); end = start + timedelta(days=6)
dfw = pd.read_sql_query("""
SELECT j.id, j.scheduled_date, j.start_time, j.end_time, j.crew, j.status,
       c.first_name || ' ' || c.last_name as customer
FROM jobs j
LEFT JOIN quotes q ON j.quote_id=q.id
LEFT JOIN leads l ON q.lead_id=l.id
LEFT JOIN contacts c ON l.contact_id=c.id
WHERE date(j.scheduled_date) BETWEEN ? AND ?
ORDER BY date(j.scheduled_date), time(j.start_time)
""", conn, params=(start.isoformat(), end.isoformat()))
cols = st.columns(7)
for i in range(7):
    d = start + timedelta(days=i)
    with cols[i]:
        st.markdown(f"**{d.strftime('%a %d %b')}**")
        dd = dfw[dfw["scheduled_date"] == d.isoformat()]
        if dd.empty: st.caption("—")
        else:
            for _, r in dd.iterrows():
                st.write(f"#{int(r['id'])} {r['start_time']}-{r['end_time']} — {r['customer']}")

with st.expander("Jobs (all)", expanded=False):
    df = pd.read_sql_query("""
    SELECT j.id, j.scheduled_date, j.start_time, j.end_time, j.crew, j.status, q.id as quote_id,
           c.first_name || ' ' || c.last_name as customer
    FROM jobs j
    LEFT JOIN quotes q ON j.quote_id=q.id
    LEFT JOIN leads l ON q.lead_id=l.id
    LEFT JOIN contacts c ON l.contact_id=c.id
    ORDER BY COALESCE(j.scheduled_date, '9999-12-31') ASC, j.start_time ASC
    """, conn)
    st.dataframe(df, width='stretch', height=300)

st.subheader("Update / Assign Job")
jid = st.number_input("Job ID", min_value=1, step=1)
col1, col2, col3 = st.columns(3)
with col1: d = st.date_input("Date", value=date.today())
with col2: start_t = st.text_input("Start (HH:MM)", value="08:00")
with col3: end_t = st.text_input("End (HH:MM)", value="11:00")
crew = st.text_input("Crew (semicolon-separated)", value="Tony;Sam")
status = st.selectbox("Status", ["Scheduled","In Progress","Done","Invoiced"], index=0)
if st.button("Save scheduling"):
    conn.execute("""UPDATE jobs SET scheduled_date=?, start_time=?, end_time=?, crew=?, status=? WHERE id=?""",
                 (d.isoformat(), start_t, end_t, crew, status, jid))
    conn.commit()
    st.success("Job updated.")
