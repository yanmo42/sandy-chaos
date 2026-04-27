#!/usr/bin/env python3
"""Compare Arm A against an open-loop temporal-driver baseline.

This is the bounded follow-on requested by the robustness pass for
SC-CONCEPT-0003: design one stronger comparator that preserves temporal
asymmetry but breaks narrative-conditioned feedback specifically.

Arm A keeps the implemented action channel:
    action = tanh(action_gain * (m + temporal_bias_gain * Delta))

Arm E keeps observer coupling and temporal asymmetry, but removes current
narrative state from the action channel:
    action = tanh(action_gain * (temporal_bias_gain * Delta))

Interpretation: Arm E is an open-loop temporal-driver comparator. It tests
whether bidirectional corridor coverage requires narrative-conditioned feedback,
or whether an exogenous temporal-asymmetry driver can reproduce the same headline
signature with less mechanism baggage.

Usage:
    python3 scripts/hyperstition_temporal_driver_compare.py \
        --out-dir memory/research/hyperstition-v0 \
        --stem temporal_driver_comparison_v0
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nfem_suite.intelligence.cognition import HyperstitionParameters, HyperstitionToyModel


BASELINE = HyperstitionParameters(
    narrative_inertia=0.3,
    social_coupling=0.0,
    observation_gain=1.4,
    observer_coupling=0.9,
    action_gain=2.5,
    temporal_bias_gain=3.0,
    noise_std=0.0,
)


class OpenLoopTemporalDriverModel(HyperstitionToyModel):
    """Comparator that removes current narrative state from the action channel."""

    def mean_field_map(self, m: float, exogenous_truth: float = 0.0, temporal_asymmetry: float = 0.0) -> float:
        p = self.params
        temporal_shift = p.temporal_bias_gain * temporal_asymmetry
        action = np.tanh(p.action_gain * temporal_shift)
        observation = (1.0 - p.observer_coupling) * exogenous_truth + p.observer_coupling * action
        inner = (p.narrative_inertia + p.social_coupling) * m + p.observation_gain * observation
        return float(np.tanh(inner))


def classify_code(initial_m: float, final_m: float, truth: float) -> int:
    init_sign = int(np.sign(initial_m))
    final_sign = int(np.sign(final_m))
    truth_sign = int(np.sign(truth))
    if truth_sign != 0 and final_sign != 0 and init_sign == final_sign and final_sign != truth_sign:
        return 1
    if truth_sign != 0 and init_sign == truth_sign and final_sign == -truth_sign:
        return -1
    return 0


def contiguous_intervals(values: Iterable[float], *, step: float, tol: float = 1e-9) -> list[list[float]]:
    ordered = sorted(float(v) for v in values)
    if not ordered:
        return []
    intervals = []
    start = ordered[0]
    prev = ordered[0]
    for value in ordered[1:]:
        if abs(value - prev - step) <= tol:
            prev = value
            continue
        intervals.append([round(start, 6), round(prev, 6)])
        start = value
        prev = value
    intervals.append([round(start, 6), round(prev, 6)])
    return intervals


def summarize_corridors(rows: list[dict], delta_vals: np.ndarray, *, dominance_threshold: float) -> dict:
    delta_step = float(delta_vals[1] - delta_vals[0]) if len(delta_vals) > 1 else 0.0
    summary = {}
    for truth_sign, truth_label in ((-1, "truth_negative"), (1, "truth_positive")):
        truth_rows = [row for row in rows if row["truth_sign"] == truth_sign]
        block = {
            "dominance_threshold": dominance_threshold,
            "self_fulfilling": {"dominant_delta_intervals": [], "peak_fraction": 0.0},
            "self_defeating": {"dominant_delta_intervals": [], "peak_fraction": 0.0},
        }
        for regime_code, regime_label in ((1, "self_fulfilling"), (-1, "self_defeating")):
            qualifying = []
            peak_fraction = 0.0
            for delta in delta_vals:
                slice_rows = [row for row in truth_rows if abs(row["temporal_asymmetry"] - float(delta)) < 1e-9]
                if not slice_rows:
                    continue
                frac = sum(1 for row in slice_rows if row["regime_code"] == regime_code) / len(slice_rows)
                peak_fraction = max(peak_fraction, float(frac))
                if frac >= dominance_threshold:
                    qualifying.append(float(delta))
            block[regime_label] = {
                "dominant_delta_intervals": contiguous_intervals(qualifying, step=delta_step),
                "peak_fraction": float(peak_fraction),
            }
        summary[truth_label] = block
    return summary


def run_profile(name: str, model: HyperstitionToyModel, args: argparse.Namespace) -> dict:
    truth_vals = np.linspace(args.truth_min, args.truth_max, args.grid)
    delta_vals = np.linspace(args.delta_min, args.delta_max, args.grid)

    counts = {"self_fulfilling": 0, "self_defeating": 0, "neutral": 0}
    rows = []

    for truth in truth_vals:
        for delta in delta_vals:
            traj = model.rollout_mean_field(
                initial_m=args.initial_m,
                steps=args.steps,
                exogenous_truth=float(truth),
                temporal_asymmetry=float(delta),
            )
            final_m = float(traj[-1])
            code = classify_code(args.initial_m, final_m, float(truth))
            regime = "neutral"
            if code == 1:
                regime = "self_fulfilling"
            elif code == -1:
                regime = "self_defeating"
            counts[regime] += 1
            rows.append({
                "truth": float(truth),
                "temporal_asymmetry": float(delta),
                "truth_sign": int(np.sign(truth)),
                "delta_sign": int(np.sign(delta)),
                "final_m": final_m,
                "regime_code": int(code),
                "regime": regime,
            })

    total = len(rows)
    corridor_summary = summarize_corridors(rows, delta_vals, dominance_threshold=args.dominance_threshold)
    signature = {
        "has_negative_truth_self_fulfilling_corridor": bool(
            corridor_summary["truth_negative"]["self_fulfilling"]["dominant_delta_intervals"]
        ),
        "has_positive_truth_self_defeating_corridor": bool(
            corridor_summary["truth_positive"]["self_defeating"]["dominant_delta_intervals"]
        ),
    }
    signature["bidirectional_paradox_coverage"] = bool(
        signature["has_negative_truth_self_fulfilling_corridor"]
        and signature["has_positive_truth_self_defeating_corridor"]
    )

    return {
        "profile": name,
        "parameters": asdict(model.params),
        "counts": counts,
        "fractions": {key: value / total for key, value in counts.items()},
        "corridor_summary": corridor_summary,
        "structural_signature": signature,
        "rows": rows,
    }


def compare_rows(arm_a_rows: list[dict], comparator_rows: list[dict]) -> dict:
    paired = list(zip(arm_a_rows, comparator_rows))
    total = len(paired)
    sign_disagreement = sum(
        1 for a, b in paired if int(np.sign(a["final_m"])) != int(np.sign(b["final_m"]))
    )
    magnitude_gap_025 = sum(1 for a, b in paired if abs(a["final_m"] - b["final_m"]) > 0.25)
    magnitude_gap_050 = sum(1 for a, b in paired if abs(a["final_m"] - b["final_m"]) > 0.50)
    regime_disagreement = sum(1 for a, b in paired if a["regime_code"] != b["regime_code"])
    return {
        "total_points": total,
        "sign_disagreement": sign_disagreement,
        "sign_disagreement_fraction": sign_disagreement / total,
        "magnitude_gap_gt_0_25": magnitude_gap_025,
        "magnitude_gap_gt_0_25_fraction": magnitude_gap_025 / total,
        "magnitude_gap_gt_0_50": magnitude_gap_050,
        "magnitude_gap_gt_0_50_fraction": magnitude_gap_050 / total,
        "regime_disagreement": regime_disagreement,
        "regime_disagreement_fraction": regime_disagreement / total,
    }


def write_outputs(results: dict, out_dir: Path, stem: str) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{stem}.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    csv_path = out_dir / f"{stem}_delta_slices.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "profile",
                "truth_band",
                "temporal_asymmetry",
                "self_fulfilling_fraction",
                "self_defeating_fraction",
                "neutral_fraction",
            ],
        )
        writer.writeheader()
        for profile_name, payload in results["profiles"].items():
            rows = payload["rows"]
            delta_vals = sorted({row["temporal_asymmetry"] for row in rows})
            for truth_sign, truth_band in ((-1, "truth_negative"), (1, "truth_positive")):
                truth_rows = [row for row in rows if row["truth_sign"] == truth_sign]
                for delta in delta_vals:
                    slice_rows = [row for row in truth_rows if abs(row["temporal_asymmetry"] - delta) < 1e-9]
                    if not slice_rows:
                        continue
                    total = len(slice_rows)
                    writer.writerow({
                        "profile": profile_name,
                        "truth_band": truth_band,
                        "temporal_asymmetry": delta,
                        "self_fulfilling_fraction": sum(1 for row in slice_rows if row["regime_code"] == 1) / total,
                        "self_defeating_fraction": sum(1 for row in slice_rows if row["regime_code"] == -1) / total,
                        "neutral_fraction": sum(1 for row in slice_rows if row["regime_code"] == 0) / total,
                    })
    return {"json": json_path, "csv": csv_path}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Arm A vs open-loop temporal-driver comparison.")
    p.add_argument("--out-dir", default="memory/research/hyperstition-v0")
    p.add_argument("--stem", default="temporal_driver_comparison_v0")
    p.add_argument("--grid", type=int, default=81)
    p.add_argument("--steps", type=int, default=80)
    p.add_argument("--initial-m", type=float, default=0.6)
    p.add_argument("--truth-min", type=float, default=-0.8)
    p.add_argument("--truth-max", type=float, default=0.8)
    p.add_argument("--delta-min", type=float, default=-0.8)
    p.add_argument("--delta-max", type=float, default=0.8)
    p.add_argument("--dominance-threshold", type=float, default=0.8)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    profiles = {
        "arm_a_narrative_on": HyperstitionToyModel(params=BASELINE),
        "arm_e_open_loop_temporal_driver": OpenLoopTemporalDriverModel(params=BASELINE),
    }
    results = {
        "pass": "temporal_driver_comparison",
        "concept": "SC-CONCEPT-0003",
        "grid": args.grid,
        "steps": args.steps,
        "initial_m": args.initial_m,
        "truth_range": [args.truth_min, args.truth_max],
        "delta_range": [args.delta_min, args.delta_max],
        "dominance_threshold": args.dominance_threshold,
        "profiles": {},
        "arm_a_comparisons": {},
    }

    for name, model in profiles.items():
        results["profiles"][name] = run_profile(name, model, args)

    results["arm_a_comparisons"]["arm_e_open_loop_temporal_driver"] = compare_rows(
        results["profiles"]["arm_a_narrative_on"]["rows"],
        results["profiles"]["arm_e_open_loop_temporal_driver"]["rows"],
    )

    arm_e_signature = results["profiles"]["arm_e_open_loop_temporal_driver"]["structural_signature"]
    results["verdict"] = (
        "COMPARATOR_REPRODUCES_BIDIRECTIONAL_COVERAGE"
        if arm_e_signature["bidirectional_paradox_coverage"]
        else "COMPARATOR_FAILS_BIDIRECTIONAL_COVERAGE"
    )

    paths = write_outputs(results, Path(args.out_dir), args.stem)

    print("[temporal-driver comparison] complete")
    print(f"json={paths['json']}")
    print(f"csv={paths['csv']}")
    for name, payload in results["profiles"].items():
        print(f"profile={name} counts={payload['counts']} signature={payload['structural_signature']}")
    print(f"compare_vs_arm_a arm_e_open_loop_temporal_driver -> {results['arm_a_comparisons']['arm_e_open_loop_temporal_driver']}")
    print(f"verdict={results['verdict']}")


if __name__ == "__main__":
    main()
