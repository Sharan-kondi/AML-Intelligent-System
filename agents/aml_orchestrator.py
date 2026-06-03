from agents.risk_agent import RiskAgent
from agents.explanation_agent import ExplanationAgent
from agents.investigation_agent import InvestigationAgent
from agents.compliance_agent import ComplianceAgent


class AMLOrchestrator:

    def __init__(self):

        self.risk_agent = RiskAgent()

        self.explanation_agent = ExplanationAgent()

        self.investigation_agent = InvestigationAgent()

        self.compliance_agent = ComplianceAgent()

    def process_case(

        self,

        node,

        risk_score,

        suspicious,

        explanations,

        fraud_rings

    ):

        # ======================================
        # RISK ANALYSIS
        # ======================================

        risk_result = self.risk_agent.analyze_risk(
            risk_score
        )

        # ======================================
        # XAI EXPLANATION
        # ======================================

        explanation_result = self.explanation_agent.generate_explanation(
            explanations
        )

        # ======================================
        # INVESTIGATION SUMMARY
        # ======================================

        investigation_result = self.investigation_agent.generate_case_summary(
            node=node,
            suspicious=suspicious,
            risk_score=risk_score
        )

        # ======================================
        # COMPLIANCE REPORT
        # ======================================

        compliance_result = self.compliance_agent.generate_compliance_report(
            node=node,
            suspicious=suspicious,
            fraud_rings=fraud_rings
        )

        return {

            "risk_analysis": risk_result,

            "explanation": explanation_result,

            "investigation": investigation_result,

            "compliance": compliance_result
        }