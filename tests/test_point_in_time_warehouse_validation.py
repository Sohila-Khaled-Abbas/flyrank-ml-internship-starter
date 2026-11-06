from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "06_point_in_time_warehouse_validation.py"
SPEC = importlib.util.spec_from_file_location("point_in_time_validation", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def make_daily_frame(missing_recent_day: bool = False, future_impressions: float = 50.0):
    cutoff = pd.Timestamp("2026-06-01")
    dates = pd.date_range(cutoff - pd.Timedelta(days=60), cutoff + pd.Timedelta(days=29), freq="D")
    rows = []
    for day in dates:
        if day < cutoff - pd.Timedelta(days=30):
            impressions = 100.0
        elif day < cutoff:
            impressions = 70.0
        else:
            impressions = float(future_impressions)

        if missing_recent_day and day == pd.Timestamp("2026-05-10"):
            impressions = np.nan

        rows.append(
            {
                "report_date": day.date(),
                "client_hash_id": "client_test_001",
                "content_hash_id": "content_test_001",
                "gsc_impressions": impressions,
                "gsc_clicks": 5.0 if pd.notna(impressions) else np.nan,
                "gsc_avg_position": 7.0,
                "gsc_data_available": True,
            }
        )
    return pd.DataFrame(rows)


class PointInTimeCohortTests(unittest.TestCase):
    def setUp(self):
        self.con = duckdb.connect()

    def tearDown(self):
        self.con.close()

    def register_frame(self, frame: pd.DataFrame, table_name: str):
        self.con.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.con.register("test_input_frame", frame)
        self.con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM test_input_frame")
        self.con.unregister("test_input_frame")

    def build(self, *, min_days=30, missing_recent_day=False, future_impressions=50.0):
        self.register_frame(
            make_daily_frame(missing_recent_day, future_impressions),
            "synthetic_fact",
        )
        return MODULE.build_cohort(
            self.con,
            min_impressions=1,
            min_days=min_days,
            decline_threshold=0.20,
            fact_relation="synthetic_fact",
            cutoffs=[("2026-06-01", "test")],
        )

    def test_features_are_pre_cutoff_and_target_is_forward_only(self):
        frame = self.build()
        self.assertEqual(len(frame), 1)
        row = frame.iloc[0]
        self.assertEqual(row["older_impressions"], 3000.0)
        self.assertEqual(row["prev_impressions"], 2100.0)
        self.assertEqual(row["next_impressions"], 1500.0)
        self.assertEqual(row["observed_days_older30"], 30)
        self.assertEqual(row["observed_days_prev30"], 30)
        self.assertEqual(row["observed_days_next30"], 30)
        self.assertEqual(row["target_decline"], 1)
        self.assertAlmostEqual(row["baseline_score"], 0.30)

    def test_future_change_changes_label_not_features(self):
        declining = self.build(future_impressions=50.0).iloc[0]
        non_declining = self.build(future_impressions=90.0).iloc[0]
        self.assertEqual(declining["target_decline"], 1)
        self.assertEqual(non_declining["target_decline"], 0)
        for column in ("older_impressions", "prev_impressions", *MODULE.FEATURES):
            self.assertAlmostEqual(float(declining[column]), float(non_declining[column]))

    def test_null_measurement_is_not_counted_as_an_observed_day(self):
        frame = self.build(min_days=29, missing_recent_day=True)
        self.assertEqual(len(frame), 1)
        self.assertEqual(frame.iloc[0]["observed_days_prev30"], 29)
        with self.assertRaises(RuntimeError):
            self.build(min_days=30, missing_recent_day=True)


if __name__ == "__main__":
    unittest.main()
