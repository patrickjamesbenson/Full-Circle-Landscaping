import streamlit as st, pandas as pd
from utils.ui import bootstrap, section, configure_page, footer
from utils.xldb import read, write, get_setting
configure_page("What If — Revenue Calc.", home=False)

bootstrap(); section("What If — Revenue Calc.","Monthly cost, equipment, and required revenue at target GM")

roles = read("Roles"); costs = read("Role_Costs"); equip = read("Equipment_Items").copy()
gm_default = float(get_setting("gm_target","0.40"))
gm = st.number_input("Target Gross Margin (0–1)", 0.0, 0.95, gm_default, step=0.01)

section("Choose Role & Monthly Cost")
if roles.empty: st.warning("No roles found. Add roles and costs in Roles & Responsibilities.")
else:
    r = st.selectbox("Role", roles["id"].astype(int).astype(str) + " — " + roles["role_name"])
    rid = int(r.split("—")[0].strip())
    base_cost = float(costs.loc[costs["role_id"]==rid, "monthly_cost"].iloc[0]) if (costs["role_id"]==rid).any() else 0.0
    st.write(f"Base monthly employment cost: **${base_cost:,.0f}**")

section("Equipment & Running Costs (editable)")
equip["selected"] = equip["selected"].fillna(False)
edited = st.data_editor(equip, hide_index=True, use_container_width=True, num_rows="dynamic")
write("Equipment_Items", edited)
equip_total = float(edited.loc[edited["selected"]==True,"monthly_cost"].fillna(0).sum())

section("Result")
added_cost = base_cost + equip_total
req_revenue = (added_cost / max(0.01, gm))
c1,c2,c3 = st.columns(3)
with c1: st.metric("Added monthly cost", f"${added_cost:,.0f}")
with c2: st.metric("GM target", f"{gm:.0%}")
with c3: st.metric("Required monthly revenue", f"${req_revenue:,.0f}")

st.caption("Tip: adjust GM target above or change equipment selection to see the effect immediately.")

footer()
