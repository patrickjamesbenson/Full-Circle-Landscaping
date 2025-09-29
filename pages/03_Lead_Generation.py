import streamlit as st
import pandas as pd
from utils.ui import bootstrap, section
from utils.db import get_conn

conn = bootstrap()
section("Lead Generation Plan & ROI", "Track channels, costs, leads, quotes, jobs, and revenue")

st.subheader("Channels")
with st.form("add_channel"):
    cname = st.text_input("Channel name")
    owner = st.text_input("Owner", value="Tony")
    notes = st.text_input("Notes", value="")
    if st.form_submit_button("Add channel") and cname:
        conn.execute("INSERT INTO channels(name, owner, notes) VALUES (?,?,?)", (cname, owner, notes))
        conn.commit()
        st.success("Channel added.")

channels = pd.DataFrame(conn.execute("SELECT * FROM channels").fetchall())
if not channels.empty:
    st.dataframe(channels, use_container_width=True)

st.subheader("Monthly Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    channel = st.selectbox("Channel", channels["name"] if not channels.empty else [])
with col2:
    month = st.text_input("Month (YYYY-MM)")
with col3:
    cost = st.number_input("Cost", 0.0, 100000.0, 0.0)

col4, col5, col6, col7 = st.columns(4)
with col4:
    leads = st.number_input("# Leads", 0, 10000, 0)
with col5:
    quotes = st.number_input("# Quotes", 0, 10000, 0)
with col6:
    jobs = st.number_input("# Jobs", 0, 10000, 0)
with col7:
    revenue = st.number_input("Revenue", 0.0, 1000000.0, 0.0)

if st.button("Add monthly metrics") and channel and month:
    row = conn.execute("SELECT id FROM channels WHERE name=?", (channel,)).fetchone()
    if row:
        conn.execute("""INSERT INTO leadgen_stats(channel_id, month, cost, leads, quotes, jobs, revenue)
                        VALUES (?,?,?,?,?,?,?)""", (row["id"], month, cost, leads, quotes, jobs, revenue))
        conn.commit()
        st.success("Metrics added.")

stats = pd.read_sql_query("""
SELECT c.name as channel, l.month, l.cost, l.leads, l.quotes, l.jobs, l.revenue,
       CASE WHEN l.leads>0 THEN ROUND(1.0*l.cost/l.leads,2) ELSE NULL END as cost_per_lead,
       CASE WHEN l.quotes>0 THEN ROUND(1.0*l.jobs/l.quotes,2) ELSE NULL END as win_rate,
       CASE WHEN l.cost>0 THEN ROUND((l.revenue - l.cost)/l.cost,2) ELSE NULL END as ROI
FROM leadgen_stats l JOIN channels c ON l.channel_id=c.id
ORDER BY l.month DESC, channel
""", conn)
st.dataframe(stats, use_container_width=True)
