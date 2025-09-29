import streamlit as st, pandas as pd
from utils.ui import bootstrap, section

conn = bootstrap()
section("Contacts & Leads (MQL → SQL)", "Maintain contacts and link leads to them")

st.subheader("Add / Edit Contact")
with st.form("add_contact"):
    c1, c2 = st.columns(2)
    with c1:
        fn = st.text_input("First name")
        phone = st.text_input("Mobile")
        street = st.text_input("Street")
        suburb = st.text_input("Suburb")
    with c2:
        ln = st.text_input("Last name")
        email = st.text_input("Email")
        postcode = st.text_input("Postcode")
        state = st.text_input("State", value="NSW")
    if st.form_submit_button("Save contact") and fn and ln:
        conn.execute("""INSERT INTO contacts(first_name,last_name,phone,email,street,suburb,postcode,state)
                        VALUES (?,?,?,?,?,?,?,?)""", (fn,ln,phone,email,street,suburb,postcode,state))
        conn.commit()
        st.success("Contact saved.")

contacts = pd.read_sql_query("SELECT id, first_name, last_name, phone, email, suburb FROM contacts ORDER BY id DESC LIMIT 200", conn)
with st.expander("Contacts (latest 200)", expanded=False):
    st.dataframe(contacts, width='stretch')

st.subheader("Add Lead")
channels = [r["name"] for r in conn.execute("SELECT name FROM channels")]
services = [r["name"] for r in conn.execute("SELECT name FROM services")]
with st.form("add_lead"):
    contact_label = st.selectbox("Contact", [f"{r['id']} — {r['first_name']} {r['last_name']} ({r['suburb']})" for _,r in contacts.iterrows()] if not contacts.empty else [])
    channel = st.selectbox("Channel", channels)
    service_requested = st.selectbox("Service requested", services)
    tier = st.selectbox("Customer tier", ["Economy","Business","First"])
    budget = st.selectbox("Budget sense", ["Low","OK","Premium"])
    timing = st.selectbox("Timing", ["ASAP","Within 2 weeks","Flexible"])
    notes = st.text_area("Notes", height=80)
    if st.form_submit_button("Create lead") and contact_label:
        cid = int(contact_label.split(" — ")[0])
        conn.execute("""INSERT INTO leads(contact_id, channel_id, service_requested, notes, tier, budget, timing, mql_status, sql_status, status, created_at)
                        VALUES (?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
                     (cid, conn.execute("SELECT id FROM channels WHERE name=?", (channel,)).fetchone()["id"],
                      service_requested, notes, tier, budget, timing, 1, 0, "New"))
        conn.commit()
        st.success("Lead created.")

with st.expander("Leads", expanded=False):
    df = pd.read_sql_query("""
    SELECT l.id, l.created_at, c.first_name || ' ' || c.last_name as contact, c.suburb, s.name as service, ch.name as channel,
           l.tier, l.budget, l.timing, l.mql_status, l.sql_status, l.status
    FROM leads l
    JOIN contacts c ON l.contact_id=c.id
    LEFT JOIN channels ch ON ch.id=l.channel_id
    LEFT JOIN services s ON s.name=l.service_requested
    ORDER BY datetime(l.created_at) DESC
    """, conn)
    st.dataframe(df, width='stretch', height=360)

st.subheader("Qualify / Promote to Quote")
lid = st.number_input("Lead ID", 1, step=1)
col1, col2, col3 = st.columns(3)
with col1: mql = st.selectbox("MQL", [0,1])
with col2: sql = st.selectbox("SQL", [0,1])
with col3: status = st.selectbox("Status", ["New","Contacted","Qualified","Disqualified"])
notes2 = st.text_area("Update notes (optional)", height=80)
if st.button("Update lead"):
    conn.execute("UPDATE leads SET mql_status=?, sql_status=?, status=?, notes=COALESCE(notes,'') || CHAR(10) || ? WHERE id=?",
                 (mql, sql, status, notes2, lid))
    conn.commit()
    st.success("Lead updated.")

if st.button("Create Quote from Lead"):
    conn.execute("INSERT INTO quotes(lead_id, created_at, status, total, gm_pct, notes) VALUES (?,?,?,0,(SELECT value FROM settings WHERE key='default_gm_pct'), '')",
                 (lid, __import__("datetime").datetime.now().isoformat(), "Draft"))
    conn.commit()
    st.success("Draft quote created.")
