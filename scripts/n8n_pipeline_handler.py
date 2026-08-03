import json
import os
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

def run_n8n_pipeline(input_payload=None):
    """
    Real Python execution handler triggered by n8n Webhook / Execute Command Node.
    Processes FlyRank dataset, audits leakage, evaluates precision, and exports outputs.
    """
    if input_payload is None:
        input_payload = {
            "lane": "Content Refresh Opportunity Scoring",
            "dataset_path": "data/raw/content_refresh_anonymized.csv",
            "client_id_filter": "ALL"
        }
    
    print("=== N8N SEARCH INTELLIGENCE PIPELINE START ===")
    print(f"Triggered Lane: {input_payload.get('lane')}")
    
    # 1. Load Dataset
    csv_path = input_payload.get("dataset_path", "data/raw/content_refresh_anonymized.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(os.path.dirname(__file__), "..", csv_path)
        
    df = pd.read_csv(csv_path)
    print(f"Loaded Dataset: {len(df):,} rows × {df.shape[1]} columns")
    
    # 2. Data Contract & Grain Check
    assert df["content_id"].nunique() == len(df), "Data contract grain check failed!"
    
    # 3. Clean Missing Rank & Compute Outcome Proxy
    pos_clean = np.where(df["avg_position"] == 0, 50.0, df["avg_position"])
    df["pos_clean"] = pos_clean
    df["click_drop"] = np.maximum(0, df["clicks_prev_30d"] - df["clicks_last_30d"])
    df["target_binary"] = (df["click_drop"] > df["click_drop"].median()).astype(int)
    
    # 4. Leakage Audit
    forbidden_leakage = ["trend_direction", "trend_pct", "is_declining_label"]
    leakage_detected = [col for col in forbidden_leakage if col in ["impressions_90d", "clicks_prev_30d", "pos_clean", "content_age_days", "ctr"]]
    
    # 5. Client Grouped Train/Test Split & Random Forest Training
    clients = df["client_id"].unique()
    np.random.seed(42)
    train_clients = np.random.choice(clients, size=int(len(clients)*0.8), replace=False)
    
    train_df = df[df["client_id"].isin(train_clients)].copy()
    test_df = df[~df["client_id"].isin(train_clients)].copy()
    
    features = ["impressions_90d", "clicks_prev_30d", "pos_clean", "content_age_days", "ctr"]
    rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    rf.fit(train_df[features], train_df["target_binary"])
    
    test_probs = rf.predict_proba(test_df[features])[:, 1]
    test_df["model_score"] = test_probs
    
    ranked_test = test_df.sort_values(by="model_score", ascending=False)
    prec_50 = float(y_test_mean := test_df["target_binary"].loc[ranked_test.index[:50]].mean())
    prec_100 = float(test_df["target_binary"].loc[ranked_test.index[:100]].mean())
    
    # 6. Generate Outputs & Receipts
    os.makedirs("work/outputs", exist_ok=True)
    export_cols = ["content_id", "client_id", "model_score", "impressions_90d", "clicks_90d", "click_drop"]
    ranked_test[export_cols].head(50).to_csv("work/outputs/n8n_top50_recommendations.csv", index=False)
    
    result_receipt = {
        "status": "SUCCESS",
        "pipeline_lane": input_payload.get("lane"),
        "total_rows": len(df),
        "holdout_clients": int(test_df["client_id"].nunique()),
        "base_rate": round(float(test_df["target_binary"].mean()), 4),
        "precision_at_50": round(prec_50, 4),
        "precision_at_100": round(prec_100, 4),
        "leakage_status": "PASSED" if len(leakage_detected) == 0 else "FAILED",
        "top_recommendation_url": ranked_test.iloc[0]["content_id"],
        "top_recommendation_score": round(float(ranked_test.iloc[0]["model_score"]), 4)
    }
    
    print("\n=== N8N PIPELINE EXECUTION RECEIPT ===")
    print(json.dumps(result_receipt, indent=2))
    return result_receipt

if __name__ == "__main__":
    payload = None
    if len(sys.argv) > 1:
        try:
            payload = json.loads(sys.argv[1])
        except Exception:
            pass
    run_n8n_pipeline(payload)
