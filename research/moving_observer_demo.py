#!/usr/bin/env python3
"""
Moving-Observer Anticipation Experiment — Step 3 of plans/defensible-frontier-2026-06-21.md

Predictions/thresholds are committed, dated, BEFORE this code in:
    plans/moving-observer-prereg-2026-06-21.md   (P1-P4 + claim discipline)

Claim under test (plain physics): an observer advecting toward a downstream boundary
gains anticipatory information about its OWN FUTURE arrival-state through the upstream
channel, and that advantage is GATED BY THE FLOW REGIME -- it must collapse as the flow
approaches critical (Fr -> 1), where the upstream channel physically pinches shut
(c_up = 1 - Fr -> 0). That regime-gating is the discriminating signature a pure
forecaster has no reason to reproduce.
"""

import json
import datetime
from pathlib import Path
import numpy as np

# ---- locked parameters ----
SIGMA2 = 1.0
T_C = 1.0
LEAD = 0.5          # fixed lead time before arrival
FROUDES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
N_TRIALS = 50000
N_BOOT = 1000
SEED = 20260621

# Bonferroni family-wise 95% over the 11 simultaneous residual tests
BONF_LO, BONF_HI = 0.05 / len(FROUDES) / 2 * 100, 100 - 0.05 / len(FROUDES) / 2 * 100


def gap(fr):
    """boundary-time gap between freshest upstream news and the arrival target."""
    return LEAD / (1.0 - fr)


def rho(fr):
    """OU predictive correlation across the gap."""
    return np.exp(-gap(fr) / T_C)


def simulate(fr, rng):
    r = rho(fr)
    # draw (B_past_news, B_future_arrival) as bivariate normal, corr = r, var = SIGMA2
    s = np.sqrt(SIGMA2)
    z1 = rng.normal(0.0, 1.0, N_TRIALS)
    z2 = rng.normal(0.0, 1.0, N_TRIALS)
    b_news = s * z1
    b_future = s * (r * z1 + np.sqrt(1.0 - r * r) * z2)

    est_anti = r * b_news                 # Bayes-optimal predictor with the channel
    sq_anti = (est_anti - b_future) ** 2  # anticipator squared error
    sq_base = b_future ** 2               # channel-removed / history-only (predict 0)
    adv = sq_base - sq_anti               # anticipatory advantage, per trial

    # paired residual vs analytic advantage rho^2 (estimator validation)
    resid = adv - r * r

    idx = rng.integers(0, N_TRIALS, size=(N_BOOT, N_TRIALS))

    def ci(arr, lo=2.5, hi=97.5):
        b = arr[idx].mean(axis=1)
        return [float(np.percentile(b, lo)), float(np.percentile(b, hi))]

    return {
        "Fr": fr,
        "c_up": 1.0 - fr,
        "gap": float(gap(fr)),
        "rho": float(r),
        "mse_anticipator": float(sq_anti.mean()),
        "mse_baseline": float(sq_base.mean()),
        "advantage": float(adv.mean()),
        "advantage_ci": ci(adv),
        "analytic_advantage": float(r * r),
        "resid_ci_bonf": ci(resid, BONF_LO, BONF_HI),   # should contain 0
    }


def main():
    rng = np.random.default_rng(SEED)
    rows = [simulate(fr, rng) for fr in FROUDES]
    advs = [r["advantage"] for r in rows]

    # P1: non-negative (MC-noise aware) and monotonically non-increasing in Fr
    nonincr = all(advs[i + 1] <= advs[i] + 2e-3 for i in range(len(advs) - 1))
    not_sig_neg = all(r["advantage_ci"][1] >= 0.0 for r in rows)
    p1 = nonincr and not_sig_neg
    # P2 decisive falsifier: collapse at criticality (Fr=0.99)
    top = rows[-1]
    p2 = (top["advantage_ci"][0] <= 0.0 <= top["advantage_ci"][1]) and abs(top["advantage"]) < 0.01
    # P3: real anticipation at low Fr (Fr=0.1 advantage significantly > 0)
    lo = rows[0]
    p3 = lo["advantage_ci"][0] > 0.0
    # P4: estimator validation. Bonferroni residual CI contains 0, OR MC and analytic
    # agree to a numerical floor (handles the Fr->1 cells where advantage is identically
    # 0 every trial: a degenerate zero-width CI cannot bracket an exact float).
    p4 = all((r["resid_ci_bonf"][0] <= 0.0 <= r["resid_ci_bonf"][1])
             or abs(r["advantage"] - r["analytic_advantage"]) < 1e-6 for r in rows)
    verdict = "PASS" if (p1 and p2 and p3 and p4) else "FAIL"

    result = {
        "experiment": "moving_observer_demo",
        "date": datetime.date.today().isoformat(),
        "prereg": "plans/moving-observer-prereg-2026-06-21.md",
        "params": {"SIGMA2": SIGMA2, "T_C": T_C, "LEAD": LEAD, "froudes": FROUDES,
                   "n_trials": N_TRIALS, "n_boot": N_BOOT, "seed": SEED},
        "rows": rows,
        "checks": {"P1_monotonic_gating": bool(p1), "P2_falsifier_collapse_at_criticality": bool(p2),
                   "P3_real_anticipation_low_Fr": bool(p3), "P4_estimator_validation": bool(p4)},
        "verdict": verdict,
    }

    outdir = Path("memory/research")
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.date.today().strftime("%Y%m%d")
    jpath = outdir / f"moving_observer_results_{stamp}.json"
    jpath.write_text(json.dumps(result, indent=2))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        frs = np.array(FROUDES)
        ad = np.array([r["advantage"] for r in rows])
        lo_ci = np.array([r["advantage_ci"][0] for r in rows])
        hi_ci = np.array([r["advantage_ci"][1] for r in rows])
        an = np.array([r["analytic_advantage"] for r in rows])

        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        ax.fill_between(frs, lo_ci, hi_ci, alpha=0.2, color="purple")
        ax.plot(frs, ad, "o-", color="purple", label="anticipatory advantage (MC, 95% CI)")
        ax.plot(frs, an, "k--", lw=1, label=r"analytic $\rho_\Delta^2$")
        ax.axhline(0, color="k", lw=0.6)
        ax.axvline(1.0, color="red", lw=0.8, ls=":")
        ax.annotate("Fr -> 1: upstream channel closes,\nadvantage collapses (falsifier)",
                    xy=(0.99, 0.0), xytext=(0.45, 0.18), fontsize=8,
                    arrowprops=dict(arrowstyle="->"))
        ax.set_xlabel("Froude number  Fr = u/c   (criticality at Fr = 1)")
        ax.set_ylabel("anticipatory advantage about own future state")
        ax.set_title("Anticipation is gated by the flow regime")
        ax.legend(fontsize=9)
        fig.tight_layout()
        ppath = outdir / f"moving_observer_demo_{stamp}.png"
        fig.savefig(ppath, dpi=130)
        result["plot"] = str(ppath)
        jpath.write_text(json.dumps(result, indent=2))
    except Exception as e:
        result["plot_error"] = repr(e)

    print(f"VERDICT: {verdict}   checks: P1={p1} P2={p2} P3={p3} P4={p4}")
    print(f"{'Fr':>6} {'c_up':>6} {'gap':>7} {'rho':>7} {'mse_anti':>9} {'advantage':>11} {'adv_95CI':>22} {'analytic':>9}")
    for r in rows:
        ci = f"[{r['advantage_ci'][0]:+.4f},{r['advantage_ci'][1]:+.4f}]"
        print(f"{r['Fr']:>6.2f} {r['c_up']:>6.2f} {r['gap']:>7.3f} {r['rho']:>7.4f} "
              f"{r['mse_anticipator']:>9.4f} {r['advantage']:>11.4f} {ci:>22} {r['analytic_advantage']:>9.4f}")
    print(f"\nwrote {jpath}")
    if "plot" in result:
        print(f"wrote {result['plot']}")


if __name__ == "__main__":
    main()
