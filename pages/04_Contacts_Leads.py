# =================================
# FILE: pages/04_Contacts_Leads.py
# =================================
import streamlit as st, pandas as pd
from utils.ui import bootstrap, section, configure_page, footer
from utils.xldb import read, write, next_id
configure_page("Contacts & Leads", home=False)

bootstrap(); section("Contacts & Leads","Every lead links to a contact")
contacts = read("Contacts"); channels = read("Channels"); services = read("Services")

with st.expander("Add contact", expanded=False):
    with st.form("cform"):
        fn = st.text_input("First name"); ln = st.text_input("Last name")
        phone = st.text_input("Mobile"); email = st.text_input("Email")
        street = st.text_input("Street address"); suburb = st.text_input("Suburb"); pc = st.text_input("Postcode")
        if st.form_submit_button("Save contact") and fn and ln:
            df = contacts.copy(); nid = next_id(df)
            row = {"id":nid,"first_name":fn,"last_name":ln,"phone":phone,"email":email,"street":street,"suburb":suburb,"postcode":pc}
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True); write("Contacts", df); contacts=df; st.success("Saved.")

with st.expander("Add lead (linked to a contact)", expanded=False):
    if contacts.empty or channels.empty or services.empty: st.warning("Need at least one contact, channel, and service.")
    else:
        with st.form("lform"):
            copt = contacts["id"].astype(int).astype(str) + " — " + contacts["first_name"] + " " + contacts["last_name"]
            csel = st.selectbox("Contact", copt); cid = int(csel.split("—")[0].strip())
            ch = st.selectbox("Channel", channels["name"].tolist()); srv = st.selectbox("Service requested", services["name"].tolist())
            tier = st.selectbox("Tier", ["Economy","Business","First"])
            budget = st.selectbox("Budget", ["Low","OK","Premium"]); timing = st.selectbox("Timing", ["ASAP","Within 2 weeks","Flexible"])
            notes = st.text_area("Notes", height=80)
            if st.form_submit_button("Save lead"):
                leads = read("Leads"); nid = next_id(leads); ch_id = int(channels.loc[channels["name"]==ch,"id"].iloc[0])
                row = {"id":nid,"created_at":pd.Timestamp.now().isoformat(),"contact_id":cid,"channel_id":ch_id,"service_requested":srv,
                       "notes":notes,"tier":tier,"budget":budget,"timing":timing,"status":"New","mql":1,"sql":0}
                leads = pd.concat([leads, pd.DataFrame([row])], ignore_index=True); write("Leads", leads); st.success("Lead saved.")

with st.expander("Contacts table", expanded=False):
    st.dataframe(contacts, use_container_width=True)

with st.expander("Leads table (with names)", expanded=True):
    leads_df = read("Leads").copy()
    if leads_df.empty:
        st.info("No leads yet.")
    else:
        # Join names
        c_small = contacts[["id","first_name","last_name"]].rename(columns={"id":"contact_id"})
        ch_small = channels[["id","name"]].rename(columns={"id":"channel_id","name":"channel"})
        m = leads_df.merge(c_small, on="contact_id", how="left").merge(ch_small, on="channel_id", how="left")
        m["contact"] = (m["first_name"].fillna("") + " " + m["last_name"].fillna("")).str.strip()
        disp = m[["id","created_at","contact","channel","service_requested","tier","budget","timing","status","mql","sql","notes"]]
        st.dataframe(disp, use_container_width=True, hide_index=True)

footer()
