import streamlit as st
from utils.ui import bootstrap, section
from utils.db import get_conn

conn = bootstrap()
section("Vision & Business Settings", "Define the future state and key settings")

st.subheader("Vision")
vision = st.text_area("Company Vision (1–2 paragraphs)", value="To be the most trusted, tidy, and on-time landscaping team in our area—focused on repeat customers who value clear communication and quality results.", height=150)
if st.button("Save vision"):
    conn.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?,?)", ("vision", vision))
    conn.commit()
    st.success("Saved.")

st.subheader("Basic Settings")
col1, col2 = st.columns(2)
with col1:
    company = st.text_input("Company name", value= (conn.execute("SELECT value FROM settings WHERE key='company_name'").fetchone() or {"value": "Tony's Landscapes"})["value"])
    owner = st.text_input("Owner name", value= (conn.execute("SELECT value FROM settings WHERE key='owner_name'").fetchone() or {"value": "Tony"})["value"])
with col2:
    radius = st.number_input("Service radius (km)", 1, 100, 20)
    target_suburbs = st.text_input("Target suburbs (comma-separated)", value="Hamilton, Mayfield, New Lambton, Kotara, Merewether")

if st.button("Save settings"):
    conn.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?,?)", ("company_name", company))
    conn.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?,?)", ("owner_name", owner))
    conn.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?,?)", ("service_radius_km", str(radius)))
    conn.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?,?)", ("target_suburbs", target_suburbs))
    conn.commit()
    st.success("Settings saved.")
