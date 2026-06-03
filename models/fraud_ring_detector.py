import networkx as nx


class FraudRingDetector:

    def __init__(self, graph):

        self.graph = graph

    def detect_fraud_rings(self):

        # ======================================
        # FIND CONNECTED COMPONENTS
        # ======================================

        # networkx.connected_components requires undirected graph.
        # If it is a DiGraph, convert to undirected.
        g_undirected = self.graph.to_undirected() if self.graph.is_directed() else self.graph

        connected_components = list(
            nx.connected_components(g_undirected)
        )

        suspicious_rings = []

        # ======================================
        # DETECT LARGE COMMUNITIES
        # ======================================

        for component in connected_components:

            if len(component) >= 3:

                suspicious_rings.append(component)

        return suspicious_rings