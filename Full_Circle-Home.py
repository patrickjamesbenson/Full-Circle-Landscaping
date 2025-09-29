import streamlit as st
from datetime import timedelta, date
import pandas as pd
from utils.ui import bootstrap, brand_hero

st.set_page_config(page_title="Home", layout="wide")
conn = bootstrap()

brand_hero()

col1, col2, col3, col4 = st.columns(4)
with col1:
    total_rev = conn.execute("SELECT ROUND(SUM(total),2) as r FROM invoices WHERE status='Paid'").fetchone()["r"] or 0
    st.metric("Paid revenue (since start)", f"${total_rev:,.2f}")
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

def week_bounds(d: date):
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday

today = date.today()
this_mon, this_sun = week_bounds(today)
last_mon, last_sun = week_bounds(today - timedelta(days=7))
next_mon, next_sun = week_bounds(today + timedelta(days=7))

def paid_between(d1, d2):
    r = conn.execute(
        "SELECT SUM(total) as r FROM invoices WHERE status='Paid' AND date(issue_date) BETWEEN ? AND ?",
        (d1.isoformat(), d2.isoformat())
    ).fetchone()["r"]
    return float(r or 0.0)

def expected_between(d1, d2):
    r = conn.execute(
        """
        SELECT COALESCE(SUM(q.total),0) as tot
        FROM jobs j
        JOIN quotes q ON q.id=j.quote_id
        WHERE date(j.scheduled_date) BETWEEN ? AND ?
        """, (d1.isoformat(), d2.isoformat())
    ).fetchone()["tot"]
    inv = conn.execute(
        """
        SELECT COALESCE(SUM(i.total),0) as tot
        FROM invoices i
        JOIN jobs j ON i.job_id=j.id
        WHERE date(j.scheduled_date) BETWEEN ? AND ?
        """,
        (d1.isoformat(), d2.isoformat())
    ).fetchone()["tot"]
    return float(max(r or 0.0, inv or 0.0))

c1, c2, c3 = st.columns(3)
with c1:
    st.metric(f"Revenue last week ({last_mon:%d %b}–{last_sun:%d %b})", f"${paid_between(last_mon,last_sun):,.0f}")
with c2:
    st.metric(f"Revenue this week ({this_mon:%d %b}–{this_sun:%d %b})", f"${paid_between(this_mon,this_sun):,.0f}")
with c3:
    st.metric(f"Expected next week ({next_mon:%d %b}–{next_sun:%d %b})", f"${expected_between(next_mon,next_sun):,.0f}")

st.subheader("This Week — Calendar")
df = pd.read_sql_query(
    """
    SELECT j.id as job_id, j.scheduled_date, j.start_time, j.end_time, j.crew, j.status,
           l.name as customer, l.suburb
    FROM jobs j
    LEFT JOIN quotes q ON j.quote_id=q.id
    LEFT JOIN leads l ON q.lead_id=l.id
    WHERE date(j.scheduled_date) BETWEEN ? AND ?
    ORDER BY date(j.scheduled_date), time(j.start_time)
    """,
    conn, params=(this_mon.isoformat(), this_sun.isoformat())
)
days = [this_mon + timedelta(days=i) for i in range(7)]
cols = st.columns(7)
for i, d in enumerate(days):
    with cols[i]:
        st.markdown(f"**{d.strftime('%a %d %b')}**")
        day_df = df[df["scheduled_date"] == d.isoformat()]
        if day_df.empty:
            st.caption("—")
        else:
            for _, r in day_df.iterrows():
                st.write(f"#{int(r['job_id'])} {r['start_time']}-{r['end_time']} — {r['customer']} ({r['suburb']})")
