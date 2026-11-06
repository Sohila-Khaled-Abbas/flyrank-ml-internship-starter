from __future__ import annotations

import argparse
import getpass
import json
import os
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "work" / "outputs" / "point_in_time"
REL = "hf://datasets/FlyRank/internship-warehouse"
FACT = f"read_parquet('{REL}/fact_content_daily_performance/**/*.parquet')"

# Each cohort predicts the following 30 days using only the 30 days before cutoff.
TRAIN_CUTOFFS = [
    "2025-06-01", "2025-07-01", "2025-08-01", "2025-09-01",
    "2025-10-01", "2025-11-01", "2025-12-01", "2026-01-01",
]
VALIDATION_CUTOFFS = ["2026-02-01", "2026-03-01"]
TEST_CUTOFFS = ["2026-06-01"]
FEATURES = [
    "log1p_prev_impressions",
    "log1p_prev_clicks",
    "log1p_older_impressions",
    "mean_position_prev30",
    "observed_days_prev30",
]


def parse_args():
    p = argparse.ArgumentParser(
        description="Point-in-time FlyRank warehouse evaluation (authorized Hugging Face access required)."
    )
    p.add_argument("--token", default=None, help="Prefer HF_TOKEN environment variable; avoid command-line tokens.")
    p.add_argument("--min-impressions", type=int, default=100)
    p.add_argument("--min-observed-days", type=int, default=20)
    p.add_argument("--decline-threshold", type=float, default=0.20)
    p.add_argument("--test-size", type=float, default=0.20)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--memory-limit", default="6GB", help="DuckDB memory budget; leave headroom for Windows and Python.")
    p.add_argument("--threads", type=int, default=4)
    default_temp = Path("D:/duckdb_tmp/flyrank") if Path("D:/").exists() else ROOT / "work" / "duckdb_tmp"
    p.add_argument("--temp-dir", default=str(default_temp), help="DuckDB spill directory; prefer a drive with ample free space.")
    p.add_argument("--scratch-dir", default=None, help="Directory for the full local Parquet cohort; defaults to the report output directory.")
    p.add_argument("--max-ml-rows", type=int, default=100_000, help="Maximum rows loaded for each model partition.")
    return p.parse_args()


def cutoff_values(cutoffs=None):
    rows = list(cutoffs) if cutoffs is not None else []
    if cutoffs is None:
        for split, dates in (
            ("train", TRAIN_CUTOFFS),
            ("validation", VALIDATION_CUTOFFS),
            ("test", TEST_CUTOFFS),
        ):
            rows.extend((d, split) for d in dates)
    values = ",\n".join(
        f"(DATE '{date}', '{split}')" for date, split in rows
    )
    return values


def build_cohort_sql(
    min_impressions: int,
    min_days: int,
    decline_threshold: float,
    *,
    fact_relation: str = FACT,
    cutoffs=None,
):
    rows = list(cutoffs) if cutoffs is not None else []
    if cutoffs is None:
        for split, dates in (
            ("train", TRAIN_CUTOFFS),
            ("validation", VALIDATION_CUTOFFS),
            ("test", TEST_CUTOFFS),
        ):
            rows.extend((d, split) for d in dates)
    if not rows:
        raise ValueError("At least one cutoff is required.")

    first_report_date = min(pd.Timestamp(date) for date, _ in rows) - pd.Timedelta(days=60)
    end_report_date = max(pd.Timestamp(date) for date, _ in rows) + pd.Timedelta(days=30)

    # Explicit global bounds allow date pruning before joining daily rows to the cutoffs.
    return f"""
    WITH cutoffs(cutoff_date, split_name) AS (VALUES {cutoff_values(rows)}),
    daily AS (
        SELECT
            CAST(report_date AS DATE) AS report_date,
            client_hash_id,
            content_hash_id,
            gsc_impressions::DOUBLE AS impressions,
            gsc_clicks::DOUBLE AS clicks,
            NULLIF(gsc_avg_position, 0)::DOUBLE AS avg_position
        FROM {fact_relation}
        WHERE gsc_data_available IS TRUE
          AND report_date >= DATE '{first_report_date:%Y-%m-%d}'
          AND report_date < DATE '{end_report_date:%Y-%m-%d}'
    ),
    cohort AS (
        SELECT
            c.cutoff_date,
            c.split_name,
            d.client_hash_id,
            d.content_hash_id,
            SUM(CASE WHEN d.report_date >= c.cutoff_date - INTERVAL 30 DAY
                      AND d.report_date < c.cutoff_date
                     THEN d.impressions ELSE 0 END) AS prev_impressions,
            SUM(CASE WHEN d.report_date >= c.cutoff_date - INTERVAL 30 DAY
                      AND d.report_date < c.cutoff_date
                     THEN d.clicks ELSE 0 END) AS prev_clicks,
            SUM(CASE WHEN d.report_date >= c.cutoff_date - INTERVAL 60 DAY
                      AND d.report_date < c.cutoff_date - INTERVAL 30 DAY
                     THEN d.impressions ELSE 0 END) AS older_impressions,
            COUNT(DISTINCT CASE
                WHEN d.report_date >= c.cutoff_date - INTERVAL 60 DAY
                 AND d.report_date < c.cutoff_date - INTERVAL 30 DAY
                 AND d.impressions IS NOT NULL
                THEN d.report_date END) AS observed_days_older30,
            AVG(CASE WHEN d.report_date >= c.cutoff_date - INTERVAL 30 DAY
                      AND d.report_date < c.cutoff_date
                     THEN d.avg_position END) AS mean_position_prev30,
            COUNT(DISTINCT CASE
                WHEN d.report_date >= c.cutoff_date - INTERVAL 30 DAY
                 AND d.report_date < c.cutoff_date
                 AND d.impressions IS NOT NULL
                THEN d.report_date END) AS observed_days_prev30,
            SUM(CASE WHEN d.report_date >= c.cutoff_date
                      AND d.report_date < c.cutoff_date + INTERVAL 30 DAY
                     THEN d.impressions ELSE 0 END) AS next_impressions,
            COUNT(DISTINCT CASE
                WHEN d.report_date >= c.cutoff_date
                 AND d.report_date < c.cutoff_date + INTERVAL 30 DAY
                 AND d.impressions IS NOT NULL
                THEN d.report_date END) AS observed_days_next30
        FROM cutoffs c
        JOIN daily d
          ON d.report_date >= c.cutoff_date - INTERVAL 60 DAY
         AND d.report_date < c.cutoff_date + INTERVAL 30 DAY
        GROUP BY 1, 2, 3, 4
    )
    SELECT *,
        CASE WHEN prev_impressions >= {min_impressions}
                   AND observed_days_prev30 >= {min_days}
                   AND observed_days_older30 >= {min_days}
                   AND observed_days_next30 >= {min_days}
             THEN CAST(next_impressions < prev_impressions * (1.0 - {decline_threshold}) AS INTEGER)
             ELSE NULL END AS target_decline
    FROM cohort
    WHERE prev_impressions >= {min_impressions}
      AND observed_days_prev30 >= {min_days}
      AND observed_days_older30 >= {min_days}
      AND observed_days_next30 >= {min_days}
    """


def build_cohort(
    con,
    min_impressions: int,
    min_days: int,
    decline_threshold: float,
    *,
    fact_relation: str = FACT,
    cutoffs=None,
):
    # Small synthetic tests use this in-memory helper. main() writes the full warehouse
    # result to Parquet instead of collecting every row in pandas.
    sql = build_cohort_sql(
        min_impressions,
        min_days,
        decline_threshold,
        fact_relation=fact_relation,
        cutoffs=cutoffs,
    )
    frame = con.sql(sql).df()
    if frame.empty:
        raise RuntimeError("No eligible cohort rows returned. Check source schema and thresholds.")
    frame["log1p_prev_impressions"] = np.log1p(frame["prev_impressions"].clip(lower=0))
    frame["log1p_prev_clicks"] = np.log1p(frame["prev_clicks"].clip(lower=0))
    frame["log1p_older_impressions"] = np.log1p(frame["older_impressions"].clip(lower=0))
    frame["baseline_score"] = (
        1.0 - frame["prev_impressions"] / frame["older_impressions"].replace(0, np.nan)
    ).clip(lower=0, upper=1).fillna(0)
    frame["target_decline"] = frame["target_decline"].astype(int)
    return frame


def sql_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/").replace("'", "''")


def configure_duckdb(con, memory_limit: str, threads: int, temp_dir: Path) -> None:
    if threads < 1:
        raise ValueError("--threads must be at least 1.")
    temp_dir.mkdir(parents=True, exist_ok=True)
    con.execute(f"SET memory_limit = '{memory_limit}'")
    con.execute(f"SET threads = {threads}")
    con.execute(f"SET temp_directory = '{sql_path(temp_dir)}'")
    con.execute("SET max_temp_directory_size = '100GB'")
    con.execute("SET preserve_insertion_order = false")


HASH_BUCKETS = 10_000_019


def fetch_model_sample(con, predicate: str, max_rows: int, *, stratified: bool):
    # Hash sampling is repeatable. Training is class-stratified; validation/test
    # are uniformly sampled so their observed class prevalence is retained in expectation.
    counts = con.execute(
        f"""
        SELECT target_decline, COUNT(*) AS row_count
        FROM cohort_with_group
        WHERE {predicate}
        GROUP BY target_decline
        ORDER BY target_decline
        """
    ).df()
    available = int(counts["row_count"].sum()) if not counts.empty else 0
    if available == 0:
        return pd.DataFrame(), {"available_rows": 0, "loaded_rows": 0, "sampled": False}

    hash_expr = "hash(client_hash_id, content_hash_id, cutoff_date)"
    if available <= max_rows:
        sample_condition = "TRUE"
        strategy = "all eligible rows"
    elif stratified:
        conditions = []
        per_class_cap = max(1, max_rows // max(1, len(counts)))
        for row in counts.itertuples(index=False):
            row_count = int(row.row_count)
            if row_count <= per_class_cap:
                conditions.append(f"target_decline = {int(row.target_decline)}")
            else:
                threshold = max(1, int((per_class_cap / row_count) * HASH_BUCKETS * 0.98))
                conditions.append(
                    f"(target_decline = {int(row.target_decline)} AND {hash_expr} % {HASH_BUCKETS} < {threshold})"
                )
        sample_condition = "(" + " OR ".join(conditions) + ")"
        strategy = "deterministic hash sample stratified by target class"
    else:
        threshold = max(1, int((max_rows / available) * HASH_BUCKETS * 0.98))
        sample_condition = f"{hash_expr} % {HASH_BUCKETS} < {threshold}"
        strategy = "deterministic uniform hash sample; class prevalence preserved in expectation"

    frame = con.execute(
        f"""
        SELECT
            ln(1.0 + greatest(prev_impressions, 0.0)) AS log1p_prev_impressions,
            ln(1.0 + greatest(prev_clicks, 0.0)) AS log1p_prev_clicks,
            ln(1.0 + greatest(older_impressions, 0.0)) AS log1p_older_impressions,
            mean_position_prev30,
            observed_days_prev30,
            CAST(target_decline AS INTEGER) AS target_decline,
            CASE WHEN older_impressions IS NULL OR older_impressions = 0 THEN 0.0
                 ELSE greatest(0.0, least(1.0, 1.0 - prev_impressions / older_impressions))
            END AS baseline_score
        FROM cohort_with_group
        WHERE {predicate}
          AND ({sample_condition})
        """
    ).df()
    return frame, {
        "available_rows": available,
        "loaded_rows": int(len(frame)),
        "sampled": int(len(frame)) < available,
        "strategy": strategy,
    }


def metric_block(y, scores, k=100):
    y = np.asarray(y, dtype=int)
    scores = np.asarray(scores, dtype=float)
    order = np.argsort(-scores)
    top = order[: min(k, len(order))]
    return {
        "rows": int(len(y)),
        "positive_rate": float(y.mean()) if len(y) else None,
        "precision_at_100": float(y[top].mean()) if len(top) else None,
        "precision_at_100_count": int(len(top)),
        "roc_auc": float(roc_auc_score(y, scores)) if len(np.unique(y)) == 2 else None,
        "average_precision": float(average_precision_score(y, scores)) if len(np.unique(y)) == 2 else None,
    }


def main():
    args = parse_args()
    token = args.token or os.environ.get("HF_TOKEN")
    if not token:
        token = getpass.getpass("Hugging Face READ token (input hidden): ")
    if not token:
        raise SystemExit("A Hugging Face READ token is required.")

    OUT.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"CREATE OR REPLACE SECRET hf (TYPE huggingface, TOKEN '{token.replace(chr(39), chr(39)+chr(39))}')")

    # Metadata-only verification before the main scan.
    bounds = con.sql(
        f"SELECT COUNT(*) AS rows, MIN(report_date) AS min_date, MAX(report_date) AS max_date FROM {FACT}"
    ).df()
    print("Warehouse metadata:", bounds.to_dict(orient="records"))

    frame = build_cohort(
        con,
        args.min_impressions,
        args.min_observed_days,
        args.decline_threshold,
    )
    frame.to_parquet(OUT / "cohort_features_local.parquet", index=False)

    clients = sorted(frame["client_hash_id"].dropna().astype(str).unique())
    if len(clients) < 5:
        raise RuntimeError("Too few eligible clients for a meaningful client holdout.")
    splitter = GroupShuffleSplit(n_splits=1, test_size=args.test_size, random_state=args.seed)
    train_client_idx, test_client_idx = next(
        splitter.split(np.zeros(len(clients)), groups=np.asarray(clients))
    )
    train_clients = set(np.asarray(clients)[train_client_idx])
    test_clients = set(np.asarray(clients)[test_client_idx])

    train = frame[
        frame["split_name"].eq("train")
        & frame["client_hash_id"].astype(str).isin(train_clients)
    ].copy()
    validation = frame[
        frame["split_name"].eq("validation")
        & frame["client_hash_id"].astype(str).isin(train_clients)
    ].copy()
    test = frame[
        frame["split_name"].eq("test")
        & frame["client_hash_id"].astype(str).isin(test_clients)
    ].copy()

    if min(len(train), len(validation), len(test)) == 0:
        raise RuntimeError("Train, validation, or unseen-client test cohort is empty.")
    if train["target_decline"].nunique() < 2 or validation["target_decline"].nunique() < 2:
        raise RuntimeError("Training and validation require both target classes.")

    X_train, y_train = train[FEATURES], train["target_decline"]
    X_val, y_val = validation[FEATURES], validation["target_decline"]
    X_test, y_test = test[FEATURES], test["target_decline"]

    models = {
        "logistic_regression": make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(class_weight="balanced", max_iter=2000, random_state=args.seed),
        ),
        "random_forest": make_pipeline(
            SimpleImputer(strategy="median"),
            RandomForestClassifier(
                n_estimators=400,
                min_samples_leaf=20,
                class_weight="balanced_subsample",
                n_jobs=-1,
                random_state=args.seed,
            ),
        ),
    }
    validation_results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        validation_results[name] = metric_block(y_val, model.predict_proba(X_val)[:, 1])

    selected = max(
        validation_results,
        key=lambda name: (
            validation_results[name]["average_precision"] or -1,
            validation_results[name]["precision_at_100"] or -1,
        ),
    )
    # Refit on train + validation (same client population), then evaluate once on unseen clients.
    train_val = pd.concat([train, validation], ignore_index=True)
    final_model = models[selected]
    final_model.fit(train_val[FEATURES], train_val["target_decline"])
    test_scores = final_model.predict_proba(X_test)[:, 1]

    results = {
        "status": "executed_point_in_time_warehouse_evaluation",
        "source": "FlyRank/internship-warehouse",
        "source_table": "fact_content_daily_performance",
        "feature_window": "30 calendar days immediately before cutoff; report_date < cutoff",
        "target_window": "30 calendar days beginning at cutoff; cutoff <= report_date < cutoff + 30 days",
        "target": f"next-30-day impressions decline greater than {args.decline_threshold:.0%} versus immediately preceding 30 days",
        "baseline": "prior 30-day decline score relative to the 30 days before that; pre-cutoff only",
        "availability_rule": "gsc_data_available IS TRUE; minimum observed days enforced in both windows",
        "minimum_prior_impressions": args.min_impressions,
        "minimum_observed_days_each_window": args.min_observed_days,
        "feature_columns": FEATURES,
        "train_cutoffs": TRAIN_CUTOFFS,
        "validation_cutoffs": VALIDATION_CUTOFFS,
        "test_cutoffs": TEST_CUTOFFS,
        "client_split_seed": args.seed,
        "train_clients": len(train_clients),
        "test_clients": len(test_clients),
        "client_overlap": len(train_clients & test_clients),
        "cohort_sizes": {
            "train_rows": int(len(train)),
            "validation_rows": int(len(validation)),
            "unseen_client_test_rows": int(len(test)),
            "train_clients": int(train["client_hash_id"].nunique()),
            "validation_clients": int(validation["client_hash_id"].nunique()),
            "unseen_test_clients": int(test["client_hash_id"].nunique()),
        },
        "validation_model_selection_metrics": validation_results,
        "selected_model": selected,
        "unseen_client_future_test": metric_block(y_test, test_scores),
        "unseen_client_future_test_baseline": metric_block(y_test, test["baseline_score"].to_numpy()),
        "test_cutoff": TEST_CUTOFFS,
        "limitations": [
            "This is predictive association, not causal evidence that refreshing content causes recovery.",
            "Content/client metadata and query-mix features are deliberately excluded until their effective timestamps can be verified.",
            "The fixed 90-day query table is excluded because its window overlaps the final warehouse months.",
            "Metrics apply only to the eligible observed-GSC cohort and configured thresholds.",
        ],
    }
    (OUT / "evaluation_summary.json").write_text(json.dumps(results, indent=2))
    # Aggregate metrics only; no pseudonymous row-level identifiers are exported.
    print(json.dumps(results, indent=2))
    print(f"Local outputs saved under: {OUT}")


if __name__ == "__main__":
    main()
