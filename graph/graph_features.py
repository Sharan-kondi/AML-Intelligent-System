import networkx as nx
import pandas as pd


class GraphFeatureExtractor:

    def __init__(self, graph):
        self.graph = graph

    def extract_node_features(self):

        features = []

        degree_dict = dict(self.graph.degree())
        clustering_dict = nx.clustering(self.graph)

        pagerank_dict = nx.pagerank(self.graph)

        for node in self.graph.nodes():

            feature = {
                "node": node,
                "degree": degree_dict.get(node, 0),
                "clustering_coeff": clustering_dict.get(node, 0),
                "pagerank": pagerank_dict.get(node, 0)
            }

            features.append(feature)

        return pd.DataFrame(features)