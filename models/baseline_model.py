# models/baseline_model.py

import pandas as pd
from sklearn.ensemble import IsolationForest

# -------------------------------
# PATHS
# -------------------------------
DATA_PATH = "data/processed/graph_features.parquet"
OUTPUT_PATH = "data/processed/fraud_results.parquet"

# -------------------------------
# LOAD DATA
# -------------------------------
def load_data():
    print("Loading graph features...")
    df = pd.read_parquet(DATA_PATH)
    print("Data shape:", df.shape)
    return df

# -------------------------------
# ADD AML RISK LOGIC (IMPORTANT)
# -------------------------------
def add_risk_features(df):
    print("Adding risk features...")

    # High degree = many connections
    df["high_degree_flag"] = df["degree"] > df["degree"].quantile(0.95)

    # High pagerank = influential node
    df["high_pagerank_flag"] = df["pagerank"] > df["pagerank"].quantile(0.95)

    # Combined risk score (simple but powerful)
    df["risk_score"] = (
        df["high_degree_flag"].astype(int) +
        df["high_pagerank_flag"].astype(int)
    )

    return df

# -------------------------------
# TRAIN MODEL
# -------------------------------
def train_model(df):
    print("Training Isolation Forest...")

    X = df[["degree", "pagerank"]]

    model = IsolationForest(
        n_estimators=100,
        contamination=0.02,
        random_state=42
    )

    df["anomaly_score"] = model.fit_predict(X)

    return df

# -------------------------------
# SAVE RESULTS
# -------------------------------
def save_results(df):
    df.to_parquet(OUTPUT_PATH, index=False)
    print("✅ Results saved at:", OUTPUT_PATH)

# -------------------------------
# SHOW RESULTS
# -------------------------------
def show_results(df):
    suspicious = df[df["anomaly_score"] == -1]

    print("\n🚨 Top Suspicious Accounts:")
    print(suspicious.sort_values(by="risk_score", ascending=False).head(10))

    print("\n📊 Summary:")
    print("Total Accounts:", len(df))
    print("Suspicious Accounts:", len(suspicious))

# -------------------------------
# MAIN
# -------------------------------
def main():
    df = load_data()
    df = add_risk_features(df)
    df = train_model(df)

    show_results(df)
    save_results(df)

if __name__ == "__main__":
    main()