import streamlit as st
import json
import os



def show_investigations():

    st.subheader("🕵️ Investigation Center")

    folder = "data/cases"

    if not os.path.exists(folder):

        st.warning("No Investigation Cases")

        return

    files = os.listdir(folder)

    selected = st.selectbox(
        "Select AML Case",
        files
    )

    if selected:

        path = os.path.join(folder, selected)

        with open(path, "r") as f:

            data = json.load(f)

        st.json(data)