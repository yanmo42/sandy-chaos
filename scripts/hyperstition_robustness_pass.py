#!/usr/bin/env python3
"""Bounded robustness pass for SC-CONCEPT-0003 Arm A corridor structure.

Tests whether the bidirectional corridor split (self-fulfilling for truth<0,
self-defeating for truth>0) remains qualitatively stable under small
one-at-a-time parameter perturbations around the Arm A baseline.

Arm A baseline:
    narrative_inertia=0.3, social_coupling=0.0, observation_gain=1.4,
    observer_coupling=0.9, action_gain=2.5, temporal_bias_gain=3.0

Strategy:
- Perturb each parameter ±5% and ±10% (one at a time, all others held fixed).
- Run the same 81×81 truth × delta grid as the ablation pass.
- Report structural signature (bidirectional coverage yes/no + corridor intervals).
- Flag any perturbation that collapses either corridor arm.

Usage:
    ./venv/bin/python scripts/hyperstition_robustness_pass.py \\
        --out-dir memory/research/hyperstition-v0 \\
        --stem robustness_pass_v0
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
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

PERTURBABLE_PARAMS = [
    "observer_coupling",
    "temporal_bias_gain",
    "narrative_inertia",
    "action_gain",
    "observation_gain",
]

PERTURBATION_STEPS = [-0.10, -0.05, 0.05, 0.10]


def build_perturbed(param: str, frac: float) -> HyperstitionParameters:
    baseline_val = getattr(BASELINE, param)
    delta = baseline_val * frac
    new_val = float(np.clip(baseline_val + delta, 0.0, None))
    kwargs = asdict(BASELINE)
    kwargs[param] = new_val
    return HyperstitionParameters(**kwargs)


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


def classify_code(initial_m: float, final_m: float, truth: float) -> int:
    init_sign = int(np.sign(initial_m))
    final_sign = int(np.sign(final_m))
    truth_sign = int(np.sign(truth))
    if truth_sign != 0 and final_sign != 0 and init_sign == final_sign and final_sign != truth_sign:
        return 1
    if truth_sign != 0 and init_sign == truth_sign and final_sign == -truth_sign:
        return -1
    return 0


def run_profile(params: HyperstitionParameters, args: argparse.Namespace) -> dict:
    model = HyperstitionToyModel(params=params)

    truth_vals = np.linspace(args.truth_min, args.truth_max, args.grid)
    delta_vals = np.linspace(args.delta_min, args.delta_max, args.grid)
    delta_step = float(delta_vals[1] - delta_vals[0]) if len(delta_vals) > 1 else 0.0

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
            rows.append({
                "truth": float(truth),
                "temporal_asymmetry": float(delta),
                "truth_sign": int(np.sign(truth)),
                "final_m": final_m,
                "regime_code": code,
            })

    fulfilling_corridor: list[list[float]] = []
    defeating_corridor: list[list[float]] = []

    for truth_sign, regime_code, target in (
        (-1, 1, fulfilling_corridor),
        (1, -1, defeating_corridor),
    ):
        truth_rows = [r for r in rows if r["truth_sign"] == truth_sign]
        qualifying = []
        for delta in delta_vals:
            slice_rows = [r for r in truth_rows if abs(r["temporal_asymmetry"] - float(delta)) < 1e-9]
            if not slice_rows:
                continue
            frac = sum(1 for r in slice_rows if r["regime_code"] == regime_code) / len(slice_rows)
            if frac >= args.dominance_threshold:
                qualifying.append(float(delta))
        target.extend(contiguous_intervals(qualifying, step=delta_step))

    bidirectional = bool(fulfilling_corridor and defeating_corridor)

    counts = {"self_fulfilling": 0, "self_defeating": 0, "neutral": 0}
    for r in rows:
        if r["regime_code"] == 1:
            counts["self_fulfilling"] += 1
        elif r["regime_code"] == -1:
            counts["self_defeating"] += 1
        else:
            counts["neutral"] += 1

    return {
        "parameters": asdict(params),
        "counts": counts,
        "negative_truth_fulfilling_corridor": fulfilling_corridor,
        "positive_truth_defeating_corridor": defeating_corridor,
        "bidirectional_coverage": bidirectional,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Bounded robustness pass for Arm A corridor structure.")
    p.add_argument("--out-dir", default="memory/research/hyperstition-v0")
    p.add_argument("--stem", default="robustness_pass_v0")
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

    print("[robustness pass] running baseline Arm A...")
    baseline_result = run_profile(BASELINE, args)
    print(f"  baseline: bidirectional={baseline_result['bidirectional_coverage']}")
    print(f"    fulfilling corridor: {baseline_result['negative_truth_fulfilling_corridor']}")
    print(f"    defeating corridor:  {baseline_result['positive_truth_defeating_corridor']}")

    perturbation_results = []
    collapsed = []

    for param in PERTURBABLE_PARAMS:
        for frac in PERTURBATION_STEPS:
            params = build_perturbed(param, frac)
            label = f"{param} {'+' if frac > 0 else ''}{int(frac * 100)}%"
            print(f"[robustness pass] {label} ...")
            result = run_profile(params, args)
            survived = result["bidirectional_coverage"]
            entry = {
                "label": label,
                "perturbed_param": param,
                "perturbation_fraction": frac,
                "perturbed_value": getattr(params, param),
                "baseline_value": getattr(BASELINE, param),
                "bidirectional_coverage": survived,
                "negative_truth_fulfilling_corridor": result["negative_truth_fulfilling_corridor"],
                "positive_truth_defeating_corridor": result["positive_truth_defeating_corridor"],
                "counts": result["counts"],
            }
            perturbation_results.append(entry)
            if not survived:
                collapsed.append(label)
            status = "OK" if survived else "COLLAPSED"
            print(f"  [{status}] {label}: fulfilling={result['negative_truth_fulfilling_corridor']} "
                  f"defeating={result['positive_truth_defeating_corridor']}")

    summary = {
        "pass": "robustness",
        "concept": "SC-CONCEPT-0003",
        "date": "2026-04-21",
        "grid": args.grid,
        "steps": args.steps,
        "initial_m": args.initial_m,
        "dominance_threshold": args.dominance_threshold,
        "baseline": {
            "parameters": asdict(BASELINE),
            **{k: baseline_result[k] for k in (
                "counts", "negative_truth_fulfilling_corridor",
                "positive_truth_defeating_corridor", "bidirectional_coverage"
            )},
        },
        "perturbations": perturbation_results,
        "collapsed_count": len(collapsed),
        "total_perturbations": len(perturbation_results),
        "collapsed_labels": collapsed,
        "structural_verdict": "STABLE" if not collapsed else f"PARTIALLY_FRAGILE ({len(collapsed)}/{len(perturbation_results)} collapsed)",
    }

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{args.stem}.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n=== ROBUSTNESS PASS SUMMARY ===")
    print(f"total perturbations: {len(perturbation_results)}")
    print(f"collapsed: {len(collapsed)}")
    if collapsed:
        print("fragile conditions:")
        for label in collapsed:
            print(f"  - {label}")
    else:
        print("no collapses — bidirectional corridor structure is robust under ±10% parameter drift")
    print(f"verdict: {summary['structural_verdict']}")
    print(f"output: {json_path}")


if __name__ == "__main__":
    main()
