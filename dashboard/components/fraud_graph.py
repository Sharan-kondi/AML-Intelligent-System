import streamlit as st
import networkx as nx
import pickle
from pyvis.network import Network
import streamlit.components.v1 as components



def show_graph():

    st.subheader("🌐 Fraud Network Graph")

    try:

        with open(
            "data/processed/transaction_graph.pkl",
            "rb"
        ) as f:

            G = pickle.load(f)

        net = Network(
            height="700px",
            width="100%",
            bgcolor="#0B1220",
            font_color="white"
        )

        for node in G.nodes():

            net.add_node(
                node,
                label=node,
                color="#00F5D4"
            )

        for edge in G.edges():

            net.add_edge(
                edge[0],
                edge[1]
            )

        net.save_graph(
            "dashboard/graph.html"
        )

        with open(
            "dashboard/graph.html",
            "r",
            encoding="utf-8"
        ) as f:

            html = f.read()

        components.html(
            html,
            height=700
        )

    except Exception as e:

        st.error(str(e))