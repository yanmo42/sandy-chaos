#!/usr/bin/env python3
"""Corridor survival sweep under narrative-boundary coupling q(L,t)=B0+λN_t.

Contract 7 (AUD-007): Tests whether the L4 bidirectional corridor structure
survives when the temporal asymmetry Δ becomes time-varying via the coupling.

Outputs:
  memory/research/narrative_coupling_results_YYYYMMDD.json
"""

from __future__ import annotations

import datetime
import json
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nfem_suite.intelligence.cognition import HyperstitionParameters, HyperstitionToyModel
from nfem_suite.intelligence.cognition.hyperstition import NarrativeBoundaryChannel

# L4 Arm-A parameters (from ablation_compare.py)
ARM_A_PARAMS = HyperstitionParameters(
    narrative_inertia=0.3,
    social_coupling=0.0,
    observation_gain=1.4,
    observer_coupling=0.9,
    action_gain=2.5,
    temporal_bias_gain=3.0,
    noise_std=0.0,
)

# Same sweep grid as L4 result packet
TRUTH_GRID = np.linspace(-0.8, 0.8, 81)
DELTA_GRID = np.linspace(-0.8, 0.8, 81)
INITIAL_M = 0.6
STEPS = 80

# Dominance threshold: corridor declared if > 80% of a truth-band slice
DOMINANCE_THRESH = 0.80

LAMBDA_VALUES = [0.0, 0.1, 0.5, 1.0]


def measure_corridors(model: HyperstitionToyModel, lam: float) -> dict:
    """Sweep (truth, delta) grid and measure corridor metrics for given lambda."""
    neg_truth_mask = TRUTH_GRID < 0
    pos_truth_mask = TRUTH_GRID > 0

    neg_truth_vals = TRUTH_GRID[neg_truth_mask]
    pos_truth_vals = TRUTH_GRID[pos_truth_mask]

    # For each delta: rate of self-fulfilling over neg-truth slice
    sf_rates_by_delta = []
    # For each delta: rate of self-defeating over pos-truth slice
    sd_rates_by_delta = []

    total_sf = 0
    total_sd = 0
    total = 0

    for delta in DELTA_GRID:
        channel = NarrativeBoundaryChannel(B0=delta, lam=lam, mode="sinusoidal", period=20.0)

        sf_neg = 0
        sd_pos = 0

        for T in TRUTH_GRID:
            traj = model.rollout_narrative_coupled(INITIAL_M, channel, steps=STEPS, exogenous_truth=T)
            final_m = traj[-1]
            paradox = model.classify_paradox(INITIAL_M, final_m, T)
            if paradox["self_fulfilling"]:
                total_sf += 1
                if T < 0:
                    sf_neg += 1
            if paradox["self_defeating"]:
                total_sd += 1
                if T > 0:
                    sd_pos += 1
            total += 1

        sf_rate = sf_neg / max(len(neg_truth_vals), 1)
        sd_rate = sd_pos / max(len(pos_truth_vals), 1)
        sf_rates_by_delta.append(sf_rate)
        sd_rates_by_delta.append(sd_rate)

    sf_rates = np.array(sf_rates_by_delta)
    sd_rates = np.array(sd_rates_by_delta)

    # Corridor declared where rate > dominance threshold
    sf_corridor_deltas = DELTA_GRID[sf_rates > DOMINANCE_THRESH].tolist()
    sd_corridor_deltas = DELTA_GRID[sd_rates > DOMINANCE_THRESH].tolist()

    sf_corridor_present = len(sf_corridor_deltas) > 0
    sd_corridor_present = len(sd_corridor_deltas) > 0
    bidirectional = sf_corridor_present and sd_corridor_present

    # Corridor range strings
    sf_range = f"Δ ∈ [{min(sf_corridor_deltas):.2f}, {max(sf_corridor_deltas):.2f}]" if sf_corridor_present else "none"
    sd_range = f"Δ ∈ [{min(sd_corridor_deltas):.2f}, {max(sd_corridor_deltas):.2f}]" if sd_corridor_present else "none"

    return {
        "lambda": float(lam),
        "total_self_fulfilling": int(total_sf),
        "total_self_defeating": int(total_sd),
        "total_grid_points": int(total),
        "sf_corridor_present": bool(sf_corridor_present),
        "sd_corridor_present": bool(sd_corridor_present),
        "bidirectional_coverage": bool(bidirectional),
        "sf_corridor_range": sf_range,
        "sd_corridor_range": sd_range,
        "sf_rates_by_delta": [float(r) for r in sf_rates],
        "sd_rates_by_delta": [float(r) for r in sd_rates],
    }


def verdict(results_by_lambda: list[dict]) -> dict[float, str]:
    """Assign SURVIVES/WEAKENS/COLLAPSES verdict per lambda."""
    baseline = next(r for r in results_by_lambda if r["lambda"] == 0.0)
    verdicts: dict[float, str] = {}
    for r in results_by_lambda:
        lam = r["lambda"]
        if lam == 0.0:
            verdicts[lam] = "SURVIVES"
            continue
        bidi = r["bidirectional_coverage"]
        sf_ok = r["sf_corridor_present"]
        sd_ok = r["sd_corridor_present"]
        if bidi:
            verdicts[lam] = "SURVIVES"
        elif sf_ok or sd_ok:
            verdicts[lam] = "WEAKENS"
        else:
            verdicts[lam] = "COLLAPSES"
    return verdicts


def main() -> None:
    print("SANDY CHAOS — CONTRACT 7: Narrative-Boundary Coupling (AUD-007)")
    model = HyperstitionToyModel(params=ARM_A_PARAMS, rng_seed=42)

    results_list = []
    for lam in LAMBDA_VALUES:
        print(f"\nRunning lambda={lam}...")
        r = measure_corridors(model, lam)
        results_list.append(r)
        print(f"  SF corridor: {r['sf_corridor_range']}")
        print(f"  SD corridor: {r['sd_corridor_range']}")
        print(f"  Bidirectional: {r['bidirectional_coverage']}")

    verdicts_map = verdict(results_list)
    for r in results_list:
        r["verdict"] = verdicts_map[r["lambda"]]
        print(f"  lambda={r['lambda']} -> {r['verdict']}")

    # Two surfaces connected: check if both corridor surfaces (sf in neg-truth space,
    # sd in pos-truth space) are simultaneously active at any Δ for lambda > 0
    two_surfaces_connected = any(
        r["bidirectional_coverage"] for r in results_list if r["lambda"] > 0.0
    )

    payload = {
        "contract": "C7",
        "audit_id": "AUD-007",
        "date": datetime.date.today().strftime("%Y%m%d"),
        "lambda_values": LAMBDA_VALUES,
        "dominance_threshold": DOMINANCE_THRESH,
        "grid_points": len(TRUTH_GRID) * len(DELTA_GRID),
        "two_surfaces_connected": bool(two_surfaces_connected),
        "results": results_list,
        "verdicts": {str(k): v for k, v in verdicts_map.items()},
    }

    out_dir = Path("/home/ian/projects/sandy-chaos/memory/research")
    out_dir.mkdir(parents=True, exist_ok=True)
    today_str = datetime.date.today().strftime("%Y%m%d")
    out_path = out_dir / f"narrative_coupling_results_{today_str}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"\nSaved results to {out_path}")

    print("\n=== SUMMARY ===")
    for lam in LAMBDA_VALUES:
        r = next(x for x in results_list if x["lambda"] == lam)
        print(f"lambda={lam}: {r['verdict']}  (SF={r['sf_corridor_range']}, SD={r['sd_corridor_range']})")
    print(f"Two surfaces connected: {'YES' if two_surfaces_connected else 'NO'}")


if __name__ == "__main__":
    main()
