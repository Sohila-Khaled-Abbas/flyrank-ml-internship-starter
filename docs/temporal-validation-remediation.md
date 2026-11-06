# Temporal validation remediation plan

**Status: NOT VALIDATED — original snapshot experiment withdrawn as predictive evidence**

## Why the original result is not valid

The starter file `content_refresh_anonymized.csv` is a single export snapshot. Its documented activity fields (including `impressions_90d`, `clicks_90d`, `sessions_90d`, `ctr`, `avg_position`, and engagement rates) aggregate activity through the export date. The target `trend_direction` is derived from the most recent 30-day impressions compared with the preceding 30 days.

Those periods overlap: the target's recent 30-day period is included in the 90-day feature aggregates and derived rates. Excluding only `trend_direction`, `trend_pct`, and `is_declining_label` does not make the remaining snapshot aggregates temporally safe. A client-grouped split only isolates clients; it does not fix this time-window overlap.

The existing 30,000-row experiment and its metrics are therefore **exploratory snapshot results only**. Previously published Precision@K and ROC-AUC claims are withdrawn and must not be represented as validated predictive performance.

## Required point-in-time design

Use the daily warehouse fact at grain `report_date × client × content`. For each eligible content item, define a prediction cutoff (T):

1. Build every feature using records with `report_date < T` only. Document the exact lookback interval for each feature.
2. Define the outcome only after the cutoff, for example a decline over the next 30 days relative to a preceding 30-day baseline. The label window must begin after (T).
3. Join content/client metadata only when its effective timestamp is at or before (T). Exclude fields whose values are only known after the cutoff.
4. Enforce minimum history and availability rules per client using `gsc_data_start` and `ga4_data_start`; preserve three-valued availability flags and do not turn unknown history into observed zeros.
5. Use a chronological train/validation/test design. Keep client groups disjoint for the primary unseen-client test where sample size permits, and report both temporal and group coverage.
6. Fit imputation, encoding, feature selection, and calibration on training data only. Do not select the final model on the test set.
7. Compare against a baseline computed from the same pre-cutoff information and evaluate on the exact same test cohort.
8. Report cohort dates, clients, rows, positive rate, missingness, Precision@K, recall, average precision, ROC-AUC, confidence intervals where feasible, and a leakage audit.

## Acceptance checks before restoring performance claims

- [ ] A prediction cutoff and forward label window are explicit and non-overlapping.
- [ ] Automated tests assert that no feature row uses data at or after its cutoff.
- [ ] No target-derived or future-derived field enters the feature matrix.
- [ ] Train, validation, and test windows are chronological.
- [ ] Client overlap is reported and matches the chosen evaluation question.
- [ ] Baseline and model are evaluated on identical held-out records.
- [ ] All metrics are regenerated from the same reproducible pipeline run.
- [ ] README, paper, notebooks, model report, and demo use the same validated result.

## Current limitation

The repository's public starter CSV does not contain the row-level dates needed to reconstruct point-in-time features and future labels. The larger daily warehouse release is described in the data dictionary, but the required warehouse data and access credentials are not part of this repository. Therefore, this change documents and enforces the validation boundary; it does **not** claim to have retrained a temporally valid model or generated replacement performance metrics.

## Historical artifact policy

Keep the original notebook, model artifacts, and exploratory metrics for traceability, but label them as historical, snapshot-based experiments. Do not silently overwrite their history or describe them as leakage-free.
