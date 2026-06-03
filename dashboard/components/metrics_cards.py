import streamlit as st


def show_metrics(

    total_transactions,
    suspicious_accounts,
    fraud_rings,
    critical_alerts
):

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Transactions",
        total_transactions
    )

    c2.metric(
        "Suspicious Accounts",
        suspicious_accounts
    )

    c3.metric(
        "Fraud Rings",
        fraud_rings
    )

    c4.metric(
        "Critical Alerts",
        critical_alerts
    )