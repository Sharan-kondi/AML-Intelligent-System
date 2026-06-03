import streamlit as st


def show_agents():

    st.subheader("🤖 Agentic AML Intelligence")

    c1, c2 = st.columns(2)

    with c1:

        st.info(
            "Risk Agent Active"
        )

        st.success(
            "Compliance Agent Running"
        )

    with c2:

        st.warning(
            "Investigation Agent Monitoring"
        )

        st.error(
            "Fraud Ring Agent Triggered"
        )