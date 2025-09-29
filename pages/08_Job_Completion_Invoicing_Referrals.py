import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
from utils.ui import bootstrap, section
from utils.db import get_conn

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "assets", "uploads")

conn = bootstrap()
section("Job Completion → Invoicing → Referrals", "Close the loop on each job")

st.subheader("Mark Job Done & Upload Photos")
jid = st.number_input("Job ID", min_value=1, step=1)
photos = st.file_uploader("Upload photos", type=["png","jpg","jpeg"], accept_multiple_files=True)
if st.button("Mark Done & Save Photos"):
    conn.execute("UPDATE jobs SET status='Done' WHERE id=?", (jid,))
    os.makedirs(UPLOAD_DIR, exist_ok=True)
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
if st.button("Save Referral"):
    conn.execute("""INSERT INTO referrals(job_id, customer_name, text, permission, created_at) VALUES (?,?,?,?,datetime('now'))""",
                 (jid, customer, ref_text, 1 if permission else 0))
    conn.commit()
    st.success("Referral saved.")
