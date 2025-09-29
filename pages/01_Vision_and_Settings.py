import streamlit as st, pandas as pd
from utils.ui import bootstrap, section
from utils.xldb import read, write, get_setting, set_setting

bootstrap()
section("Vision & Settings", "Define the future state and defaults")

with st.expander("Vision", expanded=False):
    s = read("Settings"); current = s.loc[s["key"]=="vision","value"]
    vision = st.text_area("Company Vision", value=(current.iloc[0] if not current.empty else "Be the most trusted, tidy, on-time landscaping team."), height=150)
    if st.button("Save vision"):
        set_setting("vision", vision); st.success("Saved.")

with st.expander("Business Settings", expanded=False):
    company = get_setting("company_name","Full Circle Gardens")
    owner = get_setting("owner_name","Tony")
    gm = float(get_setting("gm_target","0.40"))
    col1,col2 = st.columns(2)
    with col1:
        company = st.text_input("Company Name", value=company)
        gm_in = st.number_input("Target Gross Margin (0–1)", 0.0, 0.95, gm, step=0.01)
    with col2:
        owner = st.text_input("Owner Name", value=owner)
        radius = st.number_input("Service radius (km)", 1, 100, int(get_setting("service_radius_km","20")))
    if st.button("Save settings"):
        set_setting("company_name", company); set_setting("owner_name", owner)
        set_setting("gm_target", str(gm_in)); set_setting("service_radius_km", str(radius))
        st.success("Saved.")

with st.expander("Settings table (read-only)", expanded=False):
    st.dataframe(read("Settings"), use_container_width=True)
