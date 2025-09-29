# ===========================
# FILE: pages/06_Quoting.py
# ===========================
import os, sys, subprocess, time
import streamlit as st, pandas as pd
from utils.ui import bootstrap, section
from utils.xldb import read, write, next_id, get_setting

bootstrap(); section("Quoting","Target Gross Margin applies to pricing")
APP_ROOT = os.path.dirname(os.path.dirname(__file__))
QUOTE_PHOTOS = os.path.join(APP_ROOT, "assets", "quote_photos")
os.makedirs(QUOTE_PHOTOS, exist_ok=True)

def open_folder(path:str)->bool:
    """Why: convenience to open photos folder in platform file manager."""
    try:
        if os.name == "nt":
            os.startfile(path)  # Windows
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception as e:
        st.error(f"Could not open folder: {e}")
        return False

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

with st.expander("Edit quote lines + BEFORE photos", expanded=True):
    qid = st.number_input("Quote ID", min_value=1, step=1)
    # Quick access to folder
    if st.button("Open BEFORE photos folder"):
        if open_folder(QUOTE_PHOTOS): st.success("Opened photos folder.")
    if (quotes["id"].astype(int)==qid).any():
        q = quotes.loc[quotes["id"].astype(int)==qid].iloc[0]
        st.write(f"Quote #{int(q['id'])} — Status: {q['status']}")

        # BEFORE photos uploader
        files = st.file_uploader("Upload BEFORE photos (attached to this quote)", accept_multiple_files=True, type=["png","jpg","jpeg"])
        if st.button("Save photos"):
            saved = 0
            for ph in files or []:
                ts = time.strftime("%Y%m%d_%H%M%S")
                safe = ph.name.replace(" ", "_")
                with open(os.path.join(QUOTE_PHOTOS, f"quote{qid}_{ts}_{safe}"), "wb") as f:
                    f.write(ph.getbuffer())
                saved += 1
            st.success(f"Saved {saved} photo(s).")

        # Existing thumbnails
        existing = sorted([p for p in os.listdir(QUOTE_PHOTOS) if p.startswith(f"quote{qid}_")])
        if existing:
            st.caption("Existing BEFORE photos:")
            cols = st.columns(6)
            for i, p in enumerate(existing[:24]):  # show up to 24 thumbs
                with cols[i % 6]:
                    st.image(os.path.join(QUOTE_PHOTOS, p), caption=p, use_column_width=True)

        # Quote lines UI
        if not price.empty:
            it = st.selectbox("Item", price["name"].tolist()); qty = st.number_input("Qty", 0.0, 10000.0, 1.0)
            mode = st.radio("Pricing mode", ["Use unit rate","Back-calc from GM"])
            if st.button("Add line") and qty>0:
                pb = price.loc[price["name"]==it].iloc[0]; unit_rate = float(pb["unit_rate"])
                sell = unit_rate if mode=="Use unit rate" else (unit_rate*0.6)/(1-gm_target)  # why: hit GM target
                line_total = round(qty*sell,2)
                qit = read("Quote_Items"); qitid = next_id(qit)
                row = {"id":qitid,"quote_id":qid,"item_id":int(pb["id"]),"description":it,"qty":qty,"unit_price":round(sell,2),
                       "cost_estimate":round(sell*0.6,2),"line_total":line_total,"gm":round(1-(sell*0.6)/max(0.01,sell),2)}
                qit = pd.concat([qit, pd.DataFrame([row])], ignore_index=True); write("Quote_Items", qit)
                tot = float(qit.loc[qit["quote_id"]==qid,"line_total"].fillna(0).sum()); quotes.loc[quotes["id"]==qid,"total"]=round(tot,2); write("Quotes", quotes)
                st.success("Line added.")
    else:
        st.info("Enter an existing Quote ID.")

with st.expander("Quotes table (with lead + contact + photos)", expanded=False):
    q = read("Quotes").copy(); l = read("Leads"); c = read("Contacts")
    if q.empty:
        st.info("No quotes yet.")
    else:
        l2 = l.rename(columns={"id":"lead_id"})[["lead_id","contact_id","service_requested"]]
        c2 = c.rename(columns={"id":"contact_id"})[["contact_id","first_name","last_name","suburb"]]
        m = q.merge(l2, on="lead_id", how="left").merge(c2, on="contact_id", how="left")
        m["contact"] = (m["first_name"].fillna("") + " " + m["last_name"].fillna("")).str.strip()

        # count BEFORE photos per quote
        try:
            all_files = os.listdir(QUOTE_PHOTOS)
        except FileNotFoundError:
            all_files = []
        counts = {}
        for fn in all_files:
            if fn.startswith("quote"):
                try:
                    qid_str = fn.split("_")[0].replace("quote","")
                    qid_i = int(qid_str)
                    counts[qid_i] = counts.get(qid_i, 0) + 1
                except Exception:
                    pass
        m["before_photos"] = m["id"].astype(int).map(counts).fillna(0).astype(int)

        disp = m[["id","created_at","status","target_gm","total","service_requested","contact","suburb","before_photos"]]
        st.dataframe(disp, use_container_width=True, hide_index=True)

        # quick preview + folder open
        qpick = st.number_input("Preview BEFORE photos for Quote ID", min_value=1, step=1, key="qprev")
        c1, c2 = st.columns([1,1])
        with c1:
            if st.button("Open photos folder for this Quote"):
                if open_folder(QUOTE_PHOTOS): st.success("Opened photos folder.")
        with c2:
            if (m["id"].astype(int)==qpick).any():
                existing = sorted([p for p in os.listdir(QUOTE_PHOTOS) if p.startswith(f"quote{qpick}_")])
                if existing:
                    cols = st.columns(6)
                    for i, p in enumerate(existing[:24]):
                        with cols[i % 6]:
                            st.image(os.path.join(QUOTE_PHOTOS, p), caption=p, use_column_width=True)
                else:
                    st.caption("No BEFORE photos for this quote.")

