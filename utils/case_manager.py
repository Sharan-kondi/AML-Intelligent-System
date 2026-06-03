import json
import os
from datetime import datetime


class AMLCaseManager:

    def __init__(self):

        self.case_folder = "data/cases"

        os.makedirs(
            self.case_folder,
            exist_ok=True
        )

    def save_case(

        self,

        node,

        risk_score,

        suspicious,

        explanations,

        fraud_rings

    ):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        case_data = {

            "account": node,

            "risk_score": risk_score,

            "suspicious": suspicious,

            "explanations": explanations,

            "fraud_ring_count": len(fraud_rings),

            "timestamp": timestamp
        }

        filename = f"{node}_{timestamp}.json"

        filepath = os.path.join(
            self.case_folder,
            filename
        )

        with open(filepath, "w") as f:

            json.dump(
                case_data,
                f,
                indent=4
            )

        # Update FastAPI in-memory cache instantly
        try:
            from api.routes.alert_routes import add_case_to_cache
            add_case_to_cache(case_data)
        except Exception:
            pass

        return filepath