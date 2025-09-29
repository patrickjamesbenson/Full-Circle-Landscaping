import streamlit as st, pandas as pd
from utils.ui import bootstrap, section
from utils.xldb import read, write, next_id

bootstrap(); section("Business Essentials","Insurance, regos, subscriptions — costs & due dates")

with st.expander("Add essential", expanded=False):
    df = read("Essentials"); col1,col2,col3 = st.columns(3)
    with col1: name = st.text_input("Name")
    with col2: provider = st.text_input("Provider")
    with col3: cost = st.number_input("Cost", 0.0, 100000.0, 0.0)
    col4,col5 = st.columns(2)
    with col4: cycle = st.selectbox("Billing cycle", ["monthly","quarterly","yearly"])
    with col5: due = st.date_input("Next due date")
    notes = st.text_input("Notes", value="")
    if st.button("Add essential") and name:
        nid = next_id(df); row = {"id":nid,"name":name,"provider":provider,"cost":cost,"billing_cycle":cycle,"next_due":due.isoformat(),"notes":notes}
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True); write("Essentials", df); st.success("Added.")
with st.expander("Essentials table", expanded=False):
    st.dataframe(read("Essentials"), use_container_width=True)
with st.expander("Upcoming (next 60 days)", expanded=False):
    df = read("Essentials").copy()
    df["next_due"] = pd.to_datetime(df["next_due"], errors="coerce")
    cutoff = pd.Timestamp.today()+pd.Timedelta(days=60)
    st.dataframe(df[df["next_due"].notna() & (df["next_due"]<=cutoff)].sort_values("next_due"), use_container_width=True)

