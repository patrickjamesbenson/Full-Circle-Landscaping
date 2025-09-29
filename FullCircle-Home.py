# =========================
# FILE: FullCircle-Home.py
# =========================
import os
import sys
import subprocess
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.ui import bootstrap, section
from utils.xldb import read

VERSION = "v5.5"  # why: visible app versioning

st.set_page_config(page_title="Home", layout="wide")
bootstrap()  # unified header
section("Home", "Overview & this week")

# Data
invoices = read("Invoices")
jobs = read("Jobs")
quotes = read("Quotes")
leads = read("Leads")
contacts = read("Contacts")

def _sum(df: pd.DataFrame, mask) -> float:
    try:
        return float(df.loc[mask, "total"].fillna(0).astype(float).sum())
    except Exception:
        return 0.0

def open_folder(path: str) -> bool:
    """Why: quick access to BEFORE photos from dashboard."""
    try:
        if os.name == "nt":
            os.startfile(path)  # noqa: SLF001
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception as exc:
        st.error(f"Could not open folder: {exc}")
        return False

# KPIs
pd_paid = pd.to_datetime(invoices.get("paid_date"), errors="coerce")
rev_30 = _sum(invoices, (invoices.get("status") == "Paid") & pd_paid.notna() &
              (pd_paid >= pd.Timestamp.today() - pd.Timedelta(days=30)))
rev_open = _sum(invoices, (invoices.get("status") == "Unpaid"))

today = date.today()
monday = today - timedelta(days=today.weekday())
sunday = monday + timedelta(days=6)

# Jobs done this week
if jobs.empty:
    jobs_done = 0
else:
    sd = pd.to_datetime(jobs["scheduled_date"], errors="coerce")
    mask = (jobs["status"] == "Done") & sd.notna() & (sd.dt.date >= monday) & (sd.dt.date <= sunday)
    jobs_done = int(mask.sum())

q_sent = int(quotes.get("status").isin(["Sent", "Accepted"]).sum()) if not quotes.empty else 0

# Build week join for list view + revenue (scheduled)
j = jobs.copy()
j["scheduled_dt"] = pd.to_datetime(j["scheduled_date"], errors="coerce")
in_week = j["scheduled_dt"].notna() & (j["scheduled_dt"].dt.date >= monday) & (j["scheduled_dt"].dt.date <= sunday)
j = j.loc[in_week].copy()

q = quotes.rename(columns={"id": "quote_id_q"})[["quote_id_q", "lead_id", "total"]]
j = j.merge(q, left_on="quote_id", right_on="quote_id_q", how="left")

l = leads.rename(columns={"id": "lead_id_l"})[["lead_id_l", "contact_id", "service_requested"]]
j = j.merge(l, left_on="lead_id", right_on="lead_id_l", how="left")

c = contacts.rename(columns={"id": "contact_id_c"})[["contact_id_c", "first_name", "last_name", "suburb"]]
j = j.merge(c, left_on="contact_id", right_on="contact_id_c", how="left")

rev_sched_week = float(j.get("total", pd.Series(dtype=float)).fillna(0).astype(float).sum())

# KPIs row
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.metric("Paid revenue (30d)", f"${rev_30:,.0f}")
with c2: st.metric("Outstanding (AR)", f"${rev_open:,.0f}")
with c3: st.metric("Jobs done (this week)", f"{jobs_done}")
with c4: st.metric("Quotes in play", f"{q_sent}")
with c5: st.metric("Scheduled revenue (this week)", f"${rev_sched_week:,.0f}")

st.divider()
st.subheader("This Week — List View")

def _name(row):
    f = str(row.get("first_name") or "").strip()
    l_ = str(row.get("last_name") or "").strip()
    return (f + " " + l_).strip()

display = pd.DataFrame({
    "Date": j["scheduled_dt"].dt.date,
    "Time": (j["start_time"].fillna("") + "–" + j["end_time"].fillna("")).str.strip("–"),
    "Job": j["service_requested"].fillna(""),
    "Suburb": j["suburb"].fillna(""),
    "Crew": j["crew"].fillna(""),
    "Revenue (est.)": j["total"].fillna(0).astype(float).round(2),
    "Status": j["status"].fillna(""),
    "Contact": j.apply(_name, axis=1),
}).sort_values(["Date", "Time"], kind="stable")

st.dataframe(display, use_container_width=True, hide_index=True)

# --- Today's BEFORE photos gallery ---
APP_ROOT = os.path.dirname(__file__)
QUOTE_PHOTOS = os.path.join(APP_ROOT, "assets", "quote_photos")
st.divider()
col_title, col_btn = st.columns([4, 1])
with col_title:
    st.subheader("Today’s BEFORE photos")
with col_btn:
    if st.button("Open BEFORE photos folder"):
        if open_folder(QUOTE_PHOTOS):
            st.toast("Opened BEFORE photos folder")

if os.path.isdir(QUOTE_PHOTOS) and not jobs.empty:
    j_today = jobs.copy()
    j_today["scheduled_dt"] = pd.to_datetime(j_today["scheduled_date"], errors="coerce")
    j_today = j_today.loc[j_today["scheduled_dt"].dt.date == today].copy()
    if not j_today.empty:
        # Join for headers
        q2 = quotes.rename(columns={"id": "quote_id_q"})[["quote_id_q", "lead_id", "total"]]
        j_today = j_today.merge(q2, left_on="quote_id", right_on="quote_id_q", how="left")
        l2 = leads.rename(columns={"id": "lead_id_l"})[["lead_id_l", "contact_id", "service_requested"]]
        j_today = j_today.merge(l2, left_on="lead_id", right_on="lead_id_l", how="left")
        c2 = contacts.rename(columns={"id": "contact_id_c"})[["contact_id_c", "first_name", "last_name", "suburb"]]
        j_today = j_today.merge(c2, left_on="contact_id", right_on="contact_id_c", how="left")

        any_shown = False
        for _, r in j_today.sort_values(["start_time", "end_time"], na_position="last").iterrows():
            qid = r.get("quote_id")
            if pd.isna(qid):
                continue
            qid = int(qid)
            files = [fn for fn in os.listdir(QUOTE_PHOTOS) if fn.startswith(f"quote{qid}_")]
            title = (
                f"#{int(r['id'])} {str(r.get('start_time') or '')}–{str(r.get('end_time') or '')} • "
                f"{r.get('service_requested') or ''} — {r.get('suburb') or ''} • "
                f"Crew: {r.get('crew') or ''} • Est: ${float(r.get('total') or 0):,.0f}"
            )
            st.markdown(f"**{title}**")
            if files:
                any_shown = True
                cols = st.columns(6)
                for i, p in enumerate(sorted(files)[:24]):
                    with cols[i % 6]:
                        st.image(os.path.join(QUOTE_PHOTOS, p), use_column_width=True)
            else:
                st.caption("_No BEFORE photos for this job’s quote._")
        if not any_shown:
            st.caption("No BEFORE photos found for today’s jobs.")
    else:
        st.caption("No jobs scheduled for today.")
else:
    st.caption("Photos folder not found yet. Upload BEFORE photos on the Quoting page to create it.")

# Footer
st.markdown(
    f"<hr style='opacity:.3;margin-top:24px;margin-bottom:8px'>"
    f"<div style='font-size:12px;opacity:.8'>© 2025 LB Lighting • Full Circle Control Centre {VERSION}</div>",
    unsafe_allow_html=True,
)