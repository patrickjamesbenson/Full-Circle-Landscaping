import streamlit as st, pandas as pd
from utils.ui import bootstrap, section
from utils.xldb import read, write, next_id

bootstrap(); section("Roles & Responsibilities","Populate org + costs (used in What-If)")

with st.expander("Add role", expanded=False):
    r = read("Roles")
    with st.form("rform"):
        name = st.text_input("Role name"); desc = st.text_area("Description", height=80)
        resp = st.text_area("Responsibilities (one per line)", height=120)
        if st.form_submit_button("Add role") and name:
            nid = next_id(r); row = {"id":nid,"role_name":name,"description":desc,"responsibilities":resp}
            r = pd.concat([r, pd.DataFrame([row])], ignore_index=True); write("Roles", r); st.success("Added.")

with st.expander("Role costs (monthly)", expanded=False):
    rc = read("Role_Costs"); r = read("Roles")
    if not r.empty:
        ropt = r["id"].astype(int).astype(str) + " — " + r["role_name"]; sel = st.selectbox("Role", ropt)
        rid = int(sel.split("—")[0].strip()); cost = st.number_input("Monthly cost", 0.0, 20000.0, 5500.0)
        if st.button("Save cost"):
            if (rc["role_id"]==rid).any(): rc.loc[rc["role_id"]==rid,"monthly_cost"]=cost
            else: rc = pd.concat([rc, pd.DataFrame([{"id":next_id(rc),"role_id":rid,"monthly_cost":cost}])], ignore_index=True)
            write("Role_Costs", rc); st.success("Saved.")
    st.dataframe(read("Role_Costs"), use_container_width=True)

