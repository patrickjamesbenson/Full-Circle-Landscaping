import streamlit as st
from utils.ui import bootstrap, section
from utils.db import get_conn

st.set_page_config(page_title="Tony's Landscaping Ops", layout="wide")
conn = bootstrap()

section("Tony's Landscaping — Control Centre", "Quick links and KPIs")

col1, col2, col3, col4 = st.columns(4)
with col1:
    total_rev = conn.execute("SELECT ROUND(SUM(total),2) as r FROM invoices WHERE status='Paid'").fetchone()["r"] or 0
    st.metric("Paid revenue (last 6+ months)", f"${total_rev:,.2f}")
with col2:
    owed = conn.execute("SELECT ROUND(SUM(total),2) as r FROM invoices WHERE status!='Paid'").fetchone()["r"] or 0
    st.metric("Outstanding (AR)", f"${owed:,.2f}")
with col3:
    leads = conn.execute("SELECT COUNT(*) as c FROM leads").fetchone()["c"]
    st.metric("Leads (total)", leads)
with col4:
    jobs_next = conn.execute("SELECT COUNT(*) as c FROM jobs WHERE status='Scheduled'").fetchone()["c"]
    st.metric("Scheduled jobs", jobs_next)

st.divider()
st.write("Use the sidebar **Pages** to navigate each part of the workflow.")
