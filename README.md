<p align="center">
  <h1 align="center">🛡️ AML Intelligent System</h1>
  <p align="center">
    <strong>AI-Powered Anti-Money Laundering Detection & Investigation Platform</strong>
  </p>
  <p align="center">
    <a href="#features">Features</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#api-reference">API</a> •
    <a href="#testing">Testing</a> •
    <a href="#license">License</a>
  </p>
</p>

---

## 📋 Overview

**AML Intelligent System** is a comprehensive, production-grade Anti-Money Laundering platform that leverages **Graph Neural Networks (GNN)**, **multi-agent orchestration**, and **real-time stream processing** to detect, investigate, and report suspicious financial transactions.

The system combines cutting-edge deep learning on transaction graphs with an autonomous multi-agent pipeline — enabling financial institutions to move from reactive rule-based alerts to proactive, explainable, AI-driven compliance.

---

## ✨ Features

| Category | Capability |
|---|---|
| 🧠 **GNN-Based Detection** | Graph Neural Network built with PyTorch Geometric for transaction pattern recognition |
| 🤖 **Multi-Agent Pipeline** | Autonomous agents for risk scoring, investigation, compliance, and explainability — coordinated by an orchestrator |
| ⚡ **Real-Time Ingestion** | Apache Kafka producer for streaming transaction data |
| 🔄 **Batch Processing** | PySpark pipeline for large-scale historical transaction analysis |
| 📊 **Explainability** | SHAP explainer and natural-language reason generator for transparent, auditable decisions |
| 🔐 **Security** | JWT authentication, Role-Based Access Control (RBAC), and audit logging |
| 🖥️ **Dual Dashboard** | Streamlit analytics dashboard with rich components + custom HTML/JS/CSS operational frontend |
| 🧪 **Testing** | Pipeline test suite for end-to-end validation |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                           │
│   ┌──────────────────────┐     ┌──────────────────────────┐    │
│   │  Streamlit Dashboard │     │  Custom Web Dashboard    │    │
│   │  (dashboard/app.py)  │     │  (frontend/)             │    │
│   │  + Components Panel  │     │  HTML + CSS + JS         │    │
│   └──────────┬───────────┘     └────────────┬─────────────┘    │
└──────────────┼──────────────────────────────┼──────────────────┘
               │            ┌─────────────────┘
               ▼            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API Layer                               │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  FastAPI  (api/main.py)                                 │  │
│   │  Routes: alert_routes · transaction_routes · auth       │  │
│   └──────────────────────┬──────────────────────────────────┘  │
│                          │                                      │
│   ┌──────────────┐  ┌────┴──────────┐  ┌────────────────────┐  │
│   │  JWT Auth    │  │  Services     │  │  Schemas           │  │
│   │  (security/) │  │  (stream,etc) │  │  (api/schemas/)    │  │
│   └──────────────┘  └───────────────┘  └────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                     Intelligence Layer                           │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  AML Orchestrator (agents/aml_orchestrator.py)           │  │
│   │  ┌──────────┐  ┌───────────────┐  ┌─────────────────┐   │  │
│   │  │  Risk    │  │ Investigation │  │   Compliance    │   │  │
│   │  │  Agent   │→ │    Agent      │→ │     Agent       │   │  │
│   │  └──────────┘  └───────────────┘  └─────────────────┘   │  │
│   │                       ↓                                  │  │
│   │              ┌─────────────────┐                         │  │
│   │              │  Explanation    │                         │  │
│   │              │     Agent      │                         │  │
│   │              └─────────────────┘                         │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   ┌─────────────────────┐  ┌─────────────────────────────────┐  │
│   │  GNN Models         │  │  Explainability                 │  │
│   │  (models/)          │  │  SHAP + Reason Generator        │  │
│   │  PyTorch Geometric  │  │  (explainability/)              │  │
│   └─────────────────────┘  └─────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                       Data Layer                                 │
│                                                                  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│   │  Kafka       │  │  Spark       │  │  Graph Builder       │  │
│   │  Producer    │  │  Streaming   │  │  (graph/)            │  │
│   │  (ingestion/)│  │  (processing)│  │  NetworkX + PyVis    │  │
│   └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Preprocessing & Feature Engineering                     │  │
│   │  (preprocessing/)                                        │  │
│   └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
AML-Intelligent-System/
│
├── agents/                       # Multi-agent pipeline
│   ├── aml_orchestrator.py       # Agent coordination layer
│   ├── risk_agent.py             # Risk scoring agent
│   ├── investigation_agent.py    # Deep investigation engine
│   ├── compliance_agent.py       # Regulatory compliance checks
│   └── explanation_agent.py      # Explainability agent
│
├── api/                          # RESTful API (FastAPI)
│   ├── main.py                   # FastAPI application entry point
│   ├── routes/
│   │   ├── alert_routes.py       # Alert management endpoints
│   │   ├── transaction_routes.py # Transaction query endpoints
│   │   └── auth_routes.py        # Authentication endpoints
│   ├── schemas/
│   │   ├── request_schema.py     # Request validation models
│   │   └── response_schema.py    # Response serialization models
│   └── services/
│       ├── stream_service.py     # Real-time streaming service
│       ├── risk_service.py       # Risk assessment service
│       └── transaction_service.py# Transaction management service
│
├── config/                       # Configuration
│   ├── db_config.py              # Database settings
│   ├── kafka_config.py           # Kafka broker settings
│   └── spark_config.py           # Spark cluster settings
│
├── dashboard/                    # Streamlit Analytics Dashboard
│   ├── app.py                    # Main dashboard application
│   ├── assets/
│   │   ├── aml_logo.png          # Brand logo
│   │   └── styles.css            # Dashboard styling
│   └── components/
│       ├── agent_panel.py        # Agent status panel
│       ├── alert_table.py        # Alert management table
│       ├── fraud_graph.py        # Fraud network graph
│       ├── graph_view.py         # Interactive graph visualization
│       ├── investigation_panel.py# Investigation workflow
│       ├── metrics_cards.py      # KPI metric cards
│       ├── navbar.py             # Navigation bar
│       └── risk_charts.py        # Risk analytics charts
│
├── data/                         # Data storage (gitignored)
│   ├── raw/                      # Raw datasets (Elliptic, KYC, synthetic)
│   ├── processed/                # Processed parquet files & graph
│   ├── cases/                    # Investigation case results (JSON)
│   └── streaming/                # Real-time stream buffer
│
├── explainability/               # Model interpretability
│   ├── shap_explainer.py         # SHAP-based feature importance
│   └── reason_generator.py       # Natural language explanations
│
├── frontend/                     # Custom Web Dashboard
│   ├── index.html                # Single-page application
│   ├── css/styles.css            # Dark-themed UI styling
│   └── js/app.js                 # Dashboard logic & API integration
│
├── graph/                        # Graph construction & analysis
│   ├── graph_builder.py          # NetworkX transaction graph builder
│   ├── graph_features.py         # Graph-based feature extraction
│   ├── graph_metrics.py          # Network analysis metrics
│   ├── graph_visualization.py    # Static graph visualization
│   └── realtime_graph.py         # Live graph updates
│
├── ingestion/                    # Data ingestion
│   ├── kafka_producer.py         # Transaction event producer
│   └── data_loader.py           # Data loading utilities
│
├── lib/                          # Vendored JS libraries
│   ├── vis-9.1.2/                # vis-network for graph rendering
│   ├── tom-select/               # Tom Select dropdowns
│   └── bindings/                 # JS utility bindings
│
├── models/                       # Machine learning models
│   ├── gnn_model.py              # GNN architecture definition
│   ├── realtime_gnn.py           # Real-time GNN inference
│   ├── train.py                  # Training pipeline
│   ├── baseline_model.py         # Baseline comparison model
│   ├── fraud_ring_detector.py    # Fraud ring detection
│   └── risk_scoring.py           # Risk score computation
│
├── preprocessing/                # Data preprocessing
│   ├── data_preprocessing.py     # Data cleaning & transformation
│   ├── data_cleaning.py          # Raw data cleaning
│   └── data_merging.py           # Multi-source data merging
│
├── processing/                   # Stream & batch processing
│   ├── spark_stream.py           # PySpark streaming pipeline
│   ├── spark_batch.py            # Batch processing jobs
│   └── feature_engineering.py    # Feature computation
│
├── security/                     # Security layer
│   ├── auth.py                   # JWT authentication
│   ├── rbac.py                   # Role-Based Access Control
│   ├── audit_logs.py             # Audit trail logging
│   └── encryption.py             # Data encryption utilities
│
├── tests/                        # Test suite
│   └── test_pipeline.py          # End-to-end pipeline tests
│
├── utils/                        # Utility functions
│   ├── alert_prioritizer.py      # Alert priority scoring
│   ├── case_manager.py           # Case lifecycle management
│   ├── helpers.py                # General helpers
│   └── logger.py                 # Logging configuration
│
├── paper.tex                     # Research paper (LaTeX)
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Container orchestration
├── LICENSE                       # MIT License
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.9+
- **Apache Kafka** (for real-time ingestion)
- **Apache Spark** (for batch/stream processing)
- **Docker & Docker Compose** (optional, for containerized deployment)

### 1. Clone the Repository

```bash
git clone https://github.com/Sharan-kondi/AML-Intelligent-System.git
cd AML-Intelligent-System
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare Data

Place your datasets in the `data/` directory:

```
data/
├── raw/
│   ├── elliptic/          # Elliptic Bitcoin dataset
│   ├── fraud_detection/   # Fraud detection dataset
│   ├── kyc/               # KYC dataset
│   └── synthetic/         # Synthetic transaction data
└── processed/             # Auto-generated by preprocessing
```

### 5. Run the API Server

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Launch the Dashboard

```bash
# Streamlit Dashboard
streamlit run dashboard/app.py

# Or serve the custom frontend
cd frontend && python -m http.server 3000
```

---

## 📡 API Reference

Base URL: `http://localhost:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/token` | Authenticate and receive JWT token |
| `GET` | `/transactions` | List transactions with filtering |
| `GET` | `/alerts` | Retrieve active alerts |
| `POST` | `/alerts/investigate` | Trigger investigation on a flagged alert |
| `GET` | `/stream/status` | Real-time stream status |

### Authentication

All protected endpoints require a valid JWT bearer token:

```bash
# Get token
curl -X POST http://localhost:8000/auth/token \
  -d "username=admin&password=admin"

# Use token
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/transactions
```

---

## 🧠 Model Details

### Graph Neural Network

The core detection model is a **GNN** built with PyTorch Geometric:

- **Architecture**: Graph convolutional layers for transaction network analysis
- **Input**: Transaction graph with node features (amount, frequency, velocity, time patterns)
- **Output**: Binary classification (legitimate vs. suspicious) with confidence scores
- **Real-Time**: `realtime_gnn.py` enables live inference on streaming data
- **Explainability**: Integrated SHAP explanations + natural language reason generation

### Feature Engineering

The system extracts rich features from raw transactions:

| Feature Group | Examples |
|---|---|
| **Velocity** | Transaction frequency per time window |
| **Amount Statistics** | Mean, std, min, max per account |
| **Temporal Patterns** | Hour-of-day, day-of-week distributions |
| **Network Features** | In/out degree, clustering coefficient, PageRank |
| **Graph Metrics** | Community detection, centrality scores |

---

## 🤖 Agent Pipeline

The multi-agent system processes transactions through an automated pipeline:

```
Transaction → Risk Agent → Investigation Agent → Compliance Agent → Explanation Agent → Report
```

1. **Risk Agent** — Computes risk scores for incoming transactions
2. **Investigation Agent** — Performs deep analysis on flagged transactions, examines network patterns
3. **Compliance Agent** — Validates findings against regulatory requirements
4. **Explanation Agent** — Generates human-readable explanations for decisions
5. **AML Orchestrator** — Coordinates agent execution, manages pipeline flow

Case results are automatically saved to `data/cases/` as structured JSON files for audit trails.

---

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=. --cov-report=html
```

---

## 🔐 Security

- **JWT Authentication** with configurable token expiration
- **Role-Based Access Control (RBAC)** with granular permissions
- **Audit Logging** for all data access and operations
- **Data Anonymization** — All account identifiers are SHA-256 hashed
- **Input Validation** via Pydantic schemas

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **ML / DL** | PyTorch, PyTorch Geometric, scikit-learn |
| **Explainability** | SHAP, Custom Reason Generator |
| **Graph** | NetworkX, PyVis, vis-network |
| **API** | FastAPI, Uvicorn |
| **Auth** | python-jose (JWT), passlib (bcrypt) |
| **Stream Processing** | Apache Kafka (kafka-python) |
| **Batch Processing** | Apache Spark (PySpark) |
| **Dashboard** | Streamlit, Plotly, Matplotlib |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Data** | Pandas, NumPy, PyArrow, Parquet |
| **Containerization** | Docker, Docker Compose |

---

## 📄 Research Paper

This project includes a LaTeX research paper (`paper.tex`) documenting the methodology, architecture, and experimental results of the AML Intelligent System.

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/Sharan-kondi">Sharan Kondi</a>
</p>
