import streamlit as st
import pandas as pd
from utils.ui import bootstrap, section
from utils.db import get_conn

conn = bootstrap()
section("Quoting", "Build quotes from price book and convert to jobs")

leads = pd.read_sql_query("SELECT id, name FROM leads ORDER BY id DESC", conn)
items = pd.read_sql_query("SELECT id, name, unit_rate FROM price_items ORDER BY name", conn)

st.subheader("Create or select a Quote")
col1, col2 = st.columns(2)
with col1:
    lead_id = st.selectbox("Lead", leads["id"].astype(str) + " - " + leads["name"] if not leads.empty else [], index=0 if not leads.empty else None)
with col2:
    existing_quote_id = st.number_input("Existing Quote ID (optional)", min_value=0, value=0, step=1)

if st.button("Create Draft Quote"):
    if lead_id:
        lid = int(str(lead_id).split(" - ")[0])
        conn.execute("INSERT INTO quotes(lead_id, created_at, status, total, notes) VALUES (?,?,?,0,'')", (lid, __import__("datetime").datetime.now().isoformat(), "Draft"))
        conn.commit()
        st.success("Draft quote created.")

st.subheader("Quote Items")
qid = st.number_input("Quote ID to edit", min_value=1, step=1)
col3, col4, col5 = st.columns(3)
with col3:
    item = st.selectbox("Item", items["name"] if not items.empty else [])
with col4:
    qty = st.number_input("Qty", 0.0, 100000.0, 1.0)
with col5:
    if item:
        unit_rate = float(items[items["name"]==item]["unit_rate"].values[0])
    else:
        unit_rate = 0.0
    st.write(f"Unit rate: ${unit_rate:.2f}")

if st.button("Add line item") and item:
    item_id = int(items[items["name"]==item]["id"].values[0])
    line_total = round(qty * unit_rate, 2)
    conn.execute("""INSERT INTO quote_items(quote_id, item_id, description, qty, unit_price, line_total)
                    VALUES (?,?,?,?,?,?)""", (qid, item_id, item, qty, unit_rate, line_total))
    tot = conn.execute("SELECT ROUND(SUM(line_total),2) as t FROM quote_items WHERE quote_id=?", (qid,)).fetchone()["t"] or 0
    conn.execute("UPDATE quotes SET total=? WHERE id=?", (tot, qid))
    conn.commit()
    st.success("Item added.")

dfi = pd.read_sql_query("""SELECT qi.id, qi.description, qi.qty, qi.unit_price, qi.line_total
                           FROM quote_items qi WHERE qi.quote_id=?""", conn, params=(qid,))
st.dataframe(dfi, use_container_width=True)
qt = conn.execute("SELECT * FROM quotes WHERE id=?", (qid,)).fetchone()
if qt:
    st.info(f"Quote #{qid} — Status: {qt['status']} — Total: ${qt['total']:.2f}")
    new_status = st.selectbox("Update status", ["Draft","Sent","Accepted","Declined","Expired"], index=["Draft","Sent","Accepted","Declined","Expired"].index(qt['status']))
    notes = st.text_area("Notes", value=qt.get("notes") or "", height=100)
    if st.button("Save quote status/notes"):
        conn.execute("UPDATE quotes SET status=?, notes=? WHERE id=?", (new_status, notes, qid))
        conn.commit()
        st.success("Quote updated.")
    if st.button("Create Job from Accepted Quote"):
        conn.execute("INSERT INTO jobs(quote_id, scheduled_date, start_time, end_time, crew, status) VALUES (?,?, ?, ?, ?, ?)", (qid, None, None, None, "Tony", "Scheduled"))
        conn.commit()
        st.success("Job created (go to Scheduling).")
