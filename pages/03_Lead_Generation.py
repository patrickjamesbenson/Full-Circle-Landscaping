import streamlit as st, pandas as pd
from utils.ui import bootstrap, section
from utils.xldb import read, write, next_id

bootstrap(); section("Lead Generation & ROI","Track channels + monthly performance")
channels = read("Channels")
with st.expander("Channels", expanded=False):
    with st.form("add_channel"):
        cname = st.text_input("Channel name"); owner = st.text_input("Owner", value="Tony"); notes = st.text_input("Notes", value="")
        if st.form_submit_button("Add channel") and cname:
            df = channels.copy(); nid = next_id(df)
            df = pd.concat([df, pd.DataFrame([{"id":nid,"name":cname,"owner":owner,"notes":notes}])], ignore_index=True)
            write("Channels", df); channels = df; st.success("Added.")
    st.dataframe(channels, use_container_width=True)

stats = read("LeadGen_Metrics")
with st.expander("Monthly metrics", expanded=False):
    if not channels.empty:
        ch = st.selectbox("Channel", options=channels["name"].tolist()); month = st.text_input("Month (YYYY-MM)")
        col1,col2,col3,col4 = st.columns(4)
        with col1: cost = st.number_input("Cost", 0.0, 100000.0, 0.0)
        with col2: leads = st.number_input("Leads", 0, 9999, 0)
        with col3: quotes = st.number_input("Quotes", 0, 9999, 0)
        with col4: jobs = st.number_input("Jobs", 0, 9999, 0)
        revenue = st.number_input("Revenue", 0.0, 1000000.0, 0.0)
        if st.button("Add metrics") and month:
            ch_id = int(channels.loc[channels["name"]==ch,"id"].iloc[0])
            df = stats.copy(); nid = next_id(df)
            df = pd.concat([df, pd.DataFrame([{"id":nid,"channel_id":ch_id,"month":month,"cost":cost,"leads":leads,"quotes":quotes,"jobs":jobs,"revenue":revenue}])], ignore_index=True)
            write("LeadGen_Metrics", df); stats = df; st.success("Added.")
    st.dataframe(stats, use_container_width=True)
