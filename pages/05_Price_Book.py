import streamlit as st, pandas as pd
from utils.ui import bootstrap, section
from utils.xldb import read, write, next_id

bootstrap(); section("Price Book","Rates used by quoting")
df = read("Price_Book")
with st.form("pb"):
    name = st.text_input("Item name"); cat = st.text_input("Category", value="General")
    unit = st.selectbox("Unit", ["hour","m2","m3","unit"]); rate = st.number_input("Unit rate", 0.0, 100000.0, 100.0)
    notes = st.text_input("Notes", value="")
    if st.form_submit_button("Add item") and name:
        nid = next_id(df); row = {"id":nid,"name":name,"category":cat,"unit":unit,"unit_rate":rate,"notes":notes}
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True); write("Price_Book", df); st.success("Added.")
with st.expander("Price book table", expanded=False):
    st.dataframe(read("Price_Book"), use_container_width=True)
