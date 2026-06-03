import networkx as nx


class ReasonGenerator:

    def __init__(self, graph):

        self.graph = graph

    def generate_reason(

        self,

        node,

        transaction_amount,

        suspicious_prediction

    ):

        reasons = []

        # ======================================
        # HIGH TRANSACTION AMOUNT
        # ======================================

        if transaction_amount > 50000:

            reasons.append(
                "High transaction amount detected"
            )

        # ======================================
        # HIGH NETWORK CONNECTIVITY
        # ======================================

        degree = self.graph.degree(node)

        if degree >= 3:

            reasons.append(
                "Highly connected account in transaction network"
            )

        # ======================================
        # HIGH PAGERANK
        # ======================================

        pagerank = nx.pagerank(self.graph).get(node, 0)

        if pagerank > 0.20:

            reasons.append(
                "High influence score in graph network"
            )

        # ======================================
        # GNN DETECTION
        # ======================================

        if suspicious_prediction:

            reasons.append(
                "GNN model classified account as suspicious"
            )

        # ======================================
        # DEFAULT
        # ======================================

        if len(reasons) == 0:

            reasons.append(
                "No major suspicious indicators found"
            )

        return reasons