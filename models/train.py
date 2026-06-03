import torch
import pandas as pd
import networkx as nx

from torch_geometric.data import Data
from gnn_model import AML_GNN


# ==========================================
# CREATE SAMPLE GRAPH
# ==========================================

G = nx.Graph()

transactions = [

    ("CUST_1001", "CUST_1002", 0),
    ("CUST_1002", "CUST_1003", 0),
    ("CUST_1003", "CUST_1004", 1),
    ("CUST_1004", "CUST_1005", 1),
    ("CUST_1005", "CUST_1006", 0),
]

for s, r, label in transactions:

    G.add_edge(s, r)

# ==========================================
# NODE INDEXING
# ==========================================

node_mapping = {}

for i, node in enumerate(G.nodes()):

    node_mapping[node] = i

# ==========================================
# EDGE INDEX
# ==========================================

edge_index = []

for edge in G.edges():

    src = node_mapping[edge[0]]
    dst = node_mapping[edge[1]]

    edge_index.append([src, dst])

edge_index = torch.tensor(edge_index).t().contiguous()

# ==========================================
# NODE FEATURES
# ==========================================

x = torch.rand((len(G.nodes()), 3))

# ==========================================
# LABELS
# ==========================================

y = torch.tensor([0, 0, 1, 1, 0, 0])

# ==========================================
# DATA OBJECT
# ==========================================

data = Data(x=x, edge_index=edge_index, y=y)

# ==========================================
# MODEL
# ==========================================

model = AML_GNN(
    input_dim=3,
    hidden_dim=16,
    output_dim=2
)

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.01
)

# ==========================================
# TRAINING
# ==========================================

print("GNN Training Started...\n")

for epoch in range(50):

    model.train()

    optimizer.zero_grad()

    out = model(data)

    loss = torch.nn.functional.nll_loss(out, data.y)

    loss.backward()

    optimizer.step()

    if epoch % 5 == 0:

        print(f"Epoch {epoch} | Loss: {loss.item():.4f}")

print("\nGNN Training Completed")

# ==========================================
# SAVE CHECKPOINT
# ==========================================
torch.save(model.state_dict(), "models/gnn_checkpoint.pt")
print("GNN Model Checkpoint Saved at models/gnn_checkpoint.pt")