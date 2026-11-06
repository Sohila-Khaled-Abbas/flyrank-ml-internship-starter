# Point-in-time warehouse rebuild

This workflow is designed to replace the withdrawn 30k snapshot metrics with a reproducible evaluation against the authorized hosted daily warehouse.

## Source and access

- Dataset: [FlyRank/internship-warehouse](https://huggingface.co/datasets/FlyRank/internship-warehouse)
- Fact table: `fact_content_daily_performance` (about 78.8M rows; report-date × client × content grain)
- Storage: gated Parquet; use only access granted to your Hugging Face account.
- The 30k CSV remains a historical starter exercise. It is not used for prospective evaluation.

Read [DATA_USE.md](https://github.com/flyrank-bih/flyrank-ml-internship-starter/blob/main/DATA_USE.md) and accept the Hugging Face dataset terms before running. Never commit the READ token, downloaded warehouse data, row-level cohorts, or pseudonymous IDs.

## Evaluation design

For each monthly cutoff, the script creates:

- Features from the 30 calendar days immediately before cutoff, plus a prior 30-day context window for momentum.
- A transparent momentum baseline comparing those two pre-cutoff windows.
- A target from the following 30 calendar days, strictly beginning at cutoff.
- GSC-only eligible rows using `gsc_data_available IS TRUE`. Observed-day counts use non-null daily rows, relying on the source's documented `report_date × client × content` grain.
- Minimum prior impressions and minimum observed days in the older feature, recent feature, and forward outcome windows.
- Train cutoffs June 2025–January 2026.
- Validation cutoffs February and March 2026.
- Final test cutoff June 2026, on clients held out from training/validation.

The client split is deterministic. The final score is therefore both forward in time and on unseen clients. The fixed 90-day query table is excluded because it overlaps the later observation period. Client/content metadata is excluded until effective timestamps can be established.

## Run locally (Windows PowerShell)

The default configuration is intended for a 16 GB Windows machine: DuckDB is capped at 6 GB, uses two threads, and spills intermediate work to disk. The script processes one 90-day cutoff at a time and writes one Parquet part per cutoff, rather than aggregating all eleven cutoffs in one query. Keep the spill and scratch locations on a drive with ample free space.

```powershell
cd path\to\flyrank-ml-internship-starter
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

New-Item -ItemType Directory -Force "D:\duckdb_tmp\flyrank","D:\flyrank_warehouse_work" | Out-Null
python scripts/06_point_in_time_warehouse_validation.py --memory-limit 6GB --threads 2 --temp-dir "D:\duckdb_tmp\flyrank" --scratch-dir "D:\flyrank_warehouse_work" --max-ml-rows 100000
```

The Hugging Face READ token is requested through a hidden prompt. Do not paste it into chat, put it in the script, notebook, command history, or GitHub. The account behind the token must have accepted the dataset gate.

### Memory and sampling behavior

- The full eligible point-in-time cohort is written as eleven Parquet parts under `cohort_parts\` in the scratch directory (one file per cutoff). It is not loaded wholesale into pandas.
- DuckDB uses the configured memory limit and spills intermediate aggregation state into `--temp-dir`. The script allows up to 100 GB of spill files; make sure the selected drive has enough free space. Cutoffs are processed sequentially so only one 90-day aggregation is active at a time.
- The client-level train/test assignment is made from the full cohort before model sampling, so the unseen-client test remains separated from training clients.
- `--max-ml-rows` is the target sample size for each model partition. Training is sampled by target class; validation and test use deterministic uniform hash sampling, preserving class prevalence in expectation. Hash sampling can vary slightly around the target, and the exact available and loaded row counts are recorded in the summary.
- When validation sampling is too small to retain both classes, rerun with a higher `--max-ml-rows` value, such as `250000`, provided the machine has enough memory.

## Outputs

The aggregate `evaluation_summary.json` remains under `work/outputs/point_in_time/`. The full row-level cohort is written as Parquet parts under `cohort_parts\` in the directory passed through `--scratch-dir`. Keep both outputs local and private; do not commit the full cohort or pseudonymous IDs. Review the aggregate summary for disclosure safety before publishing.

## Important

The script is a first point-in-time baseline, not an automatic restoration of the old capstone claims. Run it with authorized access, inspect the resulting cohort sizes, class balance, date coverage, and diagnostics, and verify the schema/availability semantics against the gated release manifest. Only then decide whether the metrics are robust enough to publish. Predictive association is not causal evidence of refresh impact.
