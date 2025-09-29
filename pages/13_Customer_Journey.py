import streamlit as st, pandas as pd
from utils.ui import bootstrap, section

conn = bootstrap()
section("Customer Journey / Experience", "Stages and customer touchpoints (non-geographic)")

st.subheader("Stages")
with st.expander("Edit stages (stage, goal, owner)", expanded=False):
    df = pd.read_sql_query("SELECT id, stage, goal, owner FROM journey_stages ORDER BY id", conn)
    ed = st.data_editor(df, num_rows="dynamic", key="stages_editor", width='stretch')
    if st.button("Save stages"):
        conn.execute("DELETE FROM journey_stages")
        for _, r in ed.iterrows():
            if (r.get("stage") or "").strip():
                conn.execute("INSERT INTO journey_stages(stage,goal,owner) VALUES (?,?,?)", (r.get("stage",""), r.get("goal",""), r.get("owner","")))
        conn.commit()
        st.success("Stages saved.")

st.subheader("Touchpoints")
with st.expander("Edit touchpoints (touchpoint, stage)", expanded=False):
    df2 = pd.read_sql_query("SELECT id, touchpoint, stage FROM journey_touches ORDER BY id", conn)
    ed2 = st.data_editor(df2, num_rows="dynamic", key="touches_editor", width='stretch')
    if st.button("Save touchpoints"):
        conn.execute("DELETE FROM journey_touches")
        for _, r in ed2.iterrows():
            if (r.get("touchpoint") or "").strip():
                conn.execute("INSERT INTO journey_touches(touchpoint,stage) VALUES (?,?)", (r.get("touchpoint",""), r.get("stage","")))
        conn.commit()
        st.success("Touchpoints saved.")

st.subheader("Funnel Snapshot (last 30 days)")
snap = pd.read_sql_query("""
SELECT
  SUM(CASE WHEN date(created_at) >= date('now','-30 day') THEN 1 ELSE 0 END) AS leads_30d,
  SUM(CASE WHEN sql_status=1 AND date(created_at) >= date('now','-30 day') THEN 1 ELSE 0 END) AS sql_30d
FROM leads
""", conn)
quotes = pd.read_sql_query("""
SELECT
  SUM(CASE WHEN date(created_at) >= date('now','-30 day') THEN 1 ELSE 0 END) AS quotes_30d,
  SUM(CASE WHEN status='Accepted' AND date(created_at) >= date('now','-30 day') THEN 1 ELSE 0 END) AS accepted_30d
FROM quotes
""", conn)
inv = pd.read_sql_query("""
SELECT
  SUM(CASE WHEN status='Paid' AND date(paid_date) >= date('now','-30 day') THEN 1 ELSE 0 END) AS paid_invoices_30d
FROM invoices
""", conn)
st.write(f"Leads: **{int(snap.iloc[0]['leads_30d'] or 0)}**  |  SQLs: **{int(snap.iloc[0]['sql_30d'] or 0)}**  |  Quotes: **{int(quotes.iloc[0]['quotes_30d'] or 0)}**  |  Accepted: **{int(quotes.iloc[0]['accepted_30d'] or 0)}**  |  Paid invoices: **{int(inv.iloc[0]['paid_invoices_30d'] or 0)}**")
