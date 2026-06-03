import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')
    )
)
import json
import torch
import networkx as nx

from kafka import KafkaConsumer
from torch_geometric.data import Data

from gnn_model import AML_GNN
from agents.aml_orchestrator import AMLOrchestrator

from explainability.reason_generator import ReasonGenerator

from models.risk_scoring import AMLRiskScorer

from models.fraud_ring_detector import FraudRingDetector

from utils.case_manager import AMLCaseManager

from utils.alert_prioritizer import AlertPrioritizer


# ==========================================
# GRAPH INITIALIZATION
# ==========================================

G = nx.Graph()

print("🚀 Real-Time GNN Engine Started...\n")


# ==========================================
# LOAD MODEL
# ==========================================

model = AML_GNN(
    input_dim=3,
    hidden_dim=16,
    output_dim=2
)

checkpoint_path = "models/gnn_checkpoint.pt"
if os.path.exists(checkpoint_path):
    try:
        model.load_state_dict(torch.load(checkpoint_path, map_location=torch.device('cpu')))
        print("💾 Loaded GNN model from checkpoint!")
    except Exception as e:
        print(f"⚠️ Error loading GNN checkpoint: {str(e)}")

model.eval()


# ==========================================
# KAFKA CONSUMER
# ==========================================

consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers='localhost:9092',

    auto_offset_reset='earliest',

    enable_auto_commit=True,

    group_id='gnn-group',

    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)


# ==========================================
# STREAM PROCESSING
# ==========================================

for message in consumer:

    print("\n📩 GNN RECEIVED MESSAGE")

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
    # NODE INDEXING
    # ======================================

    node_mapping = {}

    for i, node in enumerate(G.nodes()):

        node_mapping[node] = i

    # ======================================
    # EDGE INDEX
    # ======================================

    edge_index = []

    for edge in G.edges():

        src = node_mapping[edge[0]]
        dst = node_mapping[edge[1]]

        edge_index.append([src, dst])

    if len(edge_index) == 0:
        continue

    edge_index = torch.tensor(
        edge_index,
        dtype=torch.long
    ).t().contiguous()

    # ======================================
    # NODE FEATURES
    # ======================================

    x = torch.rand(
        (len(G.nodes()), 3),
        dtype=torch.float
    )

    # ======================================
    # CREATE GRAPH DATA
    # ======================================

    data = Data(
        x=x,
        edge_index=edge_index
    )

    # ======================================
    # GNN PREDICTION
    # ======================================

    with torch.no_grad():

        output = model(data)

        predictions = output.argmax(dim=1)

    # ======================================
    # DISPLAY RESULTS
    # ======================================

    print("\n🧠 GNN Fraud Predictions:\n")

    suspicious_count = 0

    scorer = AMLRiskScorer(G)

    for node, idx in node_mapping.items():

        prediction = predictions[idx].item()

        suspicious = prediction == 1

        risk_score = scorer.calculate_risk_score(
            node=node,
            transaction_amount=amount,
            suspicious_prediction=suspicious
        )

        if suspicious:

            suspicious_count += 1

            print(f"🚨 Suspicious Account: {node}")

        else:

            print(f"✅ Normal Account: {node}")

        print(f"⚠️ AML Risk Score: {risk_score}/100\n")

                # ======================================
        # XAI REASONING
        # ======================================

        reason_generator = ReasonGenerator(G)

        reasons = reason_generator.generate_reason(

            node=node,

            transaction_amount=amount,

            suspicious_prediction=suspicious
        )

        print("\n🧠 XAI Explanation")

        for reason in reasons:

            print(f"   ↳ {reason}")

        print()

    # ======================================
    # GRAPH STATS
    # ======================================

    print("\n📊 Graph Statistics")

    print(f"Nodes : {G.number_of_nodes()}")
    print(f"Edges : {G.number_of_edges()}")

        # ======================================
    # FRAUD RING DETECTION
    # ======================================

    detector = FraudRingDetector(G)

    rings = detector.detect_fraud_rings()

    print("\n🕸️ Fraud Ring Detection")

    if len(rings) == 0:

        print("✅ No Fraud Rings Detected")

    else:

        for i, ring in enumerate(rings):

            print(f"\n🚨 Fraud Ring {i + 1}")

            for member in ring:

                print(f"   ↳ {member}")


        orchestrator = AMLOrchestrator()

        results = orchestrator.process_case(

            node=node,

            risk_score=risk_score,

            suspicious=suspicious,

            explanations=reasons,

            fraud_rings=rings
        )

        print("\n🤖 AML Agentic Intelligence\n")

        print(results["risk_analysis"])

        print(results["explanation"])

        print(results["investigation"])

        print(results["compliance"])

        # ======================================
        # AML CASE STORAGE
        # ======================================

        case_manager = AMLCaseManager()

        saved_case = case_manager.save_case(

            node=node,

            risk_score=risk_score,

            suspicious=suspicious,

            explanations=reasons,

            fraud_rings=rings
        )

        print("💾 AML Case Saved")

        print(saved_case)

        # ======================================
        # ALERT PRIORITIZATION
        # ======================================

        prioritizer = AlertPrioritizer()

        priority = prioritizer.prioritize(

            risk_score=risk_score,

            suspicious=suspicious,

            fraud_ring_count=len(rings)
        )

        print("🚨 Alert Priority")

        print(f"Priority Level : {priority}")

        print()