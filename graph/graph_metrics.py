import networkx as nx
import pandas as pd
import time
import os
import pickle

GRAPH_PATH = "graph/live_transaction_graph.gpickle"

print("✅ Graph Intelligence Engine Started...\n")

while True:

    try:

        # -----------------------------
        # LOAD GRAPH
        # -----------------------------

        with open(GRAPH_PATH, "rb") as f:
            G = pickle.load(f)

        print("\n📊 Computing Graph Intelligence Metrics...\n")

        # -----------------------------
        # GRAPH METRICS
        # -----------------------------

        degree_centrality = nx.degree_centrality(G)

        betweenness_centrality = nx.betweenness_centrality(
            G,
            k=min(20, len(G.nodes())),
            normalized=True
        )

        pagerank = nx.pagerank(G)

        clustering = nx.clustering(G.to_undirected())

        # -----------------------------
        # BUILD METRICS TABLE
        # -----------------------------

        metrics = []

        for node in G.nodes():

            risk_score = (
                degree_centrality.get(node, 0) * 0.30 +
                betweenness_centrality.get(node, 0) * 0.30 +
                pagerank.get(node, 0) * 0.30 +
                clustering.get(node, 0) * 0.10
            ) * 100

            metrics.append({
                "account": node,
                "degree_centrality": round(degree_centrality.get(node, 0), 4),
                "betweenness": round(betweenness_centrality.get(node, 0), 4),
                "pagerank": round(pagerank.get(node, 0), 4),
                "clustering": round(clustering.get(node, 0), 4),
                "risk_score": round(risk_score, 2)
            })

        # -----------------------------
        # DATAFRAME
        # -----------------------------

        df = pd.DataFrame(metrics)

        df = df.sort_values(
            by="risk_score",
            ascending=False
        )

        # -----------------------------
        # SAVE RESULTS
        # -----------------------------

        os.makedirs("graph/output", exist_ok=True)

        df.to_csv(
            "graph/output/graph_risk_scores.csv",
            index=False
        )

        # -----------------------------
        # DISPLAY RESULTS
        # -----------------------------

        print("🚨 TOP SUSPICIOUS ACCOUNTS:\n")

        print(
            df[
                [
                    "account",
                    "risk_score",
                    "degree_centrality",
                    "betweenness",
                    "pagerank"
                ]
            ].head(10)
        )

        print("\n✅ Risk Scores Saved")

    except Exception as e:

        print(f"\n❌ Error: {e}")

    # Refresh every 10 seconds
    time.sleep(10)