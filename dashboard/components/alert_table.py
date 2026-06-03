import streamlit as st
import pandas as pd
import os
import json


def load_cases():

    folder = "data/cases"

    rows = []

    if not os.path.exists(folder):

        return pd.DataFrame()

    for file in os.listdir(folder):

        if file.endswith(".json"):

            path = os.path.join(folder, file)

            with open(path, "r") as f:

                data = json.load(f)

                rows.append(data)

    return pd.DataFrame(rows)


def show_alert_table():

    st.subheader("🚨 AML Alert Center")

    df = load_cases()

    if len(df) == 0:

        st.warning("No AML Cases Found")

        return

    st.dataframe(
        df,
        use_container_width=True
    )