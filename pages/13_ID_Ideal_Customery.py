import streamlit as st, pandas as pd
from utils.ui import bootstrap, section
from utils.xldb import read

bootstrap(); section("ID Ideal Customer","Lead → Quote → Job → Invoice")

leads = read("Leads"); quotes = read("Quotes"); jobs = read("Jobs"); inv = read("Invoices"); contacts = read("Contacts")

with st.expander("Funnel overview", expanded=False):
    L = len(leads); Q = len(quotes); J = len(jobs); I = len(inv)
    paid = int((inv.get("status")=="Paid").sum())
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.metric("Leads", L)
    with c2: st.metric("Quotes", Q)
    with c3: st.metric("Jobs", J)
    with c4: st.metric("Invoices", I)
    with c5: st.metric("Paid", paid)

with st.expander("Journey by contact", expanded=False):
    if contacts.empty: st.info("No contacts.")
    else:
        opt = contacts["id"].astype(int).astype(str) + " — " + contacts["first_name"] + " " + contacts["last_name"]
        sel = st.selectbox("Contact", opt); cid = int(sel.split("—")[0].strip())
        lds = leads[leads["contact_id"]==cid]
        st.write("**Leads**"); st.dataframe(lds, use_container_width=True)
        qts = quotes[quotes["lead_id"].isin(lds["id"])]; st.write("**Quotes**"); st.dataframe(qts, use_container_width=True)
        jbs = jobs[jobs["quote_id"].isin(qts["id"])]; st.write("**Jobs**"); st.dataframe(jbs, use_container_width=True)
        invs = inv[inv["job_id"].isin(jbs["id"])]; st.write("**Invoices**"); st.dataframe(invs, use_container_width=True)

