# ================================================================
# FILE: pages/08_Job_Completion_Invoicing_Referrals.py  (UPDATED)
# ================================================================
import os
import sys
import subprocess
from datetime import date, timedelta, datetime
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from utils.ui import bootstrap, section, configure_page, footer
from utils.xldb import read, write, next_id
configure_page("Job Done → Invoice → Refer", home=False)

APP_ROOT = os.path.dirname(os.path.dirname(__file__))
UPLOADS = os.path.join(APP_ROOT, "assets", "uploads")           # legacy (kept)
REF = os.path.join(APP_ROOT, "assets", "referrals")
INV = os.path.join(APP_ROOT, "assets", "invoices")
BEFORE = os.path.join(APP_ROOT, "assets", "quote_photos")       # by quote
AFTER = os.path.join(APP_ROOT, "assets", "after_photos")        # by job

os.makedirs(UPLOADS, exist_ok=True)
os.makedirs(REF, exist_ok=True)
os.makedirs(INV, exist_ok=True)
os.makedirs(BEFORE, exist_ok=True)
os.makedirs(AFTER, exist_ok=True)

bootstrap()
section("Job Done → Invoice → Refer", "Close the loop")

def open_folder(path: str) -> bool:
    """Why: convenience access to photo folders."""
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

# --- AFTER photos + mark done ---
with st.expander("Mark job done & upload AFTER photos", expanded=False):
    jobs = read("Jobs")
    jid = st.number_input("Job ID", min_value=1, step=1)
    photos = st.file_uploader("AFTER photos (attach to this JOB)", accept_multiple_files=True, type=["png","jpg","jpeg"])
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Save AFTER photos"):
            saved = 0
            for ph in photos or []:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe = ph.name.replace(" ", "_")
                with open(os.path.join(AFTER, f"job{jid}_{ts}_{safe}"), "wb") as f:
                    f.write(ph.getbuffer())
                saved += 1
            st.success(f"Saved {saved} AFTER photo(s).")
    with c2:
        if st.button("Mark job Done"):
            jobs.loc[jobs["id"] == jid, "status"] = "Done"
            write("Jobs", jobs)
            st.success("Job marked as Done.")
    if st.button("Open AFTER photos folder"):
        if open_folder(AFTER):
            st.toast("Opened AFTER photos folder")

    # list existing AFTER
    if os.path.isdir(AFTER):
        existing = sorted([p for p in os.listdir(AFTER) if p.startswith(f"job{jid}_")])
        if existing:
            st.caption("Existing AFTER photos for this job:")
            cols = st.columns(6)
            for i, p in enumerate(existing[:24]):
                with cols[i % 6]:
                    st.image(os.path.join(AFTER, p), caption=p, use_column_width=True)

# --- Create invoice ---
with st.expander("Create invoice", expanded=False):
    invoices = read("Invoices")
    jid2 = st.number_input("Job ID to invoice", min_value=1, step=1, key="invjid")
    issue = st.date_input("Issue date", value=date.today())
    due = st.date_input("Due date", value=date.today() + timedelta(days=7))
    total = st.number_input("Invoice total", 0.0, 1000000.0, 350.0)
    if st.button("Create invoice"):
        invid = next_id(invoices)
        row = {
            "id": invid, "job_id": jid2, "issue_date": issue.isoformat(),
            "due_date": due.isoformat(), "total": total, "status": "Unpaid",
            "paid_date": None, "paid_method": None
        }
        invoices = pd.concat([invoices, pd.DataFrame([row])], ignore_index=True)
        write("Invoices", invoices)
        html = f"""<!doctype html><html><head><meta charset='utf-8'><title>Invoice {invid}</title></head>
<body style="font-family:Georgia,serif;background:#F8F5EE;color:#34382F;padding:24px;">
<h2>Invoice #{invid}</h2><p><strong>Job:</strong> {jid2}</p><p><strong>Issue:</strong> {issue} &nbsp;&nbsp; <strong>Due:</strong> {due}</p><h3>Total: ${total:,.2f}</h3></body></html>"""
        pth = os.path.join(INV, f"invoice_{invid}.html")
        open(pth, "w", encoding="utf-8").write(html)
        st.success(f"Invoice {invid} created.")

# --- Mark invoice paid ---
with st.expander("Mark invoice paid", expanded=False):
    invoices = read("Invoices")
    iid = st.number_input("Invoice ID", min_value=1, step=1, key="payiid")
    pdte = st.date_input("Paid date", value=date.today())
    pm = st.selectbox("Method", ["Card", "Bank Transfer", "Cash"])
    if st.button("Mark paid"):
        invoices.loc[invoices["id"] == iid, ["status", "paid_date", "paid_method"]] = ["Paid", pdte.isoformat(), pm]
        write("Invoices", invoices)
        st.success("Updated.")

# --- Referrals (unchanged) ---
with st.expander("Referrals (save + view)", expanded=False):
    referrals = read("Referrals")
    jid3 = st.number_input("Job ID (for referral)", min_value=1, step=1, key="refjid")
    customer = st.text_input("Customer name")
    text = st.text_area("Referral (paste)", height=100)
    ok = st.checkbox("Permission to publish", value=True)
    if st.button("Save referral"):
        rid = next_id(referrals)
        fname = f"ref_job{jid3}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        pth = os.path.join(REF, fname)
        html = f"""<!doctype html><html><head><meta charset='utf-8'><title>Referral - {customer}</title></head>
<body style="font-family:Georgia,serif;background:#F8F5EE;color:#34382F;padding:24px;">
<h2>Customer Referral</h2><p><strong>Customer:</strong> {customer}</p>
<blockquote style="border-left:4px solid #C6723D;margin:0;padding-left:12px;">{text}</blockquote>
<p><small>Saved: {datetime.now().strftime('%d %b %Y %H:%M')}</small></p></body></html>"""
        open(pth, "w", encoding="utf-8").write(html)
        row = {
            "id": rid, "job_id": jid3, "customer_name": customer, "text": text,
            "permission": 1 if ok else 0, "created_at": datetime.now().isoformat(), "file_path": pth
        }
        referrals = pd.concat([referrals, pd.DataFrame([row])], ignore_index=True)
        write("Referrals", referrals)
        st.success("Referral saved.")
    files = sorted([f for f in os.listdir(REF) if f.endswith(".html")])
    if files:
        pick = st.selectbox("View referral", files)
        with open(os.path.join(REF, pick), "r", encoding="utf-8") as f:
            components.html(f.read(), height=320, scrolling=True)

# --- BEFORE vs AFTER side-by-side ---
with st.expander("Compare BEFORE vs AFTER", expanded=True):
    jobs = read("Jobs")
    quotes = read("Quotes")
    leads = read("Leads")
    st.caption("Pick a Job ID to view its BEFORE (by Quote) against AFTER (by Job).")
    cmp_jid = st.number_input("Job ID", min_value=1, step=1, key="cmpjid")

    # Map job -> quote -> before files
    row = jobs[jobs["id"].astype(int) == int(cmp_jid)]
    if not row.empty:
        qid = int(row["quote_id"].iloc[0]) if pd.notna(row["quote_id"].iloc[0]) else None
        if qid:
            before_files = sorted([p for p in os.listdir(BEFORE) if p.startswith(f"quote{qid}_")])
        else:
            before_files = []
        after_files = sorted([p for p in os.listdir(AFTER) if p.startswith(f"job{cmp_jid}_")])

        cbtn1, cbtn2 = st.columns([1, 1])
        with cbtn1:
            if st.button("Open BEFORE folder"):
                open_folder(BEFORE)
        with cbtn2:
            if st.button("Open AFTER folder"):
                open_folder(AFTER)

        cols = st.columns(2)
        with cols[0]:
            st.write(f"**BEFORE (Quote {qid if qid else '—'})** — {len(before_files)} file(s)")
            if before_files:
                grid = st.columns(3)
                for i, p in enumerate(before_files[:30]):
                    with grid[i % 3]:
                        st.image(os.path.join(BEFORE, p), use_column_width=True)
            else:
                st.caption("No BEFORE photos found.")
        with cols[1]:
            st.write(f"**AFTER (Job {cmp_jid})** — {len(after_files)} file(s)")
            if after_files:
                grid = st.columns(3)
                for i, p in enumerate(after_files[:30]):
                    with grid[i % 3]:
                        st.image(os.path.join(AFTER, p), use_column_width=True)
            else:
                st.caption("No AFTER photos found. Upload above.")
    else:
        st.info("Enter an existing Job ID.")

footer()
