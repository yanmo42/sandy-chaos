#!/usr/bin/env python3
"""Run bounded hyperstition ablation comparisons against stronger baselines.

This script extends the initial null-model pass with a small family of stricter
comparators drawn from the project's own governance language:
- passive-observer baseline
- coupled-observer without temporal bias

Outputs:
- JSON summary with per-profile counts and Arm-A separation metrics
- CSV slice summaries by temporal asymmetry delta

Usage:
    ./venv/bin/python scripts/hyperstition_ablation_compare.py \
        --out-dir memory/research/hyperstition-v0 \
        --stem ablation_comparison_v0
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Iterable

import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nfem_suite.intelligence.cognition import HyperstitionParameters, HyperstitionToyModel


PROFILE_BUILDERS = {
    "arm_a_narrative_on": lambda: HyperstitionParameters(
        narrative_inertia=0.3,
        social_coupling=0.0,
        observation_gain=1.4,
        observer_coupling=0.9,
        action_gain=2.5,
        temporal_bias_gain=3.0,
        noise_std=0.0,
    ),
    "arm_b_null_narrative_off": lambda: HyperstitionParameters(
        narrative_inertia=0.3,
        social_coupling=0.0,
        observation_gain=1.4,
        observer_coupling=0.0,
        action_gain=2.5,
        temporal_bias_gain=0.0,
        noise_std=0.0,
    ),
    "arm_c_passive_observer": lambda: HyperstitionParameters(
        narrative_inertia=0.3,
        social_coupling=0.0,
        observation_gain=1.4,
        observer_coupling=0.0,
        action_gain=2.5,
        temporal_bias_gain=3.0,
        noise_std=0.0,
    ),
    "arm_d_coupled_no_temporal_bias": lambda: HyperstitionParameters(
        narrative_inertia=0.3,
        social_coupling=0.0,
        observation_gain=1.4,
        observer_coupling=0.9,
        action_gain=2.5,
        temporal_bias_gain=0.0,
        noise_std=0.0,
    ),
}


def classify_code(paradox: Dict[str, bool]) -> int:
    if paradox.get("self_fulfilling", False):
        return 1
    if paradox.get("self_defeating", False):
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
        intervals.append([start, prev])
        start = value
        prev = value
    intervals.append([start, prev])
    return intervals


def summarize_corridors(rows: list[dict], delta_vals: np.ndarray, *, dominance_threshold: float = 0.8) -> dict:
    delta_step = float(delta_vals[1] - delta_vals[0]) if len(delta_vals) > 1 else 0.0
    summary: dict[str, dict[str, object]] = {}

    for truth_sign, truth_label in ((-1, "truth_negative"), (1, "truth_positive")):
        truth_rows = [row for row in rows if row["truth_sign"] == truth_sign]
        block = {
            "dominance_threshold": dominance_threshold,
            "self_fulfilling": {"dominant_delta_intervals": [], "peak_fraction": 0.0},
            "self_defeating": {"dominant_delta_intervals": [], "peak_fraction": 0.0},
        }
        if not truth_rows:
            summary[truth_label] = block
            continue

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


def run_profile(name: str, args: argparse.Namespace) -> dict:
    params = PROFILE_BUILDERS[name]()
    model = HyperstitionToyModel(params=params)

    truth_vals = np.linspace(args.truth_min, args.truth_max, args.grid)
    delta_vals = np.linspace(args.delta_min, args.delta_max, args.grid)

    rows = []
    counts = {"self_fulfilling": 0, "self_defeating": 0, "neutral": 0}
    quadrant_counts = {
        "truth_neg_delta_neg": {"self_fulfilling": 0, "self_defeating": 0, "neutral": 0},
        "truth_neg_delta_pos": {"self_fulfilling": 0, "self_defeating": 0, "neutral": 0},
        "truth_pos_delta_neg": {"self_fulfilling": 0, "self_defeating": 0, "neutral": 0},
        "truth_pos_delta_pos": {"self_fulfilling": 0, "self_defeating": 0, "neutral": 0},
    }

    for truth in truth_vals:
        for delta in delta_vals:
            traj = model.rollout_mean_field(
                initial_m=args.initial_m,
                steps=args.steps,
                exogenous_truth=float(truth),
                temporal_asymmetry=float(delta),
            )
            final_m = float(traj[-1])
            paradox = model.classify_paradox(
                initial_m=args.initial_m,
                final_m=final_m,
                exogenous_truth=float(truth),
            )
            code = classify_code(paradox)
            regime = "neutral"
            if code == 1:
                regime = "self_fulfilling"
            elif code == -1:
                regime = "self_defeating"

            counts[regime] += 1

            truth_sign = int(np.sign(truth))
            delta_sign = int(np.sign(delta))
            if truth_sign != 0 and delta_sign != 0:
                quadrant = f"truth_{'neg' if truth_sign < 0 else 'pos'}_delta_{'neg' if delta_sign < 0 else 'pos'}"
                quadrant_counts[quadrant][regime] += 1

            rows.append(
                {
                    "truth": float(truth),
                    "temporal_asymmetry": float(delta),
                    "truth_sign": truth_sign,
                    "delta_sign": delta_sign,
                    "final_m": final_m,
                    "regime_code": int(code),
                    "regime": regime,
                }
            )

    total = len(rows)
    fractions = {key: float(value / total) for key, value in counts.items()}

    corridor_summary = summarize_corridors(rows, delta_vals)
    structural_signature = {
        "has_negative_truth_self_fulfilling_corridor": bool(
            corridor_summary["truth_negative"]["self_fulfilling"]["dominant_delta_intervals"]
        ),
        "has_positive_truth_self_defeating_corridor": bool(
            corridor_summary["truth_positive"]["self_defeating"]["dominant_delta_intervals"]
        ),
        "bidirectional_paradox_coverage": bool(
            corridor_summary["truth_negative"]["self_fulfilling"]["dominant_delta_intervals"]
            and corridor_summary["truth_positive"]["self_defeating"]["dominant_delta_intervals"]
        ),
    }

    return {
        "profile": name,
        "parameters": asdict(params),
        "counts": counts,
        "fractions": fractions,
        "quadrant_counts": quadrant_counts,
        "corridor_summary": corridor_summary,
        "structural_signature": structural_signature,
        "rows": rows,
    }


def compare_against_arm_a(arm_a_rows: list[dict], other_rows: list[dict]) -> dict:
    paired = list(zip(arm_a_rows, other_rows))
    total = len(paired)
    sign_disagreement = sum(
        1
        for a, b in paired
        if int(np.sign(a["final_m"])) != int(np.sign(b["final_m"]))
    )
    magnitude_gap_025 = sum(1 for a, b in paired if abs(a["final_m"] - b["final_m"]) > 0.25)
    magnitude_gap_050 = sum(1 for a, b in paired if abs(a["final_m"] - b["final_m"]) > 0.50)
    regime_disagreement = sum(1 for a, b in paired if a["regime_code"] != b["regime_code"])

    return {
        "total_points": total,
        "sign_disagreement": sign_disagreement,
        "sign_disagreement_fraction": float(sign_disagreement / total),
        "magnitude_gap_gt_0_25": magnitude_gap_025,
        "magnitude_gap_gt_0_25_fraction": float(magnitude_gap_025 / total),
        "magnitude_gap_gt_0_50": magnitude_gap_050,
        "magnitude_gap_gt_0_50_fraction": float(magnitude_gap_050 / total),
        "regime_disagreement": regime_disagreement,
        "regime_disagreement_fraction": float(regime_disagreement / total),
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
                    writer.writerow(
                        {
                            "profile": profile_name,
                            "truth_band": truth_band,
                            "temporal_asymmetry": delta,
                            "self_fulfilling_fraction": sum(1 for row in slice_rows if row["regime_code"] == 1) / total,
                            "self_defeating_fraction": sum(1 for row in slice_rows if row["regime_code"] == -1) / total,
                            "neutral_fraction": sum(1 for row in slice_rows if row["regime_code"] == 0) / total,
                        }
                    )

    return {"json": json_path, "csv": csv_path}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run bounded hyperstition ablation comparisons.")
    p.add_argument("--out-dir", default="memory/research/hyperstition-v0")
    p.add_argument("--stem", default="ablation_comparison_v0")
    p.add_argument("--grid", type=int, default=81)
    p.add_argument("--steps", type=int, default=80)
    p.add_argument("--initial-m", type=float, default=0.6)
    p.add_argument("--truth-min", type=float, default=-0.8)
    p.add_argument("--truth-max", type=float, default=0.8)
    p.add_argument("--delta-min", type=float, default=-0.8)
    p.add_argument("--delta-max", type=float, default=0.8)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    results = {
        "grid": args.grid,
        "steps": args.steps,
        "initial_m": args.initial_m,
        "truth_range": [args.truth_min, args.truth_max],
        "delta_range": [args.delta_min, args.delta_max],
        "profiles": {},
        "arm_a_comparisons": {},
    }

    for profile_name in PROFILE_BUILDERS:
        results["profiles"][profile_name] = run_profile(profile_name, args)

    arm_a_rows = results["profiles"]["arm_a_narrative_on"]["rows"]
    for profile_name, payload in results["profiles"].items():
        if profile_name == "arm_a_narrative_on":
            continue
        results["arm_a_comparisons"][profile_name] = compare_against_arm_a(arm_a_rows, payload["rows"])

    paths = write_outputs(results, Path(args.out_dir), args.stem)

    print("[hyperstition ablation comparison] complete")
    print(f"json={paths['json']}")
    print(f"csv={paths['csv']}")
    for name, payload in results["profiles"].items():
        print(f"profile={name} counts={payload['counts']} fractions={payload['fractions']}")
    for name, payload in results["arm_a_comparisons"].items():
        print(f"compare_vs_arm_a {name} -> {payload}")


if __name__ == "__main__":
    main()
