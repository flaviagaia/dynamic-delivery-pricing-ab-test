from __future__ import annotations

import unittest
from pathlib import Path

from src.data_factory import build_sample_dataset
from src.modeling import run_analysis


class DynamicDeliveryPricingABTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.base_dir = Path(__file__).resolve().parents[1]

    def test_dataset_factory_creates_files(self) -> None:
        dataset_info = build_sample_dataset(self.base_dir)
        self.assertEqual(dataset_info["dataset_source"], "synthetic_dynamic_delivery_pricing_experiment")
        self.assertTrue(Path(dataset_info["dataset_path"]).exists())
        self.assertTrue(Path(dataset_info["dataset_reference_path"]).exists())

    def test_analysis_contract(self) -> None:
        report = run_analysis(self.base_dir)
        self.assertEqual(report["dataset_source"], "synthetic_dynamic_delivery_pricing_experiment")
        self.assertEqual(report["session_count"], 1500)
        self.assertGreaterEqual(report["variant_counts"]["control"], 650)
        self.assertGreaterEqual(report["variant_counts"]["treatment"], 650)
        self.assertIn("primary_metric_contribution_margin_per_session", report["metrics"])
        self.assertIn("guardrail_checkout_conversion_rate", report["metrics"])
        self.assertIn(report["recommendation"]["decision"], {"ship_treatment", "needs_iteration"})
        self.assertTrue(Path(report["report_artifact"]).exists())

    def test_segment_analysis_is_present(self) -> None:
        report = run_analysis(self.base_dir)
        self.assertEqual(set(report["segment_lifts_by_region"].keys()), {"east", "north", "south", "west"})
        self.assertEqual(set(report["segment_lifts_by_user_segment"].keys()), {"casual", "power_user", "price_sensitive"})


if __name__ == "__main__":
    unittest.main()
