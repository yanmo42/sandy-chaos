#!/usr/bin/env python3
"""Generate a paradox phase-diagram sweep for hyperstition toy dynamics.

Outputs:
- CSV grid with per-point regime labels and terminal narrative state
- JSON summary with aggregate counts/fractions
- PNG phase diagram (regime map + terminal state heatmap)

Usage:
    ./venv/bin/python scripts/hyperstition_phase_sweep.py
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap

# Add project root so script works without editable package install.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nfem_suite.intelligence.cognition import HyperstitionParameters, HyperstitionToyModel


def _build_model(profile: str) -> HyperstitionToyModel:
    if profile == "paradox-v1":
        params = HyperstitionParameters(
            narrative_inertia=0.3,
            social_coupling=0.0,
            observation_gain=1.4,
            observer_coupling=0.9,
            action_gain=2.5,
            temporal_bias_gain=3.0,
            noise_std=0.0,
        )
    elif profile == "default":
        params = HyperstitionParameters()
    else:
        raise ValueError(f"Unknown profile: {profile}")

    return HyperstitionToyModel(params=params)


def _regime_code(paradox: Dict[str, bool]) -> int:
    if paradox.get("self_fulfilling", False):
        return 1
    if paradox.get("self_defeating", False):
        return -1
    return 0


def run_sweep(args: argparse.Namespace) -> Dict[str, object]:
    model = _build_model(args.profile)

    truth_vals = np.linspace(args.truth_min, args.truth_max, args.grid)
    delta_vals = np.linspace(args.delta_min, args.delta_max, args.grid)

    regime_grid = np.zeros((args.grid, args.grid), dtype=int)
    final_grid = np.zeros((args.grid, args.grid), dtype=float)

    rows = []
    counts = {"self_fulfilling": 0, "self_defeating": 0, "neutral": 0}

    for i, truth in enumerate(truth_vals):
        for j, delta in enumerate(delta_vals):
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
            code = _regime_code(paradox)

            if code == 1:
                counts["self_fulfilling"] += 1
                regime = "self_fulfilling"
            elif code == -1:
                counts["self_defeating"] += 1
                regime = "self_defeating"
            else:
                counts["neutral"] += 1
                regime = "neutral"

            regime_grid[i, j] = code
            final_grid[i, j] = final_m
            rows.append(
                {
                    "truth": float(truth),
                    "temporal_asymmetry": float(delta),
                    "initial_m": float(args.initial_m),
                    "final_m": final_m,
                    "regime_code": int(code),
                    "regime": regime,
                }
            )

    total = args.grid * args.grid
    fractions = {k: float(v / total) for k, v in counts.items()}

    return {
        "model_profile": args.profile,
        "parameters": asdict(model.params),
        "truth_range": [args.truth_min, args.truth_max],
        "delta_range": [args.delta_min, args.delta_max],
        "grid": int(args.grid),
        "steps": int(args.steps),
        "initial_m": float(args.initial_m),
        "counts": counts,
        "fractions": fractions,
        "truth_values": truth_vals,
        "delta_values": delta_vals,
        "regime_grid": regime_grid,
        "final_grid": final_grid,
        "rows": rows,
    }


def write_artifacts(result: Dict[str, object], out_dir: Path, stem: str) -> Dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / f"{stem}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["truth", "temporal_asymmetry", "initial_m", "final_m", "regime_code", "regime"],
        )
        writer.writeheader()
        writer.writerows(result["rows"])

    summary_path = out_dir / f"{stem}_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "model_profile": result["model_profile"],
                "parameters": result["parameters"],
                "truth_range": result["truth_range"],
                "delta_range": result["delta_range"],
                "grid": result["grid"],
                "steps": result["steps"],
                "initial_m": result["initial_m"],
                "counts": result["counts"],
                "fractions": result["fractions"],
            },
            f,
            indent=2,
        )

    # Plot
    regime_grid = result["regime_grid"]
    final_grid = result["final_grid"]

    truth_min, truth_max = result["truth_range"]
    delta_min, delta_max = result["delta_range"]
    extent = [delta_min, delta_max, truth_min, truth_max]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)

    regime_cmap = ListedColormap(["#4575b4", "#f7f7f7", "#d73027"])
    # bins: [-1.5,-0.5)->self-defeating, [-0.5,0.5)->neutral, [0.5,1.5)->self-fulfilling
    regime_norm = BoundaryNorm([-1.5, -0.5, 0.5, 1.5], regime_cmap.N)

    im0 = axes[0].imshow(
        regime_grid,
        origin="lower",
        extent=extent,
        aspect="auto",
        cmap=regime_cmap,
        norm=regime_norm,
    )
    axes[0].set_title("Paradox Regime Map")
    axes[0].set_xlabel("Temporal Asymmetry Δ")
    axes[0].set_ylabel("Truth Signal T")

    cbar0 = fig.colorbar(im0, ax=axes[0], ticks=[-1, 0, 1], shrink=0.92)
    cbar0.ax.set_yticklabels(["self-defeating", "neutral", "self-fulfilling"])

    im1 = axes[1].imshow(
        final_grid,
        origin="lower",
        extent=extent,
        aspect="auto",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
    )
    axes[1].set_title("Terminal Narrative State m(T)")
    axes[1].set_xlabel("Temporal Asymmetry Δ")
    axes[1].set_ylabel("Truth Signal T")
    fig.colorbar(im1, ax=axes[1], shrink=0.92, label="final_m")

    png_path = out_dir / f"{stem}.png"
    fig.savefig(png_path, dpi=180)
    plt.close(fig)

    return {
        "csv": csv_path,
        "summary": summary_path,
        "png": png_path,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate hyperstition paradox phase diagram sweep.")
    p.add_argument("--profile", choices=["paradox-v1", "default"], default="paradox-v1")
    p.add_argument("--out-dir", default="memory/hyperstition")
    p.add_argument("--stem", default="paradox_phase_diagram")
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
    result = run_sweep(args)
    paths = write_artifacts(result, Path(args.out_dir), args.stem)

    print("[hyperstition phase sweep] complete")
    print(f"profile={result['model_profile']} grid={result['grid']} steps={result['steps']} initial_m={result['initial_m']}")
    print(f"counts={result['counts']}")
    print(f"fractions={result['fractions']}")
    print(f"csv={paths['csv']}")
    print(f"summary={paths['summary']}")
    print(f"png={paths['png']}")


if __name__ == "__main__":
    main()
