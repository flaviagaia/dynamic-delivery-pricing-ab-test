from __future__ import annotations

import csv
import json
from pathlib import Path
from random import Random
from typing import Dict, List


PUBLIC_DATASET_REFERENCE = {
    "primary_reference": {
        "name": "NYC TLC Trip Record Data",
        "url": "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page",
        "role": "Public marketplace mobility data with trip distance, fare, and time signals used as a behavioral reference for delivery-fee elasticity and operational cost structure.",
    },
    "project_note": {
        "name": "Synthetic delivery pricing experiment",
        "url": "local_runtime_only",
        "role": "The executable dataset in this repository is synthetic because real delivery pricing experiments are usually proprietary.",
    },
    "notes": [
        "This project simulates an A/B test for a new delivery-fee pricing strategy.",
        "The goal is to show the trade-off between conversion and unit economics in a marketplace product experiment.",
    ],
}


REGIONS = ["north", "south", "east", "west"]
SEGMENTS = ["price_sensitive", "casual", "power_user"]
DEVICES = ["ios", "android", "web"]


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_sample_dataset(base_dir: Path, row_count: int = 1500) -> Dict[str, str]:
    rng = Random(42)
    rows: List[Dict[str, object]] = []

    for index in range(row_count):
        region = REGIONS[index % len(REGIONS)]
        user_segment = SEGMENTS[index % len(SEGMENTS)]
        device = DEVICES[index % len(DEVICES)]
        variant = "control" if rng.random() < 0.5 else "treatment"
        peak_hour = 1 if index % 6 in (0, 1) else 0
        rainy = 1 if index % 8 == 0 else 0

        base_subtotal = 20.0 + (index % 11) * 2.9 + rng.uniform(-1.0, 2.5)
        order_subtotal = round(max(12.0, base_subtotal), 2)
        trip_distance_km = round(1.5 + (index % 7) * 0.8 + rng.uniform(0.0, 1.2), 2)
        basket_size = 1 + (index % 5)

        control_delivery_fee = 2.99 + (0.18 * trip_distance_km) + (0.65 * peak_hour) + rng.uniform(0.0, 0.9)
        treatment_delivery_fee = control_delivery_fee
        if user_segment == "price_sensitive":
            treatment_delivery_fee -= 0.55
        elif peak_hour:
            treatment_delivery_fee += 0.25
        else:
            treatment_delivery_fee -= 0.10
        treatment_delivery_fee = round(max(1.99, treatment_delivery_fee), 2)

        delivery_fee = round(control_delivery_fee, 2) if variant == "control" else treatment_delivery_fee
        variable_cost = round(1.35 + (0.22 * trip_distance_km) + (0.15 * basket_size) + (0.35 * peak_hour) + (0.25 * rainy), 2)

        conversion_prob = 0.62
        if user_segment == "power_user":
            conversion_prob += 0.09
        elif user_segment == "price_sensitive":
            conversion_prob -= 0.06
        if device == "web":
            conversion_prob -= 0.03
        if rainy:
            conversion_prob += 0.01

        fee_penalty = max(0.0, delivery_fee - 2.99)
        fee_discount_bonus = max(0.0, 2.99 - delivery_fee)
        conversion_prob -= 0.035 * fee_penalty
        conversion_prob += 0.02 * fee_discount_bonus
        conversion_prob = _clamp(conversion_prob, 0.28, 0.92)

        converted_order = 1 if rng.random() < conversion_prob else 0

        cancellation_prob = 0.045 + (0.02 * peak_hour) + (0.015 * rainy)
        if delivery_fee > 3.9:
            cancellation_prob += 0.015
        cancellation_prob = _clamp(cancellation_prob, 0.02, 0.18)
        cancelled_order = 1 if converted_order and rng.random() < cancellation_prob else 0

        net_completed = 1 if converted_order and not cancelled_order else 0
        gross_revenue = round((order_subtotal * 0.18) + (delivery_fee if net_completed else 0.0), 2)
        contribution_margin = round(gross_revenue - (variable_cost if net_completed else 0.0), 2)

        rows.append(
            {
                "session_id": f"PRC-{index + 1:05d}",
                "user_id": f"USR-{(index % 420) + 1:04d}",
                "region": region,
                "user_segment": user_segment,
                "device": device,
                "variant": variant,
                "peak_hour": peak_hour,
                "rainy_weather": rainy,
                "basket_size": basket_size,
                "trip_distance_km": trip_distance_km,
                "order_subtotal": order_subtotal,
                "delivery_fee": round(delivery_fee, 2),
                "variable_cost": variable_cost,
                "checkout_started": 1,
                "converted_order": converted_order,
                "cancelled_order": cancelled_order,
                "net_completed_order": net_completed,
                "gross_revenue": gross_revenue,
                "contribution_margin": contribution_margin,
            }
        )

    raw_dir = base_dir / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = raw_dir / "pricing_sessions.csv"
    reference_path = raw_dir / "public_dataset_reference.json"
    _write_csv(dataset_path, rows)
    reference_path.write_text(json.dumps(PUBLIC_DATASET_REFERENCE, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "dataset_source": "synthetic_dynamic_delivery_pricing_experiment",
        "dataset_path": str(dataset_path),
        "dataset_reference_path": str(reference_path),
    }
