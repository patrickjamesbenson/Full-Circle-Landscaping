import streamlit as st
import pandas as pd
from utils.ui import bootstrap, section

conn = bootstrap()
section("Money In / Money Out", "Track AR, payments, and expenses")

st.subheader("Accounts Receivable (Invoices)")
df = pd.read_sql_query("SELECT id, job_id, issue_date, due_date, total, status, paid_date, paid_method FROM invoices ORDER BY date(issue_date) DESC", conn)
st.dataframe(df, width='stretch')

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

df2 = pd.read_sql_query("SELECT date, vendor, category, description, amount FROM ap_expenses ORDER BY date(date) DESC", conn)
st.dataframe(df2, width='stretch')

st.subheader("Monthly Summary")
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

for col in ["paid_revenue","ar_open","expenses"]:
    summary[col] = pd.to_numeric(summary[col], errors="coerce").fillna(0.0)

summary["profit_estimate"] = summary["paid_revenue"] - summary["expenses"]
st.dataframe(summary, width='stretch')
