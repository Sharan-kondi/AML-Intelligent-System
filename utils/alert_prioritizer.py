class AlertPrioritizer:

    def prioritize(

        self,

        risk_score,

        suspicious,

        fraud_ring_count

    ):

        # ======================================
        # CRITICAL ALERT
        # ======================================

        if (

            risk_score >= 90

            and suspicious

            and fraud_ring_count >= 1
        ):

            return "CRITICAL"

        # ======================================
        # HIGH ALERT
        # ======================================

        if risk_score >= 75:

            return "HIGH"

        # ======================================
        # MEDIUM ALERT
        # ======================================

        if risk_score >= 50:

            return "MEDIUM"

        # ======================================
        # LOW ALERT
        # ======================================

        return "LOW"