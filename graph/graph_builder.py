# graph/graph_builder.py

import pandas as pd
import networkx as nx
import pickle

# Path to your processed file
DATA_PATH = "data/processed/final_transactions.parquet"

# -------------------------------
# LOAD DATA
# -------------------------------
def load_data():
    print("Loading processed data...")
    df = pd.read_parquet(DATA_PATH)
    print("Data loaded:", df.shape)
    return df

# -------------------------------
# BUILD GRAPH
# -------------------------------
def build_graph(df):
    print("Building graph...")

    G = nx.DiGraph()

    for index, row in df.iterrows():
        sender = str(row["sender_id"])
        receiver = str(row["receiver_id"])
        amount = float(row["amount"])

        # Add edge
        if G.has_edge(sender, receiver):
            G[sender][receiver]["weight"] += amount
            G[sender][receiver]["count"] += 1
        else:
            G.add_edge(sender, receiver, weight=amount, count=1)

    return G

# -------------------------------
# PRINT GRAPH INFO
# -------------------------------
def print_stats(G):
    print("\nGraph Statistics")
    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())

# -------------------------------
# SAVE GRAPH
# -------------------------------
def save_graph(G):
    with open("data/processed/transaction_graph.pkl", "wb") as f:
        pickle.dump(G, f)
    print("Graph saved at data/processed/transaction_graph.pkl")

# -------------------------------
# MAIN FUNCTION
# -------------------------------
def main():
    df = load_data()
    G = build_graph(df)
    print_stats(G)
    save_graph(G)

# -------------------------------
# RUN SCRIPT
# -------------------------------
if __name__ == "__main__":
    main()