import streamlit as st
from utils.ui import bootstrap, section

conn = bootstrap()
section("Vision & Business Settings", "Define the future state and key settings")

st.subheader("Vision")
vision = st.text_area("Company Vision (1–2 paragraphs)",
    value=(conn.execute("SELECT value FROM settings WHERE key='vision'").fetchone() or {"value":"To be the most trusted, tidy, and on-time landscaping team in our area—focused on repeat customers who value clear communication and quality results."})["value"],
    height=150)
if st.button("Save vision"):
    conn.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?,?)", ("vision", vision))
    conn.commit()
    st.success("Saved.")

st.subheader("Basic Settings")
col1, col2 = st.columns(2)
with col1:
    company = st.text_input("Company name", value=(conn.execute("SELECT value FROM settings WHERE key='company_name'").fetchone() or {"value":"Full Circle Gardens"})["value"])
    owner = st.text_input("Owner name", value=(conn.execute("SELECT value FROM settings WHERE key='owner_name'").fetchone() or {"value":"Tony"})["value"])
with col2:
    radius = st.number_input("Service radius (km)", 1, 100, int(float((conn.execute("SELECT value FROM settings WHERE key='service_radius_km'").fetchone() or {"value":"20"})["value"])))
    target_suburbs = st.text_input("Target suburbs (comma-separated)", value=(conn.execute("SELECT value FROM settings WHERE key='target_suburbs'").fetchone() or {"value":"Hamilton, Mayfield, New Lambton, Kotara, Merewether"})["value"])

st.subheader("Pricing Defaults")
col3, col4 = st.columns(2)
with col3:
    gm_default = float(conn.execute("SELECT value FROM settings WHERE key='default_gm_pct'").fetchone() or {"value":"0.40"})["value"]
    gm_in = st.number_input("Target Gross Margin (0–1)", 0.0, 0.95, gm_default, step=0.01)
with col4:
    mu_default = float(conn.execute("SELECT value FROM settings WHERE key='default_markup_pct'").fetchone() or {"value":"0.67"})["value"]
    mu_in = st.number_input("Markup (on cost) (0–5)", 0.0, 5.0, mu_default, step=0.05)

if st.button("Save settings"):
    conn.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?,?)", ("company_name", company))
    conn.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?,?)", ("owner_name", owner))
    conn.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?,?)", ("service_radius_km", str(radius)))
    conn.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?,?)", ("target_suburbs", target_suburbs))
    conn.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?,?)", ("default_gm_pct", str(gm_in)))
    conn.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?,?)", ("default_markup_pct", str(mu_in)))
    conn.commit()
    st.success("Settings saved.")
