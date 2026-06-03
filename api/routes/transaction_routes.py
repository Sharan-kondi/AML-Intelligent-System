"""Transaction routes — serves live transaction data from the streaming engine."""

import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Query
from api.services.stream_service import live_transactions

router = APIRouter()


@router.get("/transactions")
def get_transactions(limit: int = Query(20, ge=1, le=100)):
    """Get recent transactions processed in real-time by the streaming engine."""
    # Generate initial sample transactions if history is empty at server startup
    if not live_transactions:
        for i in range(limit):
            risk = random.randint(30, 95)
            amount = random.randint(1000, 180000)
            risk_label = "FLAGGED" if risk >= 80 else "MONITORING"
            dt = datetime.now() - timedelta(minutes=i * 2 + random.randint(0, 90))
            
            live_transactions.append({
                "id": f"TXN-{random.randint(100000, 999999)}",
                "sender": f"ACC{random.randint(10000, 10100)}",
                "receiver": f"ACC{random.randint(10000, 10100)}",
                "amount": float(amount),
                "risk_score": float(risk),
                "status": risk_label,
                "timestamp": dt.isoformat(),
            })

    # Sort history by timestamp descending and return the limit requested
    sorted_txs = sorted(live_transactions, key=lambda x: x["timestamp"], reverse=True)
    return {"transactions": sorted_txs[:limit]}
