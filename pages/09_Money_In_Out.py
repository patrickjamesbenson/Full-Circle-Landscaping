import streamlit as st
import pandas as pd
from utils.ui import bootstrap, section
from utils.db import get_conn

conn = bootstrap()
section("Money In / Money Out", "Track AR, payments, and expenses")

st.subheader("Accounts Receivable (Invoices)")
df = pd.read_sql_query("""SELECT id, job_id, issue_date, due_date, total, status, paid_date, paid_method FROM invoices ORDER BY date(issue_date) DESC""", conn)
st.dataframe(df, use_container_width=True)

st.subheader("Expenses (AP)")
col1, col2, col3, col4 = st.columns(4)
with col1:
    d = st.date_input("Date")
with col2:
    vendor = st.text_input("Vendor")
with col3:
    cat = st.text_input("Category")
with col4:
    amt = st.number_input("Amount", 0.0, 1000000.0, 0.0)
desc = st.text_input("Description", value="")

if st.button("Add Expense"):
    conn.execute("INSERT INTO ap_expenses(date, vendor, category, description, amount) VALUES (?,?,?,?,?)", (d.isoformat(), vendor, cat, desc, amt))
    conn.commit()
    st.success("Expense added.")

df2 = pd.read_sql_query("""SELECT date, vendor, category, description, amount FROM ap_expenses ORDER BY date(date) DESC""", conn)
st.dataframe(df2, use_container_width=True)

st.subheader("Monthly Summary")
summary = pd.read_sql_query("""
WITH rev AS (
  SELECT substr(issue_date,1,7) as yymm, SUM(CASE WHEN status='Paid' THEN total ELSE 0 END) as paid_rev,
         SUM(CASE WHEN status!='Paid' THEN total ELSE 0 END) as ar_open
  FROM invoices GROUP BY 1
), exp AS (
  SELECT substr(date,1,7) as yymm, SUM(amount) as expenses
  FROM ap_expenses GROUP BY 1
)
SELECT COALESCE(rev.yymm, exp.yymm) as month,
       COALESCE(paid_rev,0) as paid_revenue,
       COALESCE(ar_open,0) as ar_open,
       COALESCE(expenses,0) as expenses,
       COALESCE(paid_rev,0) - COALESCE(expenses,0) as profit_estimate
FROM rev
FULL OUTER JOIN exp ON rev.yymm = exp.yymm
""", conn)
# SQLite doesn't support FULL OUTER JOIN; simulate with union
summary = pd.read_sql_query("""
SELECT m as month,
       COALESCE((SELECT SUM(total) FROM invoices WHERE status='Paid' AND substr(issue_date,1,7)=m),0) as paid_revenue,
       COALESCE((SELECT SUM(total) FROM invoices WHERE status!='Paid' AND substr(issue_date,1,7)=m),0) as ar_open,
       COALESCE((SELECT SUM(amount) FROM ap_expenses WHERE substr(date,1,7)=m),0) as expenses
FROM (
  SELECT DISTINCT substr(issue_date,1,7) as m FROM invoices
  UNION
  SELECT DISTINCT substr(date,1,7) FROM ap_expenses
) months
ORDER BY month DESC
""", conn)
summary["profit_estimate"] = summary["paid_revenue"] - summary["expenses"]
st.dataframe(summary, use_container_width=True)
