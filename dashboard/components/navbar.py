from streamlit_option_menu import option_menu
import streamlit as st


def create_navbar():

    with st.sidebar:

        st.markdown(
            """
            # 🛡️ AML Intelligence
            Enterprise Fraud Platform
            """
        )

        selected = option_menu(
             menu_title=None,

            options=[
                "Overview",
                "Real-Time Monitoring",
                "GNN Intelligence",
                "Fraud Rings",
                "Investigations",
                "XAI",
                "Agents",
                "Compliance",
                "System Analytics"
            ],

            icons=[
                "speedometer2",
                "activity",
                "diagram-3",
                "share",
                "search",
                "cpu",
                "robot",
                "shield-check",
                "bar-chart"
                            ],

            default_index=0,
        )

    return selected