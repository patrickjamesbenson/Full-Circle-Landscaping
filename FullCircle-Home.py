# C:\Users\Patrick\Desktop\FullCircle_ControlCentre2\FullCircle-Home.py
import streamlit as st, pandas as pd
from datetime import date, timedelta
from utils.ui import bootstrap, brand_hero_home
from utils.xldb import read

st.set_page_config(page_title="Home", layout="wide")
bootstrap(home=True); brand_hero_home()

invoices = read("Invoices")
jobs = read("Jobs")
quotes = read("Quotes")

def _sum(df: pd.DataFrame, mask) -> float:
    """Why: guard against missing/invalid totals when summing."""
    try:
        return float(df.loc[mask, "total"].fillna(0).astype(float).sum())
    except Exception:
        return 0.0

# --- Revenue tiles ---
pd_paid = pd.to_datetime(invoices.get("paid_date"), errors="coerce")
rev_30 = _sum(invoices, (invoices.get("status") == "Paid") & pd_paid.notna() &
              (pd_paid >= pd.Timestamp.today() - pd.Timedelta(days=30)))
rev_open = _sum(invoices, (invoices.get("status") == "Unpaid"))

# --- Week window ---
today = date.today()
monday = today - timedelta(days=today.weekday())
sunday = monday + timedelta(days=6)

# --- Jobs done (this week) robustly ---
if jobs.empty:
    jobs_done = 0
else:
    sd = pd.to_datetime(jobs["scheduled_date"], errors="coerce")  # datetime64
    mask = (
        (jobs["status"] == "Done")
        & sd.notna()
        & (sd.dt.date >= monday)
        & (sd.dt.date <= sunday)
    )
    jobs_done = int(mask.sum())

# --- Quotes in play ---
q_sent = int(quotes.get("status").isin(["Sent", "Accepted"]).sum()) if not quotes.empty else 0

# --- KPIs ---
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Paid revenue (30d)", f"${rev_30:,.0f}")
with c2: st.metric("Outstanding (AR)", f"${rev_open:,.0f}")
with c3: st.metric("Jobs done (this week)", f"{jobs_done}")
with c4: st.metric("Quotes in play", f"{q_sent}")

st.divider()
st.subheader("This Week — Calendar")

week = [monday + timedelta(days=i) for i in range(7)]
cal = jobs.copy()

# Ensure column exists/typed
if "scheduled_date" not in cal.columns:
    cal["scheduled_date"] = None

cal_dt = pd.to_datetime(cal["scheduled_date"], errors="coerce").dt.date
within_week = cal_dt.notna() & (cal_dt >= monday) & (cal_dt <= sunday)
cal = cal.loc[within_week].assign(scheduled_date=cal_dt.loc[within_week])

cols = st.columns(7)
for i, d in enumerate(week):
    with cols[i]:
        st.markdown(f"**{d.strftime('%a %d %b')}**")
        dd = cal[cal["scheduled_date"] == d]
        if dd.empty:
            st.caption("—")
        else:
            for _, r in dd.iterrows():
                st.write(f"#{int(r['id'])} {r.get('start_time')}-{r.get('end_time')} — Crew: {r.get('crew')}")
