import streamlit as st, pandas as pd
from utils.ui import bootstrap, section
from utils.xldb import read, write, next_id

bootstrap(); section("Money In / Money Out","AR, payments, and expenses")

with st.expander("Invoices (AR)", expanded=False):
    st.dataframe(read("Invoices"), use_container_width=True)

with st.expander("Add expense (AP)", expanded=False):
    ap = read("AP_Expenses"); col1,col2,col3,col4 = st.columns(4)
    with col1: d = st.date_input("Date")
    with col2: vendor = st.text_input("Vendor")
    with col3: cat = st.text_input("Category")
    with col4: amt = st.number_input("Amount", 0.0, 1000000.0, 0.0)
    desc = st.text_input("Description", value="")
    if st.button("Add expense"):
        nid = next_id(ap); row = {"id":nid,"date":d.isoformat(),"vendor":vendor,"category":cat,"description":desc,"amount":amt}
        ap = pd.concat([ap, pd.DataFrame([row])], ignore_index=True); write("AP_Expenses", ap); st.success("Added.")

with st.expander("Expenses table", expanded=False):
    st.dataframe(read("AP_Expenses"), use_container_width=True)

with st.expander("Monthly summary", expanded=False):
    inv = read("Invoices").copy(); ap = read("AP_Expenses").copy()
    inv["m"] = pd.to_datetime(inv["issue_date"], errors="coerce").dt.strftime("%Y-%m"); ap["m"] = pd.to_datetime(ap["date"], errors="coerce").dt.strftime("%Y-%m")
    months = sorted(set(inv["m"].dropna().tolist()+ap["m"].dropna().tolist()))
    rows=[]
    for m in months:
        paid = inv[(inv["status"]=="Paid") & (inv["m"]==m)]["total"].fillna(0).sum()
        ar_open = inv[(inv["status"]!="Paid") & (inv["m"]==m)]["total"].fillna(0).sum()
        exp = ap[ap["m"]==m]["amount"].fillna(0).sum()
        rows.append({"month":m,"paid_revenue":paid,"ar_open":ar_open,"expenses":exp,"profit_estimate":paid-exp})
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

