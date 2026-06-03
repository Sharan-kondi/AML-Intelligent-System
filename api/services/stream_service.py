import os
import sys
import json
import random
import time
import queue
import threading
from datetime import datetime
import networkx as nx

# Add project root to sys.path
sys.path.append(os.getcwd())

# Try importing real Kafka
try:
    from kafka import KafkaProducer, KafkaConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

# Thread-safe queue for internal fallback streaming
transaction_queue = queue.Queue()
G = nx.Graph()

# Live transaction history shared with API endpoints
live_transactions = []

# Status flags of the streaming engine
system_status = {
    "kafka_connected": False,
    "streaming_active": False,
    "fallback_mode": False,
    "last_processed_account": None,
    "total_processed": 0
}

def producer_thread_func():
    """Generates realistic AML transaction flow and sends it to Kafka or fallback queue."""
    global KAFKA_AVAILABLE
    
    # Try connecting to real local Kafka broker
    producer = None
    if KAFKA_AVAILABLE:
        try:
            producer = KafkaProducer(
                bootstrap_servers='localhost:9092',
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                request_timeout_ms=2000
            )
            system_status["kafka_connected"] = True
            print("[Streaming Service] Connected to real Kafka broker on localhost:9092")
        except Exception:
            print("[Streaming Service] Kafka broker not running. Starting local high-fidelity streaming simulation.")
            system_status["kafka_connected"] = False
            system_status["fallback_mode"] = True
    else:
        system_status["fallback_mode"] = True

    # High-risk and standard customer sample base
    customers = [f"ACC{i:06d}" for i in range(10000, 10150)]

    while True:
        try:
            sender = random.choice(customers)
            receiver = random.choice(customers)
            while receiver == sender:
                receiver = random.choice(customers)

            chance = random.random()
            # 80% normal transactions, 15% medium-risk, 5% highly suspicious AML alerts
            if chance < 0.80:
                amount = random.randint(1000, 25000)
            elif chance < 0.95:
                amount = random.randint(25000, 60000)
            else:
                amount = random.randint(60000, 220000)

            transaction = {
                "sender_id": sender,
                "receiver_id": receiver,
                "amount": float(amount),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Put in real Kafka or fallback queue
            if producer and system_status["kafka_connected"]:
                try:
                    producer.send("transactions", value=transaction)
                    producer.flush()
                except Exception:
                    system_status["kafka_connected"] = False
                    system_status["fallback_mode"] = True
                    transaction_queue.put(transaction)
            else:
                transaction_queue.put(transaction)

            # Calculate temporary metrics for transaction listing
            risk_score = round(chance * 100, 1)
            txn_id = f"TXN-{random.randint(100000, 999999)}"
            
            # Record in shared history
            live_transactions.insert(0, {
                "id": txn_id,
                "sender": sender,
                "receiver": receiver,
                "amount": float(amount),
                "risk_score": risk_score,
                "status": "FLAGGED" if risk_score >= 80 else "MONITORING",
                "timestamp": datetime.now().isoformat()
            })
            
            if len(live_transactions) > 100:
                live_transactions.pop()

        except Exception as e:
            print(f"[Streaming Service] Producer error: {e}")

        # Stream delay between 1.5 to 3 seconds
        time.sleep(random.uniform(1.5, 3.0))


def consumer_thread_func():
    """Consumes transactions and executes the GNN / Multi-Agent / Case generation pipeline in real-time."""
    global G
    
    consumer = None
    if KAFKA_AVAILABLE and system_status["kafka_connected"]:
        try:
            consumer = KafkaConsumer(
                'transactions',
                bootstrap_servers='localhost:9092',
                auto_offset_reset='latest',
                enable_auto_commit=True,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                consumer_timeout_ms=1000
            )
            print("[Streaming Service] Kafka consumer connected and listening to topic 'transactions'.")
        except Exception:
            consumer = None

    # Safely load the PyTorch GNN Model
    gnn_model = None
    try:
        import torch
        from torch_geometric.data import Data
        from models.gnn_model import AML_GNN
        
        gnn_model = AML_GNN(input_dim=3, hidden_dim=16, output_dim=2)
        checkpoint_path = "models/gnn_checkpoint.pt"
        if os.path.exists(checkpoint_path):
            gnn_model.load_state_dict(torch.load(checkpoint_path, map_location=torch.device('cpu')))
        gnn_model.eval()
        print("[Streaming Service] PyG GNN Inference model successfully loaded.")
    except Exception as e:
        print(f"[Streaming Service] GNN PyTorch Geometric load error (falling back to deterministic algorithm): {e}")

    # Import pipeline helpers
    from models.risk_scoring import AMLRiskScorer
    from models.fraud_ring_detector import FraudRingDetector
    from explainability.reason_generator import ReasonGenerator
    from agents.aml_orchestrator import AMLOrchestrator
    from utils.case_manager import AMLCaseManager
    from utils.alert_prioritizer import AlertPrioritizer

    case_manager = AMLCaseManager()
    orchestrator = AMLOrchestrator()
    prioritizer = AlertPrioritizer()

    system_status["streaming_active"] = True

    while True:
        transaction = None
        
        # 1. Fetch from Kafka if online
        if consumer and system_status["kafka_connected"]:
            try:
                msg_pack = consumer.poll(timeout_ms=500)
                for tp, messages in msg_pack.items():
                    if messages:
                        transaction = messages[-1].value
                        break
            except Exception:
                pass
                
        # 2. Otherwise fetch from internal queue
        if not transaction:
            try:
                transaction = transaction_queue.get(timeout=1.0)
            except queue.Empty:
                continue

        try:
            sender = transaction['sender_id']
            receiver = transaction['receiver_id']
            amount = transaction['amount']

            # Update structural network topology Graph G
            G.add_node(sender)
            G.add_node(receiver)
            G.add_edge(sender, receiver, weight=amount)

            # Classify using GNN if available, else standard rule threshold
            suspicious = False
            if gnn_model:
                try:
                    node_mapping = {node: idx for idx, node in enumerate(G.nodes())}
                    edge_index = []
                    for u, v in G.edges():
                        edge_index.append([node_mapping[u], node_mapping[v]])
                        
                    if len(edge_index) > 0:
                        import torch
                        from torch_geometric.data import Data
                        edge_tensor = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
                        x = torch.rand((len(G.nodes()), 3), dtype=torch.float)
                        data = Data(x=x, edge_index=edge_tensor)
                        with torch.no_grad():
                            output = gnn_model(data)
                            predictions = output.argmax(dim=1)
                            sender_idx = node_mapping.get(sender, 0)
                            suspicious = (predictions[sender_idx].item() == 1)
                except Exception:
                    suspicious = (amount > 50000)
            else:
                suspicious = (amount > 50000)

            # Calculate mathematical Risk Score
            scorer = AMLRiskScorer(G)
            risk_score = scorer.calculate_risk_score(
                node=sender,
                transaction_amount=amount,
                suspicious_prediction=suspicious
            )

            # Generate XAI Explanations
            reason_generator = ReasonGenerator(G)
            reasons = reason_generator.generate_reason(
                node=sender,
                transaction_amount=amount,
                suspicious_prediction=suspicious
            )

            # Detect network structures (Fraud Rings)
            detector = FraudRingDetector(G)
            rings = detector.detect_fraud_rings()
            
            # Orchestrate Multi-Agent decision process
            agent_results = orchestrator.process_case(
                node=sender,
                risk_score=risk_score,
                suspicious=suspicious,
                explanations=reasons,
                fraud_rings=rings
            )

            # Save the Case JSON file (this triggers the instant cache invalidation on the frontend!)
            saved_case = case_manager.save_case(
                node=sender,
                risk_score=risk_score,
                suspicious=suspicious,
                explanations=reasons,
                fraud_rings=rings
            )

            # Alert prioritization level
            priority = prioritizer.prioritize(
                risk_score=risk_score,
                suspicious=suspicious,
                fraud_ring_count=len(rings)
            )

            system_status["last_processed_account"] = sender
            system_status["total_processed"] += 1

        except Exception as e:
            print(f"[Streaming Service] Consumer error processing transaction: {e}")


def start_streaming_engine():
    """Initializes the background threads for transaction ingestion and GNN processing."""
    if not system_status["streaming_active"]:
        print("[Streaming Service] Starting Unified Real-Time Streaming Engine...")
        
        # Start Producer Thread
        prod_thread = threading.Thread(target=producer_thread_func, daemon=True)
        prod_thread.start()
        
        # Start Consumer Thread
        cons_thread = threading.Thread(target=consumer_thread_func, daemon=True)
        cons_thread.start()
        
        system_status["streaming_active"] = True
        print("[Streaming Service] Background threads successfully launched.")
