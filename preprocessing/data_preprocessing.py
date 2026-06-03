# processing/data_preprocessing.py

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import glob
from tqdm import tqdm
import hashlib

def anonymize_id(value):
    return hashlib.sha256(str(value).encode()).hexdigest()[:12]

def anonymize_data(df):
    print("Applying anonymization...")

    df["sender_id"] = df["sender_id"].apply(anonymize_id)
    df["receiver_id"] = df["receiver_id"].apply(anonymize_id)

    return df

from security.audit_logs import log_access

log_access("READ", "final_transactions.parquet")

# -------------------------------
# PATHS
# -------------------------------
RAW_PATH = "data/raw/"
PROCESSED_PATH = "data/processed/"

# -------------------------------
# 1. LOAD SYNTHETIC PARQUET FILES
# -------------------------------
def load_synthetic():
    print("Loading synthetic data...")

    files = glob.glob(RAW_PATH + "synthetic/*.parquet")
    df_list = []

    for f in tqdm(files):
        df_list.append(pd.read_parquet(f))

    synthetic_df = pd.concat(df_list, ignore_index=True)
    print("Synthetic shape:", synthetic_df.shape)

    return synthetic_df

# -------------------------------
# 2. LOAD KYC DATA
# -------------------------------
def load_kyc():
    print("Loading KYC data...")
    
    kyc = pd.read_csv(RAW_PATH + "kyc/kyc_dataset.csv")
    
    print("KYC shape:", kyc.shape)
    return kyc

# -------------------------------
# 3. CLEAN DATA
# -------------------------------
def clean_data(df):
    print("Cleaning data...")

    df = df.drop_duplicates()
    df = df.dropna()

    return df

# -------------------------------
# 4. MERGE TRANSACTIONS + KYC
# -------------------------------
def merge_data(transactions, kyc):
    print("Merging datasets...")

    merged = transactions.merge(
        kyc,
        left_on="sender_id",
        right_on="account_id",
        how="left"
    )

    print("Merged shape:", merged.shape)
    return merged

# -------------------------------
# 5. SAVE PROCESSED DATA
# -------------------------------
def save_data(df, filename):
    path = PROCESSED_PATH + filename
    df.to_parquet(path, index=False)
    print("Saved:", path)

# -------------------------------
# MAIN PIPELINE
# -------------------------------
def run_pipeline():
    synthetic = load_synthetic()
    synthetic = clean_data(synthetic)

    kyc = load_kyc()
    kyc = clean_data(kyc)

    merged = merge_data(synthetic, kyc)

    save_data(synthetic, "synthetic_clean.parquet")
    save_data(kyc, "kyc_clean.parquet")
    save_data(merged, "final_transactions.parquet")

if __name__ == "__main__":
    run_pipeline()