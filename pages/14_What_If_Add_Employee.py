import streamlit as st, math
from utils.ui import bootstrap, section

conn = bootstrap()
section("What If — Add an Employee", "Model added cost + required revenue at target GM")

st.subheader("Employee costs (monthly)")
c1, c2, c3 = st.columns(3)
with c1:
    base_salary_yr = st.number_input("Base salary (per year)", 0.0, 200000.0, 68000.0, step=1000.0)
    super_pct = st.number_input("Superannuation %", 0.0, 50.0, 11.0, step=0.5) / 100.0
with c2:
    leave_loading = st.number_input("Leave/loading (annual $)", 0.0, 20000.0, 2500.0, step=100.0)
    insurances_mo = st.number_input("Insurances (per month)", 0.0, 5000.0, 180.0, step=10.0)
with c3:
    phone_mo = st.number_input("Phone/data (per month)", 0.0, 500.0, 40.0, step=5.0)
    other_mo = st.number_input("Other recurring (per month)", 0.0, 5000.0, 120.0, step=10.0)

salary_mo = base_salary_yr/12.0
on_costs_mo = salary_mo*super_pct + (leave_loading/12.0) + insurances_mo + phone_mo + other_mo

st.subheader("Equipment costs")
c4, c5, c6 = st.columns(3)
with c4:
    van_capex = st.number_input("Van purchase (CAPEX)", 0.0, 120000.0, 30000.0, step=1000.0)
    van_life_mo = st.number_input("Van life (months)", 1, 120, 60)
    mower_capex = st.number_input("Mowers/tools CAPEX", 0.0, 30000.0, 6000.0, step=500.0)
with c5:
    mower_life_mo = st.number_input("Mowers/tools life (months)", 1, 120, 36)
    pressure_capex = st.number_input("Pressure washer CAPEX", 0.0, 15000.0, 2500.0, step=250.0)
    pressure_life_mo = st.number_input("Pressure washer life (months)", 1, 120, 48)
with c6:
    fuel_mo = st.number_input("Fuel (per month)", 0.0, 5000.0, 380.0, step=10.0)
    maintenance_mo = st.number_input("Maintenance (per month)", 0.0, 5000.0, 220.0, step=10.0)

capex_amort_mo = (van_capex/van_life_mo) + (mower_capex/mower_life_mo) + (pressure_capex/pressure_life_mo)
running_mo = fuel_mo + maintenance_mo

st.subheader("Gross Margin target")
gm_default = float((conn.execute("SELECT value FROM settings WHERE key='default_gm_pct'").fetchone() or {"value":"0.40"})["value"])
gm = st.number_input("Target Gross Margin (0–1)", 0.0, 0.95, gm_default, step=0.01)

total_added_cost_mo = on_costs_mo + capex_amort_mo + running_mo
required_revenue_mo = total_added_cost_mo / max(1e-9, gm)
required_revenue_wk = required_revenue_mo / 4.33
st.info(f"Added monthly cost: ${total_added_cost_mo:,.0f}  →  Required revenue/month at {gm:.0%} GM: ${required_revenue_mo:,.0f}  (~${required_revenue_wk:,.0f} / week)")
st.caption("Rule of thumb: with avg job value and GM, divide weekly revenue target by avg job price to estimate extra jobs/week.")
