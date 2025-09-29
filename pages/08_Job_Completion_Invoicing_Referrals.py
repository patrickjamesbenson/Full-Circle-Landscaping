import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta, datetime
from utils.ui import bootstrap, section

ROOT = os.path.dirname(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(ROOT, "assets", "uploads")
REF_DIR = os.path.join(ROOT, "assets", "referrals")

conn = bootstrap()
section("Job Completion → Invoicing → Referrals", "Close the loop on each job")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REF_DIR, exist_ok=True)

st.subheader("Mark Job Done & Upload Photos")
jid = st.number_input("Job ID", min_value=1, step=1)
photos = st.file_uploader("Upload photos", type=["png","jpg","jpeg"], accept_multiple_files=True)
if st.button("Mark Done & Save Photos"):
    conn.execute("UPDATE jobs SET status='Done' WHERE id=?", (jid,))
    for ph in photos or []:
        save_path = os.path.join(UPLOAD_DIR, f"job{jid}_{ph.name}")
        with open(save_path, "wb") as f:
            f.write(ph.getbuffer())
        conn.execute("INSERT INTO job_photos(job_id, file_path) VALUES (?,?)", (jid, save_path))
    conn.commit()
    st.success("Job marked done and photos saved.")

st.subheader("Create Invoice")
issue = st.date_input("Issue date", value=date.today())
due = st.date_input("Due date", value=date.today()+timedelta(days=7))
total = st.number_input("Invoice total", 0.0, 1000000.0, 350.0)
if st.button("Create Invoice"):
    conn.execute("""INSERT INTO invoices(job_id, issue_date, due_date, total, status) VALUES (?,?,?,?,?)""",
                 (jid, issue.isoformat(), due.isoformat(), total, "Unpaid"))
    conn.commit()
    st.success("Invoice created.")

st.subheader("Record Payment")
inv_id = st.number_input("Invoice ID", min_value=1, step=1)
paid_date = st.date_input("Paid date", value=date.today())
method = st.selectbox("Payment method", ["Card","Bank Transfer","Cash"])
if st.button("Mark Paid"):
    conn.execute("UPDATE invoices SET status='Paid', paid_date=?, paid_method=? WHERE id=?", (paid_date.isoformat(), method, inv_id))
    conn.commit()
    st.success("Marked as paid.")

st.subheader("Ask for Referral")
customer = st.text_input("Customer name")
ref_text = st.text_area("Referral text (paste from customer)", height=120)
permission = st.checkbox("Permission to publish", value=True)

def save_referral_html(job_id:int, customer:str, text:str):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"ref_job{job_id}_{ts}.html"
    path = os.path.join(REF_DIR, fname)
    html = f"""<!doctype html>
<html><head><meta charset="utf-8">
<title>Referral - {customer}</title>
<style>
body{{font-family:Georgia,serif;background:#F0EBDD;color:#34382F;padding:24px;}}
blockquote{{font-size:1.2rem;line-height:1.5;border-left:4px solid #C6723D;margin:0;padding-left:16px;}}
small{{color:#6C715F;}}
</style></head>
<body>
<h2>Full Circle Gardens — Customer Referral</h2>
<p><strong>Customer:</strong> {customer}</p>
<blockquote>{text}</blockquote>
<p><small>Saved: {datetime.now().strftime("%d %b %Y %H:%M")}</small></p>
</body></html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path

if st.button("Save Referral"):
    conn.execute("""INSERT INTO referrals(job_id, customer_name, text, permission, created_at) VALUES (?,?,?,?,datetime('now'))""",
                 (jid, customer, ref_text, 1 if permission else 0))
    conn.commit()
    p = save_referral_html(jid, customer, ref_text)
    st.success(f"Referral saved. HTML: {os.path.basename(p)}")

st.subheader("Referral Repository")
files = sorted([f for f in os.listdir(REF_DIR) if f.endswith(".html")])
if files:
    for f in files:
        st.markdown(f"- {f}")
else:
    st.caption("No referral files yet.")
