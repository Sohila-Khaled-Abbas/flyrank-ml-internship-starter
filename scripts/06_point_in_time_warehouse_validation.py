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
    p.add_argument("--threads", type=int, default=2)
    default_temp = Path("D:/duckdb_tmp/flyrank") if Path("D:/").exists() else ROOT / "work" / "duckdb_tmp"
    p.add_argument("--temp-dir", default=str(default_temp), help="DuckDB spill directory; prefer a drive with ample free space.")
    p.add_argument("--scratch-dir", default=None, help="Directory for the full local Parquet cohort; defaults to the report output directory.")
    p.add_argument("--max-ml-rows", type=int, default=100_000, help="Target sample size for each model partition.")
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
            SUM(CASE
                WHEN d.report_date >= c.cutoff_date - INTERVAL 60 DAY
                 AND d.report_date < c.cutoff_date - INTERVAL 30 DAY
                 AND d.impressions IS NOT NULL
                THEN 1 ELSE 0 END) AS observed_days_older30,
            AVG(CASE WHEN d.report_date >= c.cutoff_date - INTERVAL 30 DAY
                      AND d.report_date < c.cutoff_date
                     THEN d.avg_position END) AS mean_position_prev30,
            SUM(CASE
                WHEN d.report_date >= c.cutoff_date - INTERVAL 30 DAY
                 AND d.report_date < c.cutoff_date
                 AND d.impressions IS NOT NULL
                THEN 1 ELSE 0 END) AS observed_days_prev30,
            SUM(CASE WHEN d.report_date >= c.cutoff_date
                      AND d.report_date < c.cutoff_date + INTERVAL 30 DAY
                     THEN d.impressions ELSE 0 END) AS next_impressions,
            SUM(CASE
                WHEN d.report_date >= c.cutoff_date
                 AND d.report_date < c.cutoff_date + INTERVAL 30 DAY
                 AND d.impressions IS NOT NULL
                THEN 1 ELSE 0 END) AS observed_days_next30
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

    hash_expr = "hash(CAST(client_hash_id AS VARCHAR) || '|' || CAST(content_hash_id AS VARCHAR) || '|' || CAST(cutoff_date AS VARCHAR))"
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
                threshold = max(1, int((per_class_cap / row_count) * HASH_BUCKETS * 0.95))
                conditions.append(
                    f"(target_decline = {int(row.target_decline)} AND {hash_expr} % {HASH_BUCKETS} < {threshold})"
                )
        sample_condition = "(" + " OR ".join(conditions) + ")"
        strategy = "deterministic hash sample stratified by target class"
    else:
        threshold = max(1, int((max_rows / available) * HASH_BUCKETS * 0.95))
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
    if args.max_ml_rows < 2:
        raise SystemExit("--max-ml-rows must be at least 2.")

    token = args.token or os.environ.get("HF_TOKEN")
    if not token:
        token = getpass.getpass("Hugging Face READ token (input hidden): ")
    if not token:
        raise SystemExit("A Hugging Face READ token is required.")

    OUT.mkdir(parents=True, exist_ok=True)
    scratch_dir = Path(args.scratch_dir).expanduser() if args.scratch_dir else OUT
    scratch_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(args.temp_dir).expanduser()

    con = duckdb.connect()
    configure_duckdb(con, args.memory_limit, args.threads, temp_dir)
    con.execute(
        f"CREATE OR REPLACE SECRET hf (TYPE huggingface, TOKEN '{token.replace(chr(39), chr(39)+chr(39))}')"
    )

    bounds = con.sql(
        f"SELECT COUNT(*) AS rows, MIN(report_date) AS min_date, MAX(report_date) AS max_date FROM {FACT}"
    ).df()
    print("Warehouse metadata:", bounds.to_dict(orient="records"))
    print(
        f"DuckDB memory limit: {args.memory_limit}; threads: {args.threads}; "
        f"spill directory: {temp_dir}; scratch directory: {scratch_dir}"
    )

    # The full 11-cutoff query creates an oversized aggregate hash table. Process one
    # 90-day cutoff window at a time, and keep one Parquet part per cutoff. This bounds
    # the active grouping state and avoids materializing the combined cohort in memory.
    cohort_parts_dir = scratch_dir / "cohort_parts"
    cohort_parts_dir.mkdir(parents=True, exist_ok=True)
    for old_part in cohort_parts_dir.glob("cohort_*.parquet"):
        old_part.unlink()

    cutoff_jobs = []
    for split_name, dates in (
        ("train", TRAIN_CUTOFFS),
        ("validation", VALIDATION_CUTOFFS),
        ("test", TEST_CUTOFFS),
    ):
        cutoff_jobs.extend((date, split_name) for date in dates)

    print(
        f"Building {len(cutoff_jobs)} point-in-time cutoff cohorts sequentially "
        "and writing one Parquet part per cutoff...",
        flush=True,
    )
    for index, (cutoff_date, split_name) in enumerate(cutoff_jobs, start=1):
        cohort_sql = build_cohort_sql(
            args.min_impressions,
            args.min_observed_days,
            args.decline_threshold,
            cutoffs=[(cutoff_date, split_name)],
        )
        part_path = cohort_parts_dir / f"cohort_{split_name}_{cutoff_date}.parquet"
        print(
            f"[{index}/{len(cutoff_jobs)}] {split_name}: cutoff={cutoff_date} "
            f"-> {part_path.name}",
            flush=True,
        )
        con.execute(
            f"COPY ({cohort_sql}) TO '{sql_path(part_path)}' "
            "(FORMAT PARQUET, COMPRESSION ZSTD)"
        )
        part_rows = int(
            con.execute(
                f"SELECT COUNT(*) FROM read_parquet('{sql_path(part_path)}')"
            ).fetchone()[0]
        )
        print(f"    rows written: {part_rows:,}", flush=True)

    cohort_glob = cohort_parts_dir / "*.parquet"
    cohort_relation = f"read_parquet('{sql_path(cohort_glob)}')"
    cohort_rows = int(con.execute(f"SELECT COUNT(*) FROM {cohort_relation}").fetchone()[0])
    if cohort_rows == 0:
        raise RuntimeError("No eligible cohort rows returned. Check source schema and thresholds.")
    print(
        f"Full local cohort written: {cohort_rows:,} rows across "
        f"{len(cutoff_jobs)} Parquet parts -> {cohort_parts_dir}",
        flush=True,
    )

    # Decide client holdout from the full cohort, not from the smaller model samples.
    client_frame = con.execute(
        f"""
        SELECT DISTINCT CAST(client_hash_id AS VARCHAR) AS client_hash_id
        FROM {cohort_relation}
        WHERE client_hash_id IS NOT NULL
        ORDER BY 1
        """
    ).df()
    clients = client_frame["client_hash_id"].astype(str).to_numpy()
    if len(clients) < 5:
        raise RuntimeError("Too few eligible clients for a meaningful client holdout.")
    splitter = GroupShuffleSplit(n_splits=1, test_size=args.test_size, random_state=args.seed)
    train_client_idx, test_client_idx = next(
        splitter.split(np.zeros(len(clients)), groups=clients)
    )
    client_split = np.full(len(clients), "train", dtype=object)
    client_split[test_client_idx] = "test"
    assignment = pd.DataFrame(
        {"client_hash_id": clients, "client_split": client_split}
    )
    con.register("client_assignment_input", assignment)
    con.execute(
        """
        CREATE OR REPLACE TEMP TABLE client_assignment AS
        SELECT * FROM client_assignment_input
        """
    )
    con.unregister("client_assignment_input")
    con.execute(
        f"""
        CREATE OR REPLACE TEMP VIEW cohort_with_group AS
        SELECT c.*, a.client_split
        FROM {cohort_relation} AS c
        INNER JOIN client_assignment AS a
          ON CAST(c.client_hash_id AS VARCHAR) = a.client_hash_id
        """
    )

    populations = con.execute(
        """
        SELECT
            split_name,
            client_split,
            COUNT(*) AS rows,
            COUNT(DISTINCT client_hash_id) AS clients
        FROM cohort_with_group
        GROUP BY 1, 2
        """
    ).df()

    def population(split_name: str, client_split_name: str) -> dict:
        selected = populations[
            populations["split_name"].eq(split_name)
            & populations["client_split"].eq(client_split_name)
        ]
        if selected.empty:
            return {"rows": 0, "clients": 0}
        return {
            "rows": int(selected.iloc[0]["rows"]),
            "clients": int(selected.iloc[0]["clients"]),
        }

    train, train_sample = fetch_model_sample(
        con,
        "split_name = 'train' AND client_split = 'train'",
        args.max_ml_rows,
        stratified=True,
    )
    validation, validation_sample = fetch_model_sample(
        con,
        "split_name = 'validation' AND client_split = 'train'",
        args.max_ml_rows,
        stratified=False,
    )
    test, test_sample = fetch_model_sample(
        con,
        "split_name = 'test' AND client_split = 'test'",
        args.max_ml_rows,
        stratified=False,
    )

    if min(len(train), len(validation), len(test)) == 0:
        raise RuntimeError(
            "Train, validation, or unseen-client test cohort is empty. "
            "Review cutoff coverage and eligibility thresholds."
        )
    if train["target_decline"].nunique() < 2 or validation["target_decline"].nunique() < 2:
        raise RuntimeError(
            "Training and validation require both target classes after sampling. "
            "Try a larger --max-ml-rows value."
        )

    # Release DuckDB's buffers before fitting scikit-learn models.
    con.close()

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
                n_estimators=250,
                max_depth=16,
                min_samples_leaf=20,
                class_weight="balanced_subsample",
                n_jobs=args.threads,
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
    train_val = pd.concat([train, validation], ignore_index=True)
    final_model = models[selected]
    final_model.fit(train_val[FEATURES], train_val["target_decline"])
    test_scores = final_model.predict_proba(X_test)[:, 1]

    train_population = population("train", "train")
    validation_population = population("validation", "train")
    test_population = population("test", "test")
    results = {
        "status": "executed_point_in_time_warehouse_evaluation",
        "source": "FlyRank/internship-warehouse",
        "source_table": "fact_content_daily_performance",
        "warehouse_rows": int(bounds.iloc[0]["rows"]),
        "warehouse_min_date": str(bounds.iloc[0]["min_date"]),
        "warehouse_max_date": str(bounds.iloc[0]["max_date"]),
        "full_eligible_cohort_rows": cohort_rows,
        "full_cohort_parquet_glob": str(cohort_glob),
        "full_cohort_parts": len(cutoff_jobs),
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
        "train_clients": int(len(train_client_idx)),
        "test_clients": int(len(test_client_idx)),
        "client_overlap": int(len(set(clients[train_client_idx]) & set(clients[test_client_idx]))),
        "cohort_sizes": {
            "train_rows_available": train_population["rows"],
            "validation_rows_available": validation_population["rows"],
            "unseen_client_test_rows_available": test_population["rows"],
            "train_clients": train_population["clients"],
            "validation_clients": validation_population["clients"],
            "unseen_test_clients": test_population["clients"],
        },
        "model_sample": {
            "target_rows_per_partition": args.max_ml_rows,
            "train": train_sample,
            "validation": validation_sample,
            "unseen_client_test": test_sample,
            "note": "The full cohort is stored in local Parquet. Model metrics use the samples documented here; validation and test use uniform deterministic hash sampling, while training is stratified by target class.",
        },
        "model_rows_used": {
            "train": int(len(train)),
            "validation": int(len(validation)),
            "unseen_client_test": int(len(test)),
        },
        "validation_model_selection_metrics": validation_results,
        "selected_model": selected,
        "unseen_client_future_test": metric_block(y_test, test_scores),
        "unseen_client_future_test_baseline": metric_block(y_test, test["baseline_score"].to_numpy()),
        "limitations": [
            "This is predictive association, not causal evidence that refreshing content causes recovery.",
            "Content/client metadata and query-mix features are deliberately excluded until their effective timestamps can be verified.",
            "The fixed 90-day query table is excluded because its window overlaps the final warehouse months.",
            "Metrics apply only to the eligible observed-GSC cohort and configured thresholds.",
            "Model metrics are sample-based when a partition exceeds --max-ml-rows; see model_sample for counts and sampling details.",
        ],
    }
    (OUT / "evaluation_summary.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))
    print(f"Evaluation summary saved under: {OUT / 'evaluation_summary.json'}")


if __name__ == "__main__":
    main()
