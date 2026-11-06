# Historical snapshot model report — withdrawn as predictive evidence

**Status: NOT VALIDATED. Do not cite these metrics as model performance.**

This report is retained to preserve the original experiment record. It was generated from the 30,000-row snapshot dataset, where the 90-day aggregate features overlap the recent 30-day period used to derive the decline label. The client-grouped split does not remove this temporal leakage risk.

The former model comparison and queue preview are intentionally omitted from this report. The original values may remain in historical notebook outputs and commits; they are not validated estimates of prospective performance.

See [the temporal validation remediation plan](../docs/temporal-validation-remediation.md) for the required point-in-time design and acceptance criteria.

**No replacement metrics are published by this change.** The repository does not contain the dated daily warehouse rows required to reconstruct non-overlapping feature and label windows.
