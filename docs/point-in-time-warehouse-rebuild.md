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
- GSC-only eligible rows using `gsc_data_available IS TRUE`.
- Minimum prior impressions and minimum observed days in the older feature, recent feature, and forward outcome windows.
- Train cutoffs June 2025–January 2026.
- Validation cutoffs February and March 2026.
- Final test cutoff June 2026, on clients held out from training/validation.

The client split is deterministic. The final score is therefore both forward in time and on unseen clients. The fixed 90-day query table is excluded because it overlaps the later observation period. Client/content metadata is excluded until effective timestamps can be established.

## Run locally (Windows PowerShell)

```powershell
cd path\to\flyrank-ml-internship-starter
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:HF_TOKEN = Read-Host "Paste Hugging Face READ token"
python scripts/06_point_in_time_warehouse_validation.py
Remove-Item Env:HF_TOKEN
```

Prefer setting `HF_TOKEN` in the process environment or entering it at the hidden prompt. Do not put the token in the script, notebook, command history, or GitHub.

## Outputs

Generated artifacts are written locally to `work/outputs/point_in_time/` and are not intended for Git:

- `cohort_features_local.parquet` — row-level feature/label cohort; keep private/local.
- `evaluation_summary.json` — aggregate evaluation summary; review for disclosure safety before publishing.

## Important

The script is a first point-in-time baseline, not an automatic restoration of the old capstone claims. Run it with authorized access, inspect the resulting cohort sizes, class balance, date coverage, and diagnostics, and verify the schema/availability semantics against the gated release manifest. Only then decide whether the metrics are robust enough to publish. Predictive association is not causal evidence of refresh impact.
