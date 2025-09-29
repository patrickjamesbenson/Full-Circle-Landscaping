import streamlit as st, pandas as pd, os
from datetime import date, timedelta, datetime
from utils.ui import bootstrap, section
from utils.xldb import read, write, next_id
import streamlit.components.v1 as components

APP_ROOT = os.path.dirname(os.path.dirname(__file__))
UP = os.path.join(APP_ROOT,"assets","uploads"); REF = os.path.join(APP_ROOT,"assets","referrals"); INV = os.path.join(APP_ROOT,"assets","invoices")
os.makedirs(UP, exist_ok=True); os.makedirs(REF, exist_ok=True); os.makedirs(INV, exist_ok=True)

bootstrap(); section("Job Completion → Invoicing → Referrals","Close the loop")

with st.expander("Mark job done & upload photos", expanded=False):
    jobs = read("Jobs"); jid = st.number_input("Job ID", min_value=1, step=1); photos = st.file_uploader("Photos", accept_multiple_files=True, type=["png","jpg","jpeg"])
    if st.button("Save job photos + Done"):
        jobs.loc[jobs["id"]==jid,"status"]="Done"; write("Jobs", jobs)
        for ph in photos or []:
            with open(os.path.join(UP, f"job{jid}_{ph.name}"), "wb") as f: f.write(ph.getbuffer())
        st.success("Saved.")

with st.expander("Create invoice", expanded=False):
    invoices = read("Invoices"); jid2 = st.number_input("Job ID to invoice", min_value=1, step=1, key="invjid")
    issue = st.date_input("Issue date", value=date.today()); due = st.date_input("Due date", value=date.today()+timedelta(days=7))
    total = st.number_input("Invoice total", 0.0, 1000000.0, 350.0)
    if st.button("Create invoice"):
        invid = next_id(invoices)
        row = {"id":invid,"job_id":jid2,"issue_date":issue.isoformat(),"due_date":due.isoformat(),"total":total,"status":"Unpaid","paid_date":None,"paid_method":None}
        invoices = pd.concat([invoices, pd.DataFrame([row])], ignore_index=True); write("Invoices", invoices)
        html = f"""<!doctype html><html><head><meta charset='utf-8'><title>Invoice {invid}</title></head>
<body style="font-family:Georgia,serif;background:#F8F5EE;color:#34382F;padding:24px;">
<h2>Invoice #{invid}</h2><p><strong>Job:</strong> {jid2}</p><p><strong>Issue:</strong> {issue} &nbsp;&nbsp; <strong>Due:</strong> {due}</p><h3>Total: ${total:,.2f}</h3></body></html>"""
        pth = os.path.join(INV, f"invoice_{invid}.html"); open(pth,"w",encoding="utf-8").write(html); st.success(f"Invoice {invid} created.")

with st.expander("Mark invoice paid", expanded=False):
    invoices = read("Invoices"); iid = st.number_input("Invoice ID", min_value=1, step=1, key="payiid")
    pdte = st.date_input("Paid date", value=date.today()); pm = st.selectbox("Method", ["Card","Bank Transfer","Cash"])
    if st.button("Mark paid"):
        invoices.loc[invoices["id"]==iid, ["status","paid_date","paid_method"]] = ["Paid", pdte.isoformat(), pm]
        write("Invoices", invoices); st.success("Updated.")

with st.expander("Referrals (save + view)", expanded=False):
    referrals = read("Referrals")
    jid3 = st.number_input("Job ID (for referral)", min_value=1, step=1, key="refjid")
    customer = st.text_input("Customer name"); text = st.text_area("Referral (paste)", height=100); ok = st.checkbox("Permission to publish", value=True)
    if st.button("Save referral"):
        rid = next_id(referrals); fname = f"ref_job{jid3}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"; pth = os.path.join(REF, fname)
        html = f"""<!doctype html><html><head><meta charset='utf-8'><title>Referral - {customer}</title></head>
<body style="font-family:Georgia,serif;background:#F8F5EE;color:#34382F;padding:24px;">
<h2>Customer Referral</h2><p><strong>Customer:</strong> {customer}</p>
<blockquote style="border-left:4px solid #C6723D;margin:0;padding-left:12px;">{text}</blockquote>
<p><small>Saved: {datetime.now().strftime('%d %b %Y %H:%M')}</small></p></body></html>"""
        open(pth,"w",encoding="utf-8").write(html)
        row = {"id":rid,"job_id":jid3,"customer_name":customer,"text":text,"permission":1 if ok else 0,"created_at":datetime.now().isoformat(),"file_path":pth}
        referrals = pd.concat([referrals, pd.DataFrame([row])], ignore_index=True); write("Referrals", referrals); st.success("Referral saved.")
    files = sorted([f for f in os.listdir(REF) if f.endswith(".html")])
    if files:
        pick = st.selectbox("View referral", files)
        with open(os.path.join(REF,pick),"r",encoding="utf-8") as f:
            components.html(f.read(), height=320, scrolling=True)
