import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os



def show_risk_chart():

    folder = "data/cases"

    rows = []

    for file in os.listdir(folder):

        if file.endswith(".json"):

            with open(
                os.path.join(folder, file),
                "r"
            ) as f:

                rows.append(json.load(f))

    if len(rows) == 0:

        st.warning("No Cases Found")

        return

    df = pd.DataFrame(rows)

    fig = px.histogram(
        df,
        x="risk_score",
        nbins=20,
        title="AML Risk Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )