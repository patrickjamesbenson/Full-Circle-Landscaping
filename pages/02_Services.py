import streamlit as st, pandas as pd
from utils.ui import bootstrap, section
from utils.xldb import read, write, next_id

bootstrap(); section("Services","Seasonal & ongoing")
df = read("Services")
with st.form("svc"):
    name = st.text_input("Service name"); desc = st.text_area("Description", height=80)
    season = st.selectbox("Season", ["summer","winter","all"], index=2); ongoing = st.checkbox("Ongoing (maintenance)")
    if st.form_submit_button("Add service") and name:
        nid = next_id(df); row = {"id":nid,"name":name,"description":desc,"season":season,"is_ongoing":1 if ongoing else 0}
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True); write("Services", df); st.success("Added.")
with st.expander("Services table", expanded=False):
    st.dataframe(df.assign(is_ongoing=df["is_ongoing"].map({0:"No",1:"Yes"})), use_container_width=True)
