import streamlit as st, pandas as pd
from utils.ui import bootstrap, section
from utils.xldb import read, write, next_id, get_setting

bootstrap(); section("Quoting","Target Gross Margin applies to pricing")
leads = read("Leads"); price = read("Price_Book"); quotes = read("Quotes")
gm_target = float(get_setting("gm_target","0.40"))
st.caption(f"Target GM: {gm_target:.0%} (change in Settings)")

with st.expander("Create quote from Lead", expanded=False):
    if leads.empty: st.warning("No leads to quote.")
    else:
        opt = leads["id"].astype(int).astype(str) + " — " + leads["service_requested"]
        lsel = st.selectbox("Lead", opt); lid = int(lsel.split("—")[0].strip())
        if st.button("Create Draft Quote"):
            qid = next_id(quotes)
            row = {"id":qid,"lead_id":lid,"created_at":pd.Timestamp.now().isoformat(),"status":"Draft","target_gm":gm_target,"total":0.0}
            quotes = pd.concat([quotes, pd.DataFrame([row])], ignore_index=True); write("Quotes", quotes); st.success(f"Quote #{qid} created.")

with st.expander("Edit quote lines", expanded=False):
    qid = st.number_input("Quote ID", min_value=1, step=1)
    if (quotes["id"].astype(int)==qid).any():
        q = quotes.loc[quotes["id"].astype(int)==qid].iloc[0]
        st.write(f"Quote #{int(q['id'])} — Status: {q['status']}")
        if not price.empty:
            it = st.selectbox("Item", price["name"].tolist()); qty = st.number_input("Qty", 0.0, 10000.0, 1.0)
            mode = st.radio("Pricing mode", ["Use unit rate","Back-calc from GM"])
            if st.button("Add line") and qty>0:
                pb = price.loc[price["name"]==it].iloc[0]; unit_rate = float(pb["unit_rate"])
                if mode=="Use unit rate": sell = unit_rate
                else: sell = (unit_rate*0.6)/(1-gm_target)  # why: pretend 60% of unit rate is cost to hit GM target
                line_total = round(qty*sell,2)
                qit = read("Quote_Items"); qitid = next_id(qit)
                row = {"id":qitid,"quote_id":qid,"item_id":int(pb["id"]),"description":it,"qty":qty,"unit_price":round(sell,2),
                       "cost_estimate":round(sell*0.6,2),"line_total":line_total,"gm":round(1-(sell*0.6)/max(0.01,sell),2)}
                qit = pd.concat([qit, pd.DataFrame([row])], ignore_index=True); write("Quote_Items", qit)
                tot = float(qit.loc[qit["quote_id"]==qid,"line_total"].fillna(0).sum()); quotes.loc[quotes["id"]==qid,"total"]=round(tot,2); write("Quotes", quotes)
                st.success("Line added.")
        qitems = read("Quote_Items"); st.dataframe(qitems[qitems["quote_id"]==qid], use_container_width=True)
        new_status = st.selectbox("Status", ["Draft","Sent","Accepted","Declined"], index=["Draft","Sent","Accepted","Declined"].index(q["status"]))
        if st.button("Save status"): quotes.loc[quotes["id"]==qid,"status"]=new_status; write("Quotes", quotes); st.success("Updated.")
    else:
        st.info("Enter an existing Quote ID.")
with st.expander("Quotes table", expanded=False):
    st.dataframe(read("Quotes"), use_container_width=True)
