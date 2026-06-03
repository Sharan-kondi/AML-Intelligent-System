# graph/graph_visualization.py

import pickle
from pyvis.network import Network
import random
import os

GRAPH_PATH = "data/processed/transaction_graph.pkl"
OUTPUT_PATH = "graph/graph.html"


def visualize_graph():

    print("Loading graph...")

    if not os.path.exists(GRAPH_PATH):
        raise FileNotFoundError("❌ Graph file not found. Run graph_builder first.")

    with open(GRAPH_PATH, "rb") as f:
        G = pickle.load(f)

    print("Graph loaded successfully!")

    # ✅ FIX: disable notebook mode
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        notebook=False
    )

    # optional physics (looks better)
    net.barnes_hut()

    # ⚠️ SAMPLE NODES (important for performance)
    nodes = list(G.nodes())
    sampled_nodes = random.sample(nodes, min(200, len(nodes)))

    # add nodes
    for node in sampled_nodes:
        net.add_node(node, label=str(node))

    # add edges
    for u, v, data in G.edges(data=True):
        if u in sampled_nodes and v in sampled_nodes:
            net.add_edge(
                u,
                v,
                value=data.get("weight", 1),
                title=f"Amount: {data.get('weight', 0)}"
            )

    # ensure output folder exists
    os.makedirs("graph", exist_ok=True)

    # ✅ FIX: use write_html instead of show()
    net.write_html(OUTPUT_PATH)

    print(f"✅ Graph saved successfully at: {OUTPUT_PATH}")
    print("👉 Open this file in your browser")


if __name__ == "__main__":
    visualize_graph()