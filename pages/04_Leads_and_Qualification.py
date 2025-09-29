import streamlit as st
import pandas as pd
from utils.ui import bootstrap, section

conn = bootstrap()
section("Leads & Qualification (MQL → SQL)", "Capture and triage leads quickly")

channels = [r["name"] for r in conn.execute("SELECT name FROM channels")]
services = [r["name"] for r in conn.execute("SELECT name FROM services")]

with st.form("add_lead"):
    name = st.text_input("Name")
    phone = st.text_input("Phone")
    email = st.text_input("Email")
    suburb = st.text_input("Suburb")
    channel = st.selectbox("Channel", channels)
    service_requested = st.selectbox("Service requested", services)
    tier = st.selectbox("Customer tier", ["Economy","Business","First"])
    budget = st.selectbox("Budget sense", ["Low","OK","Premium"])
    timing = st.selectbox("Timing", ["ASAP","Within 2 weeks","Flexible"])
    notes = st.text_area("Notes", height=80)
    submitted = st.form_submit_button("Add lead")
    if submitted and name:
        row = conn.execute("SELECT id FROM channels WHERE name=?", (channel,)).fetchone()
        conn.execute("""INSERT INTO leads(name, phone, email, suburb, channel_id, service_requested, notes, tier, budget, timing, mql_status, sql_status, status, created_at)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
                     (name, phone, email, suburb, row["id"], service_requested, notes, tier, budget, timing, 1, 0, "New"))
        conn.commit()
        st.success("Lead added.")

st.subheader("Leads")
df = pd.read_sql_query("""
SELECT l.id, l.created_at, l.name, l.phone, l.suburb, s.name as service, c.name as channel,
       l.tier, l.budget, l.timing, l.mql_status, l.sql_status, l.status
FROM leads l
LEFT JOIN channels c ON l.channel_id=c.id
LEFT JOIN services s ON s.name=l.service_requested
ORDER BY datetime(l.created_at) DESC
""", conn)
st.dataframe(df, width='stretch', height=400)

st.subheader("Qualify / Promote to Quote")
lid = st.number_input("Lead ID", 1, None, step=1)
col1, col2, col3 = st.columns(3)
with col1:
    mql = st.selectbox("MQL", [0,1])
with col2:
    sql = st.selectbox("SQL", [0,1])
with col3:
    status = st.selectbox("Status", ["New","Contacted","Qualified","Disqualified"])

notes2 = st.text_area("Update notes (optional)", height=80)
if st.button("Update lead"):
    conn.execute("UPDATE leads SET mql_status=?, sql_status=?, status=?, notes=COALESCE(notes,'') || CHAR(10) || ? WHERE id=?",
                 (mql, sql, status, notes2, lid))
    conn.commit()
    st.success("Lead updated.")

if st.button("Create Quote from Lead"):
    conn.execute("INSERT INTO quotes(lead_id, created_at, status, total, notes) VALUES (?,?,?,0,'')", (lid, __import__("datetime").datetime.now().isoformat(), "Draft"))
    conn.commit()
    st.success("Draft quote created.")
