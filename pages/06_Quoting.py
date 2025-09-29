import streamlit as st, pandas as pd, math
from utils.ui import bootstrap, section

conn = bootstrap()
section("Quoting", "Build quotes and compute Gross Margin / Markup")

leads = pd.read_sql_query("""
SELECT l.id, c.first_name||' '||c.last_name AS contact
FROM leads l JOIN contacts c ON l.contact_id=c.id
ORDER BY l.id DESC
""", conn)
items = pd.read_sql_query("SELECT id, name, unit_cost, unit_rate FROM price_items ORDER BY name", conn)

st.subheader("Create or select a Quote")
col1, col2 = st.columns(2)
with col1:
    lead_label = st.selectbox("Lead", [f"{r['id']} - {r['contact']}" for _,r in leads.iterrows()] if not leads.empty else [])
with col2:
    existing_quote_id = st.number_input("Existing Quote ID (optional)", min_value=0, value=0, step=1)

if st.button("Create Draft Quote") and lead_label:
    lid = int(lead_label.split(" - ")[0])
    gm_default = float((conn.execute("SELECT value FROM settings WHERE key='default_gm_pct'").fetchone() or {"value":"0.40"})["value"])
    conn.execute("INSERT INTO quotes(lead_id, created_at, status, total, gm_pct, notes) VALUES (?,?,?,0,?, '')",
                 (lid, __import__("datetime").datetime.now().isoformat(), "Draft", gm_default))
    conn.commit()
    st.success("Draft quote created.")

st.subheader("Quote Items")
qid = st.number_input("Quote ID to edit", min_value=1, step=1)

item_options = items["name"].tolist() if not items.empty else []
item = st.selectbox("Item", item_options)

id_lookup = dict(zip(items["name"], items["id"])) if not items.empty else {}
cost_lookup = dict(zip(items["name"], pd.to_numeric(items["unit_cost"], errors="coerce").fillna(0.0)))
rate_lookup = dict(zip(items["name"], pd.to_numeric(items["unit_rate"], errors="coerce").fillna(0.0)))
qty = st.number_input("Qty", 0.0, 100000.0, 1.0)

colc, colp = st.columns(2)
with colc: unit_cost = st.number_input("Override unit cost (optional)", 0.0, 1e9, float(cost_lookup.get(item,0.0)))
with colp: unit_price = st.number_input("Override unit price (optional)", 0.0, 1e9, float(rate_lookup.get(item,0.0)))

st.caption("Tip: Leave overrides as-is to use the price book values.")

if st.button("Add line item") and item:
    item_id = int(id_lookup.get(item, 0))
    if item_id == 0:
        st.error("Item not found in price book.")
    else:
        line_total = round(qty * unit_price, 2)
        conn.execute("""INSERT INTO quote_items(quote_id, item_id, description, qty, unit_cost, unit_price, line_total)
                        VALUES (?,?,?,?,?,?,?)""", (qid, item_id, item, qty, unit_cost, unit_price, line_total))
        tot = conn.execute("SELECT ROUND(SUM(line_total),2) as t FROM quote_items WHERE quote_id=?", (qid,)).fetchone()["t"] or 0
        conn.execute("UPDATE quotes SET total=? WHERE id=?", (tot, qid))
        conn.commit()
        st.success("Item added.")

with st.expander("Quote lines", expanded=False):
    dfi = pd.read_sql_query("""SELECT qi.id, qi.description, qi.qty, qi.unit_cost, qi.unit_price, qi.line_total FROM quote_items qi WHERE qi.quote_id=?""", conn, params=(qid,))
    st.dataframe(dfi, width='stretch')

qt = conn.execute("SELECT * FROM quotes WHERE id=?", (qid,)).fetchone()
if qt:
    st.info(f"Quote #{qid} — Status: {qt['status']} — Total: ${qt['total']:.2f}")
    gm_now = st.number_input("Target Gross Margin (0–1)", 0.0, 0.95, float(qt.get("gm_pct") or 0.40), step=0.01)
    notes = st.text_area("Notes", value=qt.get("notes") or "", height=100)

    # Compute GM on current lines
    sums = conn.execute("SELECT COALESCE(SUM(qty*unit_cost),0) as cost, COALESCE(SUM(line_total),0) as revenue FROM quote_items WHERE quote_id=?", (qid,)).fetchone()
    cost = float(sums["cost"] or 0.0); revenue = float(sums["revenue"] or 0.0)
    gm_actual = (revenue - cost)/revenue if revenue > 0 else 0.0
    st.write(f"**Current cost:** ${cost:,.2f}  |  **Revenue:** ${revenue:,.2f}  |  **Actual GM:** {gm_actual:.1%}")

    colA, colB = st.columns(2)
    with colA:
        if st.button("Save quote status/notes/GM"):
            conn.execute("UPDATE quotes SET gm_pct=?, notes=? WHERE id=?", (gm_now, notes, qid))
            conn.commit()
            st.success("Quote updated.")
    with colB:
        if st.button("Create Job from Accepted Quote"):
            conn.execute("""INSERT INTO jobs(quote_id, scheduled_date, start_time, end_time, crew, status) VALUES (?,?,?,?,?,?)""",
                         (qid, None, None, None, "Tony", "Scheduled"))
            conn.commit()
            st.success("Job created (go to Scheduling).")
