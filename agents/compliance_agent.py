class ComplianceAgent:

    def generate_compliance_report(

        self,

        node,

        suspicious,

        fraud_rings

    ):

        report = f"""

Compliance Report
-----------------

Account: {node}

Suspicious Activity: {suspicious}

Fraud Ring Count: {len(fraud_rings)}

Status:
Requires AML compliance review.
"""

        return report