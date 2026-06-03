from kafka import KafkaConsumer
import json
import networkx as nx
from pyvis.network import Network

from graph_features import GraphFeatureExtractor


# ==========================================
# CREATE GRAPH
# ==========================================

G = nx.Graph()

print("✅ Real-Time Graph Engine Started...")


# ==========================================
# KAFKA CONSUMER
# ==========================================

consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers='localhost:9092',

    auto_offset_reset='earliest',

    enable_auto_commit=True,

    group_id='graph-group',

    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)


# ==========================================
# STREAM PROCESSING
# ==========================================

for message in consumer:

    print("\n📩 Message Received From Kafka")

    transaction = message.value

    sender = transaction['sender_id']
    receiver = transaction['receiver_id']
    amount = transaction['amount']

    print(f"\n💸 Transaction: {sender} → {receiver} | ₹{amount}")

    # ======================================
    # UPDATE GRAPH
    # ======================================

    G.add_node(sender)
    G.add_node(receiver)

    G.add_edge(sender, receiver, weight=amount)

    # ======================================
    # SUSPICIOUS DETECTION
    # ======================================

    if amount > 50000:

        print("\n🚨 Suspicious Graph Transaction Detected")

        print(f"Sender   : {sender}")
        print(f"Receiver : {receiver}")
        print(f"Amount   : {amount}")

    # ======================================
    # GRAPH STATS
    # ======================================

    print(f"\n📊 Current Nodes : {G.number_of_nodes()}")
    print(f"📊 Current Edges : {G.number_of_edges()}")

    # ======================================
    # GRAPH FEATURE EXTRACTION
    # ======================================

    extractor = GraphFeatureExtractor(G)

    feature_df = extractor.extract_node_features()

    print("\n📊 Graph Features:")

    print(feature_df.head())

    # ======================================
    # LIVE VISUALIZATION
    # ======================================

    print("\n📈 Updating Graph Visualization...")

    net = Network(
        height="750px",
        width="100%",
        bgcolor="#222222",
        font_color="white"
    )

    net.from_nx(G)

    output_path = "graph/live_graph.html"

    net.save_graph(output_path)

    print(f"✅ Graph Saved → {output_path}")