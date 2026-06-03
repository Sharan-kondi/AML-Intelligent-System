from kafka import KafkaProducer
import json
import random
import time
from datetime import datetime

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("✅ Kafka Producer Started...\n")

# Sample customer IDs
customers = [f"CUST_{i}" for i in range(1000, 1100)]

while True:

    sender = random.choice(customers)
    receiver = random.choice(customers)

    while receiver == sender:
        receiver = random.choice(customers)

    # -----------------------------
    # REALISTIC AML TRANSACTION FLOW
    # -----------------------------

    chance = random.random()

    # 80% normal banking traffic
    if chance < 0.80:
        amount = random.randint(1000, 30000)

    # 15% medium-risk transactions
    elif chance < 0.95:
        amount = random.randint(30000, 70000)

    # 5% suspicious AML transactions
    else:
        amount = random.randint(70000, 200000)

    transaction = {
        "sender_id": sender,
        "receiver_id": receiver,
        "amount": float(amount),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Send to Kafka topic
    producer.send("transactions", value=transaction)

    print(f"📤 Sent Transaction: {transaction}")

    # Flush immediately
    producer.flush()

    # Realistic streaming delay
    time.sleep(random.uniform(1, 3))