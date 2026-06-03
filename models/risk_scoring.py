import networkx as nx


class AMLRiskScorer:

    def __init__(self, graph):

        self.graph = graph

    def calculate_risk_score(
        self,
        node,
        transaction_amount,
        suspicious_prediction
    ):

        # ======================================
        # GRAPH METRICS
        # ======================================

        degree = self.graph.degree(node)

        pagerank = nx.pagerank(self.graph).get(node, 0)

        # ======================================
        # RISK SCORE COMPONENTS
        # ======================================

        amount_score = min(transaction_amount / 100000, 1.0)

        degree_score = min(degree / 10, 1.0)

        pagerank_score = min(pagerank * 10, 1.0)

        prediction_score = 1.0 if suspicious_prediction else 0.2

        # ======================================
        # FINAL SCORE
        # ======================================

        risk_score = (

            amount_score * 0.35 +

            degree_score * 0.25 +

            pagerank_score * 0.20 +

            prediction_score * 0.20
        )

        return round(risk_score * 100, 2)