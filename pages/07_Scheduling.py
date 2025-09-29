# ==============================
# FILE: pages/07_Scheduling.py
# ==============================
import os, sys, subprocess
import streamlit as st, pandas as pd
from datetime import date
from utils.ui import bootstrap, section
from utils.xldb import read, write, next_id

bootstrap(); section("Scheduling","Assign jobs, dates, crew; keep 1–2 weeks ahead")
APP_ROOT = os.path.dirname(os.path.dirname(__file__))
QUOTE_PHOTOS = os.path.join(APP_ROOT, "assets", "quote_photos")
os.makedirs(QUOTE_PHOTOS, exist_ok=True)

def open_folder(path:str)->bool:
    try:
        if os.name == "nt":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception as e:
        st.error(f"Could not open folder: {e}")
        return False

quotes = read("Quotes"); jobs = read("Jobs"); leads = read("Leads"); contacts = read("Contacts")

with st.expander("Create Job from Quote", expanded=False):
    qid = st.number_input("Quote ID", min_value=1, step=1); d = st.date_input("Date", value=date.today())
    s = st.text_input("Start (HH:MM)", value="08:00"); e = st.text_input("End (HH:MM)", value="11:00")
    crew = st.text_input("Crew", value="Tony;Sam")
    if st.button("Create Job"):
        jid = next_id(jobs); row = {"id":jid,"quote_id":qid,"scheduled_date":d.isoformat(),"start_time":s,"end_time":e,"crew":crew,"status":"Scheduled"}
        jobs = pd.concat([jobs, pd.DataFrame([row])], ignore_index=True); write("Jobs", jobs); st.success("Job created.")

with st.expander("Jobs (schedule with names + BEFORE photos)", expanded=True):
    # Quick folder open
    if st.button("Open BEFORE photos folder"):
        if open_folder(QUOTE_PHOTOS): st.success("Opened photos folder.")
    jf = jobs.copy()
    if not jf.empty:
        # Join: Jobs -> Quotes -> Leads -> Contacts
        q = quotes.rename(columns={"id":"quote_id_q"})[["quote_id_q","lead_id","total"]]
        jf = jf.merge(q, left_on="quote_id", right_on="quote_id_q", how="left")
        l = leads.rename(columns={"id":"lead_id_l"})[["lead_id_l","contact_id","service_requested"]]
        jf = jf.merge(l, left_on="lead_id", right_on="lead_id_l", how="left")
        c = contacts.rename(columns={"id":"contact_id_c"})[["contact_id_c","first_name","last_name","suburb"]]
        jf = jf.merge(c, left_on="contact_id", right_on="contact_id_c", how="left")

        jf["scheduled_date"] = pd.to_datetime(jf["scheduled_date"], errors="coerce")
        jf["contact"] = (jf["first_name"].fillna("") + " " + jf["last_name"].fillna("")).str.strip()

        # BEFORE photo counts per quote
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
        jf["before_photos"] = jf["quote_id"].astype("Int64").map(counts).fillna(0).astype(int)

        disp = jf.sort_values("scheduled_date", na_position="last")
        disp = disp[["id","scheduled_date","start_time","end_time","service_requested","contact","suburb","crew","status","total","before_photos"]]
        disp = disp.rename(columns={"id":"job_id","total":"revenue_est"})
        st.dataframe(disp, use_container_width=True, hide_index=True)

        # preview picker
        jpick = st.number_input("Preview BEFORE photos for Job ID", min_value=1, step=1, key="jprev")
        row = jf[jf["id"].astype(int)==jpick]
        if not row.empty:
            qid_for_job = int(row["quote_id"].iloc[0]) if pd.notna(row["quote_id"].iloc[0]) else None
            if qid_for_job:
                existing = sorted([p for p in os.listdir(QUOTE_PHOTOS) if p.startswith(f"quote{qid_for_job}_")])
                if existing:
                    cols = st.columns(6)
                    for i, p in enumerate(existing[:24]):
                        with cols[i % 6]:
                            st.image(os.path.join(QUOTE_PHOTOS, p), caption=p, use_column_width=True)
                else:
                    st.caption("No BEFORE photos for this job's quote.")
            else:
                st.caption("This job is not linked to a quote.")
    else:
        st.info("No jobs yet.")

