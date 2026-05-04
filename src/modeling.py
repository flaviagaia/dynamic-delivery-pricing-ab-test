from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Dict, List

from .data_factory import build_sample_dataset


def _read_rows(path: str) -> List[Dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def _to_float(value: str) -> float:
    return float(value)


def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _variance(values: List[float], mean_value: float) -> float:
    if len(values) <= 1:
        return 0.0
    return sum((value - mean_value) ** 2 for value in values) / (len(values) - 1)


def _difference_with_ci(control_values: List[float], treatment_values: List[float]) -> Dict[str, float]:
    if not control_values or not treatment_values:
        return {
            "control": round(_mean(control_values), 4),
            "treatment": round(_mean(treatment_values), 4),
            "absolute_lift": 0.0,
            "relative_lift_pct": 0.0,
            "ci_low": 0.0,
            "ci_high": 0.0,
        }

    control_mean = _mean(control_values)
    treatment_mean = _mean(treatment_values)
    control_var = _variance(control_values, control_mean)
    treatment_var = _variance(treatment_values, treatment_mean)
    standard_error = math.sqrt((control_var / len(control_values)) + (treatment_var / len(treatment_values)))
    diff = treatment_mean - control_mean
    margin = 1.96 * standard_error if standard_error else 0.0

    return {
        "control": round(control_mean, 4),
        "treatment": round(treatment_mean, 4),
        "absolute_lift": round(diff, 4),
        "relative_lift_pct": round((diff / control_mean) * 100, 2) if control_mean else 0.0,
        "ci_low": round(diff - margin, 4),
        "ci_high": round(diff + margin, 4),
    }


def _metric_arrays(rows: List[Dict[str, str]], field: str) -> Dict[str, List[float]]:
    grouped = {"control": [], "treatment": []}
    for row in rows:
        grouped[row["variant"]].append(_to_float(row[field]))
    return grouped


def _build_metrics(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, float]]:
    contribution_per_session = _metric_arrays(rows, "contribution_margin")
    conversion_rate = _metric_arrays(rows, "converted_order")
    net_completion_rate = _metric_arrays(rows, "net_completed_order")
    cancellation_rate = _metric_arrays(rows, "cancelled_order")
    delivery_fee = _metric_arrays(rows, "delivery_fee")

    return {
        "primary_metric_contribution_margin_per_session": _difference_with_ci(
            contribution_per_session["control"],
            contribution_per_session["treatment"],
        ),
        "secondary_metric_net_completed_order_rate": _difference_with_ci(
            net_completion_rate["control"],
            net_completion_rate["treatment"],
        ),
        "secondary_metric_avg_delivery_fee": _difference_with_ci(
            delivery_fee["control"],
            delivery_fee["treatment"],
        ),
        "guardrail_checkout_conversion_rate": _difference_with_ci(
            conversion_rate["control"],
            conversion_rate["treatment"],
        ),
        "guardrail_cancellation_rate": _difference_with_ci(
            cancellation_rate["control"],
            cancellation_rate["treatment"],
        ),
    }


def _segment_lifts(rows: List[Dict[str, str]], segment_key: str) -> Dict[str, Dict[str, float]]:
    segments: Dict[str, List[Dict[str, str]]] = {}
    for row in rows:
        segments.setdefault(row[segment_key], []).append(row)

    result = {}
    for segment, segment_rows in sorted(segments.items()):
        margins = _metric_arrays(segment_rows, "contribution_margin")
        result[segment] = _difference_with_ci(margins["control"], margins["treatment"])
    return result


def _recommendation(metrics: Dict[str, Dict[str, float]]) -> Dict[str, object]:
    primary = metrics["primary_metric_contribution_margin_per_session"]
    conversion = metrics["guardrail_checkout_conversion_rate"]
    cancellation = metrics["guardrail_cancellation_rate"]

    launch = (
        primary["absolute_lift"] > 0
        and primary["ci_low"] > 0
        and conversion["absolute_lift"] > -0.01
        and cancellation["absolute_lift"] < 0.01
    )

    return {
        "decision": "ship_treatment" if launch else "needs_iteration",
        "reasoning": [
            "Contribution margin per exposed session is the main pricing metric because it balances revenue capture and conversion impact.",
            "Checkout conversion is a guardrail because pricing changes that hurt demand too much can destroy marketplace health.",
            "Cancellation rate is a guardrail because poor pricing can create low-quality orders that fail downstream.",
        ],
    }


def run_analysis(base_dir: Path) -> Dict[str, object]:
    dataset_info = build_sample_dataset(base_dir)
    rows = _read_rows(dataset_info["dataset_path"])
    metrics = _build_metrics(rows)

    report = {
        "dataset_source": dataset_info["dataset_source"],
        "session_count": len(rows),
        "variant_counts": {
            "control": sum(1 for row in rows if row["variant"] == "control"),
            "treatment": sum(1 for row in rows if row["variant"] == "treatment"),
        },
        "experiment_design": {
            "unit_of_randomization": "checkout_session",
            "treatment_description": "Dynamic delivery-fee policy with lower fees for price-sensitive sessions and mild peak adjustment elsewhere",
            "primary_metric": "contribution_margin_per_session",
            "secondary_metrics": ["net_completed_order_rate", "avg_delivery_fee"],
            "guardrails": ["checkout_conversion_rate", "cancellation_rate"],
        },
        "metrics": metrics,
        "segment_lifts_by_region": _segment_lifts(rows, "region"),
        "segment_lifts_by_user_segment": _segment_lifts(rows, "user_segment"),
        "recommendation": _recommendation(metrics),
    }

    processed_dir = base_dir / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    report_path = processed_dir / "pricing_experiment_report.json"
    report["report_artifact"] = str(report_path)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
