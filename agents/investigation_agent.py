class InvestigationAgent:

    def generate_case_summary(

        self,

        node,

        suspicious,

        risk_score

    ):

        summary = f"""

Investigation Summary
---------------------

Account: {node}

Risk Score: {risk_score}

Suspicious: {suspicious}

Recommendation:
Manual AML investigation recommended.
"""

        return summary