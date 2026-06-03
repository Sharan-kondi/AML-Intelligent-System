class RiskAgent:

    def analyze_risk(self, risk_score):

        if risk_score >= 80:

            return "HIGH RISK ACCOUNT"

        elif risk_score >= 50:

            return "MEDIUM RISK ACCOUNT"

        return "LOW RISK ACCOUNT"