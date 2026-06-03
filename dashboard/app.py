import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import random
import os
import json
import time
import pickle
import networkx as nx
import torch

# Import custom components & helpers
from dashboard.components.graph_view import render_graph_dashboard, load_case_data, load_fraud_results_cached
from explainability.shap_explainer import AMLShapExplainer
from explainability.reason_generator import ReasonGenerator
from models.gnn_model import AML_GNN
from models.risk_scoring import AMLRiskScorer
from models.fraud_ring_detector import FraudRingDetector
from agents.aml_orchestrator import AMLOrchestrator
from utils.alert_prioritizer import AlertPrioritizer
from utils.case_manager import AMLCaseManager

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Enterprise AML Intelligence System",
    page_icon="🏦",
    layout="wide"
)

# Auto refresh every 30 seconds for live network and cases
st_autorefresh(interval=30000, key="refresh")

# ---------------------------------------------------
# CURATED STYLE SYSTEM (VANILLA CSS)
# ---------------------------------------------------
st.markdown("""
<style>
/* Theme colors and background */
.main {
    background-color: #0f172a;
    color: #e2e8f0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
[data-testid="stSidebar"] {
    background-color: #090d16;
    border-right: 1px solid #1e293b;
}

/* Card layout & Glassmorphism */
div.metric-container, div.card {
    background: rgba(30, 41, 59, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s ease, border-color 0.2s ease;
    margin-bottom: 16px;
}
div.metric-container:hover, div.card:hover {
    transform: translateY(-2px);
    border-color: rgba(59, 130, 246, 0.4);
}

/* Titles and Headers */
h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}
.main-title {
    background: linear-gradient(135deg, #3b82f6 0%, #00ffcc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem;
    margin-bottom: 0.2rem;
}
.subtitle {
    color: #94a3b8;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}

/* Custom Alert Boxes */
.agent-box {
    background: rgba(15, 23, 42, 0.6);
    border-left: 4px solid #3b82f6;
    padding: 16px;
    border-radius: 0 12px 12px 0;
    margin-bottom: 12px;
}
.agent-header {
    font-weight: bold;
    color: #3b82f6;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Status colors */
.badge-critical { background-color: #ef4444; color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: bold; }
.badge-high { background-color: #f97316; color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: bold; }
.badge-medium { background-color: #eab308; color: black; padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: bold; }
.badge-low { background-color: #22c55e; color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: bold; }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# MODEL & DATA CACHING
# ---------------------------------------------------
@st.cache_resource
def load_transaction_graph_cached():
    path = "data/processed/transaction_graph.pkl"
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception:
            pass
    return nx.Graph()

@st.cache_resource
def get_shap_explainer_cached():
    from sklearn.ensemble import IsolationForest
    fraud_df = load_fraud_results_cached()
    if fraud_df.empty:
        return None
    X = fraud_df[["degree", "pagerank"]]
    # Recreate the Isolation Forest matching models/baseline_model.py
    model = IsolationForest(
        n_estimators=100,
        contamination=0.02,
        random_state=42
    )
    model.fit(X)
    # Background dataset sample
    background = X.sample(min(200, len(X)), random_state=42)
    return AMLShapExplainer(model, background)

@st.cache_resource
def load_gnn_model_cached():
    model = AML_GNN(input_dim=3, hidden_dim=16, output_dim=2)
    checkpoint_path = "models/gnn_checkpoint.pt"
    if os.path.exists(checkpoint_path):
        try:
            model.load_state_dict(torch.load(checkpoint_path, map_location=torch.device('cpu')))
            st.toast("🧠 Loaded GNN model from checkpoint!", icon="✅")
        except Exception as e:
            st.error(f"Error loading GNN checkpoint: {str(e)}")
    model.eval()
    return model

# Load resources
fraud_df = load_fraud_results_cached()
cases_df = load_case_data()

# ---------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------
with st.sidebar:
    st.image("dashboard/assets/aml_logo.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center; color: #00ffcc; margin-top: 0;'>AML Control Center</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    selected = option_menu(
        menu_title="Intelligence Portal",
        options=[
            "Overview",
            "Live AML Network",
            "Fraud Detection",
            "Fraud Rings",
            "GNN Intelligence",
            "Investigation Center",
            "Explainable AI",
            "Compliance",
            "System Analytics"
        ],
        icons=[
            "speedometer2",
            "diagram-3",
            "shield-fill-exclamation",
            "radioactive",
            "cpu",
            "search",
            "graph-up",
            "file-earmark-check",
            "bar-chart"
        ],
        default_index=0,
        styles={
            "container": {"background-color": "#090d16"},
            "nav-link": {"color": "#94a3b8", "font-size": "14px", "text-align": "left", "margin":"5px", "--hover-color": "#1e293b"},
            "nav-link-selected": {"background-color": "#3b82f6", "color": "white", "font-weight": "bold"}
        }
    )

# ---------------------------------------------------
# APPLICATION HEADER
# ---------------------------------------------------
st.markdown('<div class="main-title">🏦 Enterprise AML Surveillance Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Real-time GNN Inference + XAI Explanations + Multi-Agent Control Center</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# PAGE ROUTING & LOGIC
# ---------------------------------------------------

# 1. OVERVIEW PAGE
if selected == "Overview":
    if fraud_df.empty:
        st.warning("No preprocessed dataset loaded. Please train the baseline model.")
    else:
        # Calculate dynamic metrics
        total_accounts = len(fraud_df)
        total_anomalies = len(fraud_df[fraud_df["anomaly_score"] == -1])
        avg_degree = fraud_df["degree"].mean()
        total_cases = len(cases_df) if not cases_df.empty else 0
        anomaly_rate = (total_anomalies / total_accounts) * 100
        
        # Grid layout for metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <p style="color:#94a3b8; margin:0; font-size:0.9rem;">Monitored Accounts</p>
                <h2 style="margin:5px 0 0 0; color:white; font-size:2rem;">{total_accounts:,}</h2>
                <span style="color:#3b82f6; font-size:0.8rem;">Active Transactions Network</span>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <p style="color:#94a3b8; margin:0; font-size:0.9rem;">Flagged Anomalies</p>
                <h2 style="margin:5px 0 0 0; color:#ef4444; font-size:2rem;">{total_anomalies:,}</h2>
                <span style="color:#ef4444; font-size:0.8rem;">IForest Score Outliers ({anomaly_rate:.2f}%)</span>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <p style="color:#94a3b8; margin:0; font-size:0.9rem;">Avg Network Connections</p>
                <h2 style="margin:5px 0 0 0; color:#00ffcc; font-size:2rem;">{avg_degree:.1f}</h2>
                <span style="color:#00ffcc; font-size:0.8rem;">Average Degree Centrality</span>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
            <div class="metric-container">
                <p style="color:#94a3b8; margin:0; font-size:0.9rem;">Investigated Cases</p>
                <h2 style="margin:5px 0 0 0; color:#eab308; font-size:2rem;">{total_cases}</h2>
                <span style="color:#eab308; font-size:0.8rem;">Multi-Agent Reports Generated</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 📈 Network Topology Analysis")
        
        c1, c2 = st.columns(2)
        
        with c1:
            # Degree distribution chart (interactive log-scale)
            fig_degree = px.histogram(
                fraud_df,
                x="degree",
                nbins=50,
                log_y=True,
                title="Account Degree Distribution (Log Scale)",
                color_discrete_sequence=["#3b82f6"]
            )
            fig_degree.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="#e2e8f0",
                xaxis_title="Degrees (Connections Count)",
                yaxis_title="Count of Accounts"
            )
            st.plotly_chart(fig_degree, width='stretch')
            
        with c2:
            # Pagerank vs degree colored by anomalies
            fig_scatter = px.scatter(
                fraud_df.sample(min(2000, len(fraud_df))),
                x="degree",
                y="pagerank",
                color=fraud_df.sample(min(2000, len(fraud_df)))["anomaly_score"].astype(str),
                color_discrete_map={"1": "#3b82f6", "-1": "#ef4444"},
                title="Degree vs PageRank Centrality (Flagged Outliers in Red)",
                labels={"color": "Anomaly State (-1 = Outlier)"}
            )
            fig_scatter.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="#e2e8f0"
            )
            st.plotly_chart(fig_scatter, width='stretch')

# 2. LIVE AML NETWORK PAGE
elif selected == "Live AML Network":
    render_graph_dashboard()

# 3. FRAUD DETECTION PAGE
elif selected == "Fraud Detection":
    st.markdown("### 🚨 Outlier Accounts Detected via Isolation Forest")
    st.markdown("Accounts flagged below show transaction patterns that deviate significantly from baseline distributions.")
    
    if fraud_df.empty:
        st.warning("Data not available.")
    else:
        anomalies_df = fraud_df[fraud_df["anomaly_score"] == -1].copy()
        
        # Sort by risk score
        anomalies_df = anomalies_df.sort_values(by="risk_score", ascending=False)
        
        # Quick metrics comparison
        avg_normal_deg = fraud_df[fraud_df["anomaly_score"] == 1]["degree"].mean()
        avg_anomaly_deg = anomalies_df["degree"].mean()
        
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Avg Degree of Suspicious Accounts", f"{avg_anomaly_deg:.1f} connections", delta=f"{avg_anomaly_deg - avg_normal_deg:.1f} vs Normal")
        with m2:
            st.metric("Highest Degree Node Flagged", f"{anomalies_df['degree'].max()} connections")
            
        st.markdown("#### Search Anomalies Database")
        
        search_query = st.text_input("Enter Account ID to filter (e.g. ACC041606):")
        if search_query:
            filtered_anomalies = anomalies_df[anomalies_df["account_id"].str.contains(search_query, case=False)]
        else:
            filtered_anomalies = anomalies_df
            
        # Paginate results
        st.dataframe(
            filtered_anomalies[["account_id", "degree", "pagerank", "risk_score"]],
            column_config={
                "account_id": "Account ID",
                "degree": st.column_config.NumberColumn("Degree Centrality", help="Number of connections"),
                "pagerank": st.column_config.NumberColumn("PageRank", format="%.6f"),
                "risk_score": st.column_config.ProgressColumn("Base Risk Score", min_value=0, max_value=2, format="%d")
            },
            width='stretch'
        )

# 4. FRAUD RINGS PAGE
elif selected == "Fraud Rings":
    st.markdown("### 🕸️ Fraud Ring Detection Center")
    st.markdown("Runs NetworkX Connected Components analysis to find clusters of risk nodes operating together.")
    
    with st.spinner("Loading transaction graph and mapping components..."):
        G_large = load_transaction_graph_cached()
        
    if len(G_large) == 0:
        st.info("Large graph index not loaded. Rendering synthetic detected components.")
        # Fallback to simulated rings from data cases
        if not cases_df.empty:
            rings_data = cases_df[cases_df["fraud_ring_count"] > 0]
            st.error(f"Detected {len(rings_data)} distinct structural risk clusters:")
            for idx, row in rings_data.head(5).iterrows():
                st.markdown(f"""
                <div class="card">
                    <h5 style='color:#ef4444;margin:0 0 10px 0;'>🚨 Risk Cluster around {row['account']}</h5>
                    <p style='margin:0;'>Contains {row['fraud_ring_count']} connected accounts. Risk Score: <b>{row['risk_score']}%</b></p>
                </div>
                """, unsafe_allow_html=True)
    else:
        # Run actual component detection
        detector = FraudRingDetector(G_large)
        rings = detector.detect_fraud_rings()
        
        st.success(f"Analysed full transaction network. Detected **{len(rings)}** multi-party fraud rings (components with size $\ge 3$).")
        
        for idx, ring in enumerate(rings[:10]):
            members_list = list(ring)
            st.markdown(f"""
            <div class="card">
                <h5 style='color:#ef4444;margin:0 0 10px 0;'>🚨 Fraud Ring {idx+1} (Size: {len(members_list)} Accounts)</h5>
                <p style='margin:0 0 10px 0;'><b>Members:</b> {', '.join(members_list[:10])} {'...' if len(members_list) > 10 else ''}</p>
            </div>
            """, unsafe_allow_html=True)

# 5. GNN INTELLIGENCE PAGE
elif selected == "GNN Intelligence":
    st.markdown("### 🧠 PyTorch Graph Neural Network (GNN) Engine")
    st.markdown("Uses custom Graph Convolutional Networks (GCN) to classify nodes dynamically based on features and structural topology.")
    
    # Load cached GNN model
    gnn_model = load_gnn_model_cached()
    
    # Render beautiful visual GNN Architecture
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.35); border: 1px solid rgba(255,255,255,0.08); padding: 30px; border-radius: 20px; display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 20px; text-align: center; margin-bottom: 30px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); backdrop-filter: blur(8px);">
      <!-- Input Features Node -->
      <div style="flex: 1; min-width: 160px; z-index: 2;">
        <div style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); padding: 15px 20px; border-radius: 12px; box-shadow: 0 0 20px rgba(59, 130, 246, 0.35); border: 1px solid rgba(255,255,255,0.1);">
          <h5 style="margin: 0; color: white; font-size: 0.95rem;">Input Features</h5>
          <p style="margin: 5px 0 0 0; font-size: 0.75rem; color: #94a3b8; font-weight: normal; line-height: 1.2;">X ∈ ℝ<sup>N x 3</sup><br>(Degree, PageRank, Clustering)</p>
        </div>
      </div>
      
      <div style="color: #3b82f6; font-size: 1.8rem; font-weight: bold; padding: 0 5px;">➔</div>
      
      <!-- GCNConv 1 Node -->
      <div style="flex: 1; min-width: 160px; z-index: 2;">
        <div style="background: linear-gradient(135deg, #8b5cf6, #6d28d9); padding: 15px 20px; border-radius: 12px; box-shadow: 0 0 20px rgba(139, 92, 246, 0.35); border: 1px solid rgba(255,255,255,0.1);">
          <h5 style="margin: 0; color: white; font-size: 0.95rem;">GCNConv Layer 1</h5>
          <p style="margin: 5px 0 0 0; font-size: 0.75rem; color: #d8b4fe; font-weight: normal; line-height: 1.2;">3 ➔ 16 Hidden units<br>Aggregation + Linear</p>
        </div>
        <div style="margin-top: 10px; font-size: 0.7rem; color: #a78bfa; background: rgba(139, 92, 246, 0.15); padding: 3px 10px; border-radius: 20px; display: inline-block; font-weight: bold; border: 1px solid rgba(139,92,246,0.3);">ReLU Activation</div>
      </div>
      
      <div style="color: #8b5cf6; font-size: 1.8rem; font-weight: bold; padding: 0 5px;">➔</div>

      <!-- GCNConv 2 Node -->
      <div style="flex: 1; min-width: 160px; z-index: 2;">
        <div style="background: linear-gradient(135deg, #ec4899, #be185d); padding: 15px 20px; border-radius: 12px; box-shadow: 0 0 20px rgba(236, 72, 153, 0.35); border: 1px solid rgba(255,255,255,0.1);">
          <h5 style="margin: 0; color: white; font-size: 0.95rem;">GCNConv Layer 2</h5>
          <p style="margin: 5px 0 0 0; font-size: 0.75rem; color: #fbcfe8; font-weight: normal; line-height: 1.2;">16 ➔ 2 Output classes<br>Log Softmax</p>
        </div>
        <div style="margin-top: 10px; font-size: 0.7rem; color: #f472b6; background: rgba(236, 72, 153, 0.15); padding: 3px 10px; border-radius: 20px; display: inline-block; font-weight: bold; border: 1px solid rgba(236,72,153,0.3);">Loss Prediction</div>
      </div>
      
      <div style="color: #ec4899; font-size: 1.8rem; font-weight: bold; padding: 0 5px;">➔</div>

      <!-- Classification Node -->
      <div style="flex: 1; min-width: 160px; z-index: 2;">
        <div style="background: linear-gradient(135deg, #10b981, #047857); padding: 15px 20px; border-radius: 12px; box-shadow: 0 0 20px rgba(16, 185, 129, 0.35); border: 1px solid rgba(255,255,255,0.1);">
          <h5 style="margin: 0; color: white; font-size: 0.95rem;">Fraud Risk Output</h5>
          <p style="margin: 5px 0 0 0; font-size: 0.75rem; color: #a7f3d0; font-weight: normal; line-height: 1.2;">Binary Class Probabilities<br>Normal / Suspicious</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### PyTorch Geometric Implementation Definition")
    st.code(str(gnn_model), language="python")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card">
            <h4 style="margin-top:0;">GNN Node Classification Flow</h4>
            <ol style="margin-bottom:0;">
                <li><b>Message Passing</b>: Aggregates features (degree, pagerank) of adjacent nodes.</li>
                <li><b>GCNConv Layers</b>: Two-layer convolution transforms node embeddings.</li>
                <li><b>Log Softmax</b>: Predicts binary fraud probability (0 = Normal, 1 = Suspicious).</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        # Show GNN parameters
        total_params = sum(p.numel() for p in gnn_model.parameters())
        st.markdown(f"""
        <div class="card">
            <h4 style="margin-top:0;">Model Properties</h4>
            <ul style="margin-bottom:0;">
                <li>Input Dimensions: 3 (Features)</li>
                <li>Hidden Layers: 16 Dimensions</li>
                <li>Output Classes: 2 (Binary Prediction)</li>
                <li>Total Learnable Parameters: {total_params}</li>
                <li>Deployment Device: {"CUDA (GPU)" if torch.cuda.is_available() else "CPU"}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# 6. INVESTIGATION CENTER PAGE
elif selected == "Investigation Center":
    st.markdown("### 🕵️ Dynamic AML Investigation Center")
    st.markdown("Select a suspicious account to coordinate the multi-agent decision support system.")
    
    if fraud_df.empty:
        st.warning("Data not available.")
    else:
        # Accounts to select from
        flagged_list = fraud_df[fraud_df["anomaly_score"] == -1]["account_id"].tolist()[:100]
        selected_node = st.selectbox("Select Account ID for Investigation:", options=flagged_list)
        
        if selected_node:
            node_row = fraud_df[fraud_df["account_id"] == selected_node].iloc[0]
            
            degree = int(node_row["degree"])
            pagerank = float(node_row["pagerank"])
            anomaly_score = int(node_row["anomaly_score"])
            base_risk = float(node_row["risk_score"])
            
            # Setup networkx graph for local calculations
            G_local = nx.Graph()
            G_local.add_node(selected_node)
            for i in range(degree):
                G_local.add_edge(selected_node, f"CONN_ACC_{i}")
                
            # Live calculate AML Risk Score using scorer
            scorer = AMLRiskScorer(G_local)
            risk_score = scorer.calculate_risk_score(
                node=selected_node,
                transaction_amount=random.randint(50000, 250000) if base_risk > 0 else random.randint(1000, 20000),
                suspicious_prediction=(anomaly_score == -1)
            )
            
            # Live generate reasons
            generator = ReasonGenerator(G_local)
            reasons = generator.generate_reason(
                node=selected_node,
                transaction_amount=150000 if anomaly_score == -1 else 10000,
                suspicious_prediction=(anomaly_score == -1)
            )
            
            # Run Agent Orchestrator Pipeline
            orchestrator = AMLOrchestrator()
            agent_results = orchestrator.process_case(
                node=selected_node,
                risk_score=risk_score,
                suspicious=(anomaly_score == -1),
                explanations=reasons,
                fraud_rings=[1] if risk_score > 75 else []
            )
            
            # Get Alert Priority level
            prioritizer = AlertPrioritizer()
            priority_level = prioritizer.prioritize(
                risk_score=risk_score,
                suspicious=(anomaly_score == -1),
                fraud_ring_count=1 if risk_score > 75 else 0
            )
            
            # Priority badge styling
            badge_class = "badge-low"
            if priority_level == "CRITICAL": badge_class = "badge-critical"
            elif priority_level == "HIGH": badge_class = "badge-high"
            elif priority_level == "MEDIUM": badge_class = "badge-medium"
            
            # Rendering dashboard elements
            c_left, c_right = st.columns([1, 2])
            
            with c_left:
                st.markdown(f"""
                <div class="card">
                    <h4>Account Dossier</h4>
                    <p><b>ID:</b> {selected_node}</p>
                    <p><b>Risk Priority:</b> <span class="{badge_class}">{priority_level}</span></p>
                    <p><b>Total Risk Index:</b> {risk_score}%</p>
                    <p><b>Network Degree:</b> {degree} connections</p>
                    <p><b>PageRank Score:</b> {pagerank:.6f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Case management controls
                st.markdown("#### Case Resolution Action")
                case_action = st.radio("Select investigation verdict:", ["Hold (Under Review)", "Escalate to FIU", "Dismiss (False Positive)"])
                if st.button("Submit Decision"):
                    # Save Case using dynamic Case Manager
                    manager = AMLCaseManager()
                    saved_path = manager.save_case(
                        node=selected_node,
                        risk_score=risk_score,
                        suspicious=(anomaly_score == -1),
                        explanations=reasons,
                        fraud_rings=[1] if risk_score > 75 else []
                    )
                    st.success(f"Case details locked! Report saved successfully.")
                    
            with c_right:
                st.markdown("### 🤖 Multi-Agent Orchestration Logs")
                
                # Render Risk Agent
                st.markdown(f"""
                <div class="agent-box" style="border-left-color: #ef4444;">
                    <div class="agent-header" style="color: #ef4444;">
                        <span>🚨 Risk Assessment Agent</span>
                    </div>
                    <p>{agent_results['risk_analysis']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Render XAI Agent
                st.markdown(f"""
                <div class="agent-box" style="border-left-color: #eab308;">
                    <div class="agent-header" style="color: #eab308;">
                        <span>📈 Explainability Agent (XAI)</span>
                    </div>
                    <p>{agent_results['explanation'].replace(chr(10), '<br>')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Render Case Summary Agent
                st.markdown(f"""
                <div class="agent-box" style="border-left-color: #00ffcc;">
                    <div class="agent-header" style="color: #00ffcc;">
                        <span>🕵️ Investigation Summary Agent</span>
                    </div>
                    <p>{agent_results['investigation'].replace(chr(10), '<br>')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Render Compliance Agent
                st.markdown(f"""
                <div class="agent-box" style="border-left-color: #3b82f6;">
                    <div class="agent-header" style="color: #3b82f6;">
                        <span>📋 Compliance Auditor Agent</span>
                    </div>
                    <p>{agent_results['compliance'].replace(chr(10), '<br>')}</p>
                </div>
                """, unsafe_allow_html=True)

# 7. EXPLAINABLE AI PAGE
elif selected == "Explainable AI":
    st.markdown("### 📈 Explainable AI: SHAP Explanations")
    st.markdown("SHAP (SHapley Additive exPlanations) values break down the contribution of network features to the Isolation Forest model output.")
    
    explainer = get_shap_explainer_cached()
    
    if explainer is None:
        st.warning("SHAP Explainer model not available. Make sure datasets exist.")
    else:
        flagged_list = fraud_df[fraud_df["anomaly_score"] == -1]["account_id"].tolist()[:100]
        selected_node = st.selectbox("Select Account ID to Explain:", options=flagged_list)
        
        if selected_node:
            node_row = fraud_df[fraud_df["account_id"] == selected_node].iloc[0]
            deg = float(node_row["degree"])
            pr = float(node_row["pagerank"])
            
            # Get SHAP values
            explanation = explainer.explain(deg, pr)
            
            # Show stats
            st.markdown(f"#### Local Feature Contributions for **{selected_node}**")
            
            # Plot contributions
            contrib_df = pd.DataFrame({
                "Feature": ["Degree Centrality", "PageRank Influence"],
                "SHAP Value (Contribution)": [explanation["degree_contribution"], explanation["pagerank_contribution"]]
            })
            
            # Color code: Positive values mean pushing towards anomaly, negative means towards normal
            contrib_df["Direction"] = np.where(contrib_df["SHAP Value (Contribution)"] > 0, "Suspicious Bias", "Normalizing Bias")
            
            fig = px.bar(
                contrib_df,
                x="SHAP Value (Contribution)",
                y="Feature",
                color="Direction",
                orientation="h",
                color_discrete_map={"Suspicious Bias": "#ef4444", "Normalizing Bias": "#3b82f6"},
                title="SHAP Value Contribution Plot"
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="#e2e8f0"
            )
            st.plotly_chart(fig, width='stretch')
            
            # Interpretations
            st.markdown("#### Scientific Interpretation")
            if explanation["degree_contribution"] > 0:
                st.info(f"👉 **Degree Centrality** has a positive SHAP value ({explanation['degree_contribution']:.4f}). This indicates the high number of connected counterparties is raising suspicion.")
            else:
                st.info(f"👉 **Degree Centrality** has a negative SHAP value ({explanation['degree_contribution']:.4f}), meaning the account connectivity falls within typical distributions.")
                
            if explanation["pagerank_contribution"] > 0:
                st.info(f"👉 **PageRank Influence** score ({explanation['pagerank_contribution']:.4f}) indicates this node lies in a critical structural flow segment of the transaction network, increasing its risk weighting.")
            else:
                st.info(f"👉 **PageRank Influence** score ({explanation['pagerank_contribution']:.4f}) does not indicate significant transaction routing concentration.")

# 8. COMPLIANCE PAGE
elif selected == "Compliance":
    st.markdown("### 📋 Regulatory Compliance & Auditing")
    st.markdown("Archived logs and case dossiers verified by the Compliance Auditor agent.")
    
    if cases_df.empty:
        st.info("No cases archived yet. Go to 'Investigation Center' to run agents and save files.")
    else:
        st.markdown(f"Total Archived Audits: **{len(cases_df)}**")
        
        # Search compliance database
        search_comp = st.text_input("Search audit logs by Account ID:")
        if search_comp:
            display_cases = cases_df[cases_df["account"].str.contains(search_comp, case=False)]
        else:
            display_cases = cases_df
            
        st.dataframe(
            display_cases,
            column_config={
                "account": "Account ID",
                "risk_score": "Verified Risk Score (%)",
                "suspicious": "Anomaly Flag",
                "explanations": "Auditor Indicators",
                "fraud_ring_count": "Connected Ring Size",
                "timestamp": "Audit Timestamp"
            },
            width='stretch'
        )

# 9. SYSTEM ANALYTICS PAGE
elif selected == "System Analytics":
    st.markdown("### 📡 Model Execution Latency Benchmark")
    st.markdown("Measuring live performance metrics and response times of the local models and orchestrator agents.")
    
    # Benchmarking live
    start = time.time()
    # 1. Pyarrow load sample
    t0 = time.time()
    fraud_df.head(100)
    dur_data = (time.time() - t0) * 1000
    
    # 2. Isolation Forest Inference
    t0 = time.time()
    explainer = get_shap_explainer_cached()
    if explainer:
        explainer.model.predict([[5, 0.0001]])
    dur_ml = (time.time() - t0) * 1000
    
    # 3. GNN Prediction Run
    t0 = time.time()
    gnn_model = load_gnn_model_cached()
    # Create dummy PYG Data object
    x = torch.rand((2, 3))
    edge_index = torch.tensor([[0, 1], [1, 0]], dtype=torch.long)
    from torch_geometric.data import Data
    data = Data(x=x, edge_index=edge_index)
    gnn_model(data)
    dur_gnn = (time.time() - t0) * 1000
    
    # 4. Multi-agent Orchestration
    t0 = time.time()
    orchestrator = AMLOrchestrator()
    orchestrator.process_case(
        node="TEST", risk_score=50, suspicious=False, explanations=["TEST"], fraud_rings=[]
    )
    dur_agents = (time.time() - t0) * 1000
    
    # 5. SHAP values calculation
    t0 = time.time()
    if explainer:
        explainer.explain(5, 0.0001)
    dur_shap = (time.time() - t0) * 1000
    
    metrics_list = [
        {"Component": "PyArrow Data Query", "Latency (ms)": dur_data},
        {"Component": "Isolation Forest Inference", "Latency (ms)": dur_ml},
        {"Component": "Graph Neural Network Prediction", "Latency (ms)": dur_gnn},
        {"Component": "Multi-Agent Decision Execution", "Latency (ms)": dur_agents},
        {"Component": "SHAP Values Computation", "Latency (ms)": dur_shap}
    ]
    
    df_perf = pd.DataFrame(metrics_list)
    
    fig = px.bar(
        df_perf,
        x="Latency (ms)",
        y="Component",
        orientation="h",
        color="Latency (ms)",
        color_continuous_scale="Viridis",
        title="AML Inference Pipeline Benchmarks"
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#e2e8f0"
    )
    st.plotly_chart(fig, width='stretch')
    
    # Summary of stats
    st.markdown("#### System Performance Insights")
    st.info(f"⚡ Total pipeline execution latency: **{dur_data + dur_ml + dur_gnn + dur_agents + dur_shap:.2f} ms**")