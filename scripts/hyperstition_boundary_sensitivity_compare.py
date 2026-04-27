#!/usr/bin/env python3
"""Compare Arm A and Arm E on stricter hyperstition separators.

This is a bounded SC-CONCEPT-0003 follow-on to the temporal-driver comparator.
The previous pass showed that simple bidirectional corridor coverage does not
separate narrative-conditioned feedback (Arm A) from an open-loop temporal
driver (Arm E). This pass asks whether two stricter, inspectable criteria do:

1. corridor-boundary geometry across truth/delta slices,
2. sensitivity to the initial narrative state.

The script is intentionally descriptive rather than promotional: if the measured
criteria do not separate the arms cleanly, the verdict should say so.
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

from nfem_suite.intelligence.cognition import HyperstitionToyModel
from scripts.hyperstition_temporal_driver_compare import BASELINE, OpenLoopTemporalDriverModel, classify_code


def contiguous_intervals(values: Iterable[float], *, step: float, tol: float = 1e-9) -> list[list[float]]:
    ordered = sorted(float(v) for v in values)
    if not ordered:
        return []
    intervals: list[list[float]] = []
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


def rollout_code(model: HyperstitionToyModel, *, initial_m: float, steps: int, truth: float, delta: float) -> tuple[int, float]:
    traj = model.rollout_mean_field(
        initial_m=initial_m,
        steps=steps,
        exogenous_truth=float(truth),
        temporal_asymmetry=float(delta),
    )
    final_m = float(traj[-1])
    return classify_code(initial_m, final_m, float(truth)), final_m


def regime_label(code: int) -> str:
    if code == 1:
        return "self_fulfilling"
    if code == -1:
        return "self_defeating"
    return "neutral"


def boundary_summary(model: HyperstitionToyModel, *, initial_m: float, steps: int, truth_vals: np.ndarray, delta_vals: np.ndarray) -> dict:
    rows = []
    boundary_points = 0
    total_adjacent_edges = 0
    # Store codes on a rectangular grid indexed truth-major, delta-minor.
    codes = np.zeros((len(truth_vals), len(delta_vals)), dtype=int)
    finals = np.zeros_like(codes, dtype=float)
    for i, truth in enumerate(truth_vals):
        for j, delta in enumerate(delta_vals):
            code, final_m = rollout_code(model, initial_m=initial_m, steps=steps, truth=float(truth), delta=float(delta))
            codes[i, j] = code
            finals[i, j] = final_m
            rows.append({
                "truth": float(truth),
                "delta": float(delta),
                "regime_code": int(code),
                "regime": regime_label(int(code)),
                "final_m": float(final_m),
            })

    for i in range(len(truth_vals)):
        for j in range(len(delta_vals)):
            for di, dj in ((1, 0), (0, 1)):
                ni, nj = i + di, j + dj
                if ni >= len(truth_vals) or nj >= len(delta_vals):
                    continue
                total_adjacent_edges += 1
                if codes[i, j] != codes[ni, nj]:
                    boundary_points += 1

    delta_step = float(delta_vals[1] - delta_vals[0]) if len(delta_vals) > 1 else 0.0
    threshold_crossings = {}
    for code, name in ((1, "self_fulfilling"), (-1, "self_defeating")):
        by_truth = []
        truth_with_regime = []
        for i, truth in enumerate(truth_vals):
            deltas = [float(delta_vals[j]) for j in range(len(delta_vals)) if codes[i, j] == code]
            if deltas:
                truth_with_regime.append(float(truth))
                by_truth.append({
                    "truth": float(truth),
                    "delta_min": min(deltas),
                    "delta_max": max(deltas),
                    "width": max(deltas) - min(deltas),
                    "intervals": contiguous_intervals(deltas, step=delta_step),
                })
        widths = [entry["width"] for entry in by_truth]
        threshold_crossings[name] = {
            "truth_intervals_with_regime": contiguous_intervals(
                truth_with_regime,
                step=float(truth_vals[1] - truth_vals[0]) if len(truth_vals) > 1 else 0.0,
            ),
            "truth_count_with_regime": len(truth_with_regime),
            "mean_delta_width": float(np.mean(widths)) if widths else 0.0,
            "max_delta_width": float(np.max(widths)) if widths else 0.0,
            "by_truth": by_truth,
        }

    return {
        "boundary_edge_count": int(boundary_points),
        "adjacent_edge_count": int(total_adjacent_edges),
        "boundary_edge_fraction": float(boundary_points / total_adjacent_edges) if total_adjacent_edges else 0.0,
        "terminal_mean_abs": float(np.mean(np.abs(finals))),
        "terminal_std": float(np.std(finals)),
        "regime_counts": {
            "self_fulfilling": int(np.sum(codes == 1)),
            "self_defeating": int(np.sum(codes == -1)),
            "neutral": int(np.sum(codes == 0)),
        },
        "threshold_crossings": threshold_crossings,
        "rows": rows,
    }


def sensitivity_summary(model: HyperstitionToyModel, *, initial_vals: np.ndarray, steps: int, truth_vals: np.ndarray, delta_vals: np.ndarray) -> dict:
    by_initial = []
    matrix: dict[str, np.ndarray] = {}
    for initial_m in initial_vals:
        codes = np.zeros((len(truth_vals), len(delta_vals)), dtype=int)
        for i, truth in enumerate(truth_vals):
            for j, delta in enumerate(delta_vals):
                code, _ = rollout_code(model, initial_m=float(initial_m), steps=steps, truth=float(truth), delta=float(delta))
                codes[i, j] = code
        key = f"{float(initial_m):.6f}"
        matrix[key] = codes
        total = codes.size
        by_initial.append({
            "initial_m": float(initial_m),
            "self_fulfilling_fraction": float(np.sum(codes == 1) / total),
            "self_defeating_fraction": float(np.sum(codes == -1) / total),
            "neutral_fraction": float(np.sum(codes == 0) / total),
        })

    pairwise = []
    keys = list(matrix.keys())
    for a_idx, a_key in enumerate(keys):
        for b_key in keys[a_idx + 1 :]:
            a = matrix[a_key]
            b = matrix[b_key]
            disagreement = int(np.sum(a != b))
            pairwise.append({
                "initial_a": float(a_key),
                "initial_b": float(b_key),
                "regime_disagreement": disagreement,
                "regime_disagreement_fraction": float(disagreement / a.size),
            })
    fractions = [entry["regime_disagreement_fraction"] for entry in pairwise]
    return {
        "initial_values": [float(v) for v in initial_vals],
        "by_initial": by_initial,
        "pairwise_regime_disagreement": pairwise,
        "mean_pairwise_regime_disagreement_fraction": float(np.mean(fractions)) if fractions else 0.0,
        "max_pairwise_regime_disagreement_fraction": float(np.max(fractions)) if fractions else 0.0,
    }


def compare_scalar(metric_a: float, metric_e: float) -> dict:
    return {
        "arm_a": float(metric_a),
        "arm_e": float(metric_e),
        "absolute_gap": float(abs(metric_a - metric_e)),
        "relative_gap_vs_arm_a": float(abs(metric_a - metric_e) / abs(metric_a)) if metric_a else None,
    }


def run(args: argparse.Namespace) -> dict:
    truth_vals = np.linspace(args.truth_min, args.truth_max, args.grid)
    delta_vals = np.linspace(args.delta_min, args.delta_max, args.grid)
    initial_vals = np.linspace(args.initial_min, args.initial_max, args.initial_grid)
    profiles = {
        "arm_a_narrative_on": HyperstitionToyModel(params=BASELINE),
        "arm_e_open_loop_temporal_driver": OpenLoopTemporalDriverModel(params=BASELINE),
    }
    results = {
        "pass": "hyperstition_boundary_sensitivity_compare",
        "concept": "SC-CONCEPT-0003",
        "parameters": asdict(BASELINE),
        "grid": args.grid,
        "steps": args.steps,
        "baseline_initial_m": args.initial_m,
        "initial_sensitivity_range": [args.initial_min, args.initial_max],
        "initial_sensitivity_grid": args.initial_grid,
        "truth_range": [args.truth_min, args.truth_max],
        "delta_range": [args.delta_min, args.delta_max],
        "profiles": {},
        "separation_metrics": {},
    }
    for name, model in profiles.items():
        results["profiles"][name] = {
            "boundary_geometry": boundary_summary(
                model,
                initial_m=args.initial_m,
                steps=args.steps,
                truth_vals=truth_vals,
                delta_vals=delta_vals,
            ),
            "initial_condition_sensitivity": sensitivity_summary(
                model,
                initial_vals=initial_vals,
                steps=args.steps,
                truth_vals=truth_vals,
                delta_vals=delta_vals,
            ),
        }

    a = results["profiles"]["arm_a_narrative_on"]
    e = results["profiles"]["arm_e_open_loop_temporal_driver"]
    results["separation_metrics"] = {
        "boundary_edge_fraction": compare_scalar(
            a["boundary_geometry"]["boundary_edge_fraction"],
            e["boundary_geometry"]["boundary_edge_fraction"],
        ),
        "terminal_std": compare_scalar(
            a["boundary_geometry"]["terminal_std"],
            e["boundary_geometry"]["terminal_std"],
        ),
        "mean_initial_sensitivity": compare_scalar(
            a["initial_condition_sensitivity"]["mean_pairwise_regime_disagreement_fraction"],
            e["initial_condition_sensitivity"]["mean_pairwise_regime_disagreement_fraction"],
        ),
        "max_initial_sensitivity": compare_scalar(
            a["initial_condition_sensitivity"]["max_pairwise_regime_disagreement_fraction"],
            e["initial_condition_sensitivity"]["max_pairwise_regime_disagreement_fraction"],
        ),
    }
    mean_gap = results["separation_metrics"]["mean_initial_sensitivity"]["absolute_gap"]
    boundary_gap = results["separation_metrics"]["boundary_edge_fraction"]["absolute_gap"]
    if mean_gap >= args.clean_gap_threshold or boundary_gap >= args.clean_gap_threshold:
        results["verdict"] = "CANDIDATE_SEPARATOR_FOUND"
    else:
        results["verdict"] = "NO_CLEAN_SEPARATOR_FOUND"
    results["verdict_note"] = (
        "A candidate separator must remain interpretable under follow-up inspection; this pass reports measured gaps only."
        if results["verdict"] == "CANDIDATE_SEPARATOR_FOUND"
        else "The tested boundary/sensitivity criteria did not cleanly separate Arm A from Arm E at the configured gap threshold."
    )
    return results


def write_outputs(results: dict, out_dir: Path, stem: str) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{stem}.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    csv_path = out_dir / f"{stem}_boundary_rows.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["profile", "truth", "delta", "regime_code", "regime", "final_m"])
        writer.writeheader()
        for profile, payload in results["profiles"].items():
            for row in payload["boundary_geometry"]["rows"]:
                writer.writerow({"profile": profile, **row})
    return {"json": json_path, "csv": csv_path}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare Arm A and Arm E on boundary geometry and initial-condition sensitivity.")
    p.add_argument("--out-dir", default="memory/research/hyperstition-v0")
    p.add_argument("--stem", default="boundary_sensitivity_comparison_v0")
    p.add_argument("--grid", type=int, default=81)
    p.add_argument("--steps", type=int, default=80)
    p.add_argument("--initial-m", type=float, default=0.6)
    p.add_argument("--initial-min", type=float, default=-0.8)
    p.add_argument("--initial-max", type=float, default=0.8)
    p.add_argument("--initial-grid", type=int, default=9)
    p.add_argument("--truth-min", type=float, default=-0.8)
    p.add_argument("--truth-max", type=float, default=0.8)
    p.add_argument("--delta-min", type=float, default=-0.8)
    p.add_argument("--delta-max", type=float, default=0.8)
    p.add_argument("--clean-gap-threshold", type=float, default=0.1)
    return p.parse_args(argv)


def main() -> None:
    args = parse_args()
    results = run(args)
    paths = write_outputs(results, Path(args.out_dir), args.stem)
    print("[boundary/sensitivity comparison] complete")
    print(f"json={paths['json']}")
    print(f"csv={paths['csv']}")
    for profile, payload in results["profiles"].items():
        bg = payload["boundary_geometry"]
        sens = payload["initial_condition_sensitivity"]
        print(
            f"profile={profile} boundary_fraction={bg['boundary_edge_fraction']:.4f} "
            f"terminal_std={bg['terminal_std']:.4f} "
            f"mean_initial_sensitivity={sens['mean_pairwise_regime_disagreement_fraction']:.4f} "
            f"max_initial_sensitivity={sens['max_pairwise_regime_disagreement_fraction']:.4f}"
        )
    print(f"separation_metrics={results['separation_metrics']}")
    print(f"verdict={results['verdict']}")


if __name__ == "__main__":
    main()
