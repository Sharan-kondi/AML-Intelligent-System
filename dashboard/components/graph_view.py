import streamlit as st
import pandas as pd
import networkx as nx
import os
import json
import pyarrow.dataset as ds
from streamlit_agraph import agraph, Node, Edge, Config

# ---------------------------------------------------
# LOAD AML CASE DATA
# ---------------------------------------------------
@st.cache_data
def load_case_data():
    folder = "data/cases"
    rows = []
    if not os.path.exists(folder):
        return pd.DataFrame()
    for file in os.listdir(folder):
        if file.endswith(".json"):
            path = os.path.join(folder, file)
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    rows.append(data)
            except Exception:
                pass
    return pd.DataFrame(rows)

@st.cache_data
def load_fraud_results_cached():
    path = "data/processed/fraud_results.parquet"
    if os.path.exists(path):
        return pd.read_parquet(path)
    return pd.DataFrame()

# ---------------------------------------------------
# BUILD REAL TRANSACTIONS GRAPH
# ---------------------------------------------------
def build_real_graph(selected_account, fraud_df, max_edges=30):
    nodes = []
    edges = []
    G = nx.DiGraph()
    
    # Query real transactions involving the selected account
    parquet_path = "data/processed/final_transactions.parquet"
    if not os.path.exists(parquet_path):
        return nodes, edges, G
        
    try:
        dataset = ds.dataset(parquet_path, format="parquet")
        # Filter transactions
        table = dataset.to_table(
            filter=(ds.field("sender_id") == selected_account) | (ds.field("receiver_id") == selected_account),
            columns=["sender_id", "receiver_id", "amount", "timestamp"]
        )
        tx_df = table.to_pandas()
    except Exception as e:
        st.error(f"Error querying transactions: {str(e)}")
        return nodes, edges, G

    if tx_df.empty:
        return nodes, edges, G

    # Sort by amount to get most critical transactions first
    tx_df = tx_df.sort_values(by="amount", ascending=False).head(max_edges)
    
    added_nodes = set()
    
    # Pre-build list of unique nodes involved in the transactions
    unique_accounts = pd.concat([tx_df["sender_id"], tx_df["receiver_id"]]).unique()
    
    # Build dictionary of risk scores from fraud_df
    risk_dict = {}
    if not fraud_df.empty:
        # Create map of account_id -> risk_score and anomaly_score
        risk_subset = fraud_df[fraud_df["account_id"].isin(unique_accounts)]
        for _, row in risk_subset.iterrows():
            risk_dict[row["account_id"]] = {
                "risk_score": row.get("risk_score", 0),
                "anomaly_score": row.get("anomaly_score", 1),
                "degree": row.get("degree", 0),
                "pagerank": row.get("pagerank", 0.0)
            }

    # Add Selected Account Node
    selected_risk = risk_dict.get(selected_account, {"risk_score": 50, "anomaly_score": 1})
    selected_color = "#FF4B4B" if selected_risk["anomaly_score"] == -1 or selected_risk["risk_score"] >= 2 else "#3B82F6"
    
    nodes.append(
        Node(
            id=selected_account,
            label=f"★ {selected_account}",
            size=35,
            color="#FFD700" if selected_color == "#FF4B4B" else "#00FFCC", # Gold/Cyan highlight
            strokeColor="#FFFFFF",
            strokeWidth=2
        )
    )
    added_nodes.add(selected_account)
    G.add_node(selected_account, **selected_risk)

    # Process transactions to add nodes and edges
    for _, row in tx_df.iterrows():
        u = row["sender_id"]
        v = row["receiver_id"]
        amount = float(row["amount"])
        
        # Add sender node
        if u not in added_nodes:
            u_info = risk_dict.get(u, {"risk_score": 0, "anomaly_score": 1})
            u_color = "#FF4B4B" if u_info["anomaly_score"] == -1 else "#3B82F6"
            nodes.append(
                Node(
                    id=u,
                    label=u,
                    size=22,
                    color=u_color
                )
            )
            added_nodes.add(u)
            G.add_node(u, **u_info)
            
        # Add receiver node
        if v not in added_nodes:
            v_info = risk_dict.get(v, {"risk_score": 0, "anomaly_score": 1})
            v_color = "#FF4B4B" if v_info["anomaly_score"] == -1 else "#3B82F6"
            nodes.append(
                Node(
                    id=v,
                    label=v,
                    size=22,
                    color=v_color
                )
            )
            added_nodes.add(v)
            G.add_node(v, **v_info)
            
        # Add edge
        edges.append(
            Edge(
                source=u,
                target=v,
                label=f"₹{amount:,.0f}"
            )
        )
        G.add_edge(u, v, amount=amount, timestamp=str(row["timestamp"]))

    return nodes, edges, G

# ---------------------------------------------------
# SIDEBAR DETAILS
# ---------------------------------------------------
def show_sidebar(account, G):
    st.sidebar.markdown("# 🏦 Live AML Investigation")
    st.sidebar.success(f"Selected: {account}")
    
    # Calculate local metrics
    in_degree = G.in_degree(account) if G.has_node(account) else 0
    out_degree = G.out_degree(account) if G.has_node(account) else 0
    
    # Get node attributes
    node_data = G.nodes[account] if G.has_node(account) else {}
    risk_score = node_data.get("risk_score", 0)
    anomaly_score = node_data.get("anomaly_score", 1)
    pagerank = node_data.get("pagerank", 0.0)
    
    st.sidebar.metric(
        "AML Risk Level",
        f"HIGH (Flagged)" if anomaly_score == -1 else f"LOW/MEDIUM",
        delta=f"Risk Score: {risk_score}"
    )
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.sidebar.metric("Incoming Tx", in_degree)
    with col2:
        st.sidebar.metric("Outgoing Tx", out_degree)
        
    st.sidebar.metric("Centrality Rank (PageRank)", f"{pagerank:.6f}")
    
    st.sidebar.markdown("---")
    
    if anomaly_score == -1 or risk_score >= 2:
        st.sidebar.error("🚨 CRITICAL ALERT: Isolation Forest Flagged")
    else:
        st.sidebar.info("✅ Monitoring: Normal Transaction Profile")
        
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🔗 Connected Accounts")
    
    neighbors = list(G.successors(account)) + list(G.predecessors(account))
    neighbors = list(set(neighbors)) # Deduplicate
    
    for n in neighbors[:15]:
        st.sidebar.write(f"• {n}")
    if len(neighbors) > 15:
        st.sidebar.write(f"*... and {len(neighbors)-15} more*")

# ---------------------------------------------------
# MAIN GRAPH DASHBOARD
# ---------------------------------------------------
def render_graph_dashboard():
    st.markdown("## 🕸 Live AML Transaction Network")
    st.markdown("Visualizing real relationships and transaction flows from the parquet databases.")
    
    cases_df = load_case_data()
    fraud_df = load_fraud_results_cached()
    
    if fraud_df.empty:
        st.warning("Preprocessed fraud results not found. Please train models first.")
        return
        
    # Selected account dropdown from cases or flagged anomalies
    flagged_list = fraud_df[fraud_df["anomaly_score"] == -1]["account_id"].tolist()
    case_list = cases_df["account"].tolist() if not cases_df.empty else []
    
    # Merge lists
    combined_list = list(set(case_list + flagged_list))[:100] # Limit to 100 choices
    
    if not combined_list:
        combined_list = fraud_df["account_id"].head(50).tolist()
        
    selected_account = st.selectbox(
        "Select Suspicious Account to Visualize Network",
        options=combined_list
    )
    
    if selected_account:
        with st.spinner("Querying dataset and building local subgraph..."):
            nodes, edges, G = build_real_graph(selected_account, fraud_df)
            
        if not nodes:
            st.error("No transactions found for the selected account.")
            return
            
        # Draw agraph
        config = Config(
            width=900,
            height=600,
            directed=True,
            physics=True,
            hierarchical=False,
            nodeHighlightBehavior=True,
            highlightColor="#F7A7A6",
            collapsible=True,
            linkLength=180
        )
        
        st.markdown(f"### Subgraph for **{selected_account}** ({len(nodes)} nodes, {len(edges)} edges)")
        
        col_g, col_details = st.columns([3, 1])
        
        with col_g:
            selected_node = agraph(
                nodes=nodes,
                edges=edges,
                config=config
            )
        
        # Display side panel details
        show_sidebar(selected_account, G)
        
        # Display transaction data table
        st.markdown("### 📊 Transaction Details")
        records = []
        for u, v, d in G.edges(data=True):
            records.append({
                "Sender": u,
                "Receiver": v,
                "Amount (INR)": f"₹{d['amount']:,.2f}",
                "Timestamp": d.get("timestamp", "N/A")
            })
        
        if records:
            st.dataframe(pd.DataFrame(records), width='stretch')
        else:
            st.info("No transaction details found.")
            
        if selected_node and selected_node != selected_account:
            st.info(f"Double-click or search for **{selected_node}** in the selectbox above to pivot and visualize their transaction network.")