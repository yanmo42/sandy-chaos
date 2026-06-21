#!/usr/bin/env python3
"""
Retrodiction Experiment — Step 2 of plans/defensible-frontier-2026-06-21.md

Predictions/thresholds are committed, dated, in a separate artifact written before
any code: plans/retrodiction-prereg-2026-06-21.md  (predictions P1-P4 + the v2
correction note appended after the first run).

CORRECTION HISTORY (kept transparent, not hidden):
  v1 (preserved in memory/research/retrodiction_results_20260621.json) coupled the
  contemporaneous forecaster's record count to gamma (N_now ~ Poisson(gamma*eps)),
  which let the forecaster benefit from dissipation. That is unphysical: at the event
  instant t0 no records have formed yet, regardless of gamma -- records form AFTER the
  event. v1 was therefore FALSIFIED on the monotonicity prediction P1 (the advantage
  peaked then declined as the forecaster caught up). The pre-registration caught it.

  v2 (this file) fixes the model: the contemporaneous forecaster gets a FIXED look of
  N0 records (independent of gamma); the future observer inherits that same look PLUS
  the records that accumulated afterward. The two observers now differ ONLY by
  post-event record accumulation -- the clean isolation the prereg's anti-triviality
  clause demands. P4 now uses the correct paired-residual test.

Claim under test (plain physics): a FUTURE observer reconstructs a PAST event better
than the best CONTEMPORANEOUS forecaster, and that advantage is gated by irreversible
record/entropy production -- it must VANISH when records are suppressed (gamma -> 0).
"""

import json
import datetime
from pathlib import Path
import numpy as np

# ---- locked parameters ----
S0_2 = 1.0          # prior variance Var[X]
SOBS_2 = 1.0        # per-record observation noise variance
N0 = 1              # fixed contemporaneous look (records existing AT the event), gamma-independent
T = 1.0             # future readout time
GAMMAS = [0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0]   # record-production rate (dissipation knob)
N_TRIALS = 50000
N_BOOT = 1000
SEED = 20260621


def mmse(n):
    """Analytic Bayes posterior variance (= optimal-estimator MSE) given n records."""
    return 1.0 / (1.0 / S0_2 + n / SOBS_2)


def mutual_info_bits(n):
    """I(X; n records) for the Gaussian model, in bits."""
    return 0.5 * np.log2(1.0 + n * S0_2 / SOBS_2)


def posterior_mean(sum_records, n):
    precision = 1.0 / S0_2 + n / SOBS_2
    return (sum_records / SOBS_2) / precision


def simulate(gamma, rng):
    X = rng.normal(0.0, np.sqrt(S0_2), N_TRIALS)

    # contemporaneous forecaster: fixed look of N0 records (gamma-independent)
    n_now = np.full(N_TRIALS, N0)
    # future observer: same N0 look PLUS records accumulated after the event
    n_fut = N0 + rng.poisson(gamma * T, N_TRIALS)

    def sum_of_records(n):
        noise = np.where(n > 0, rng.normal(0.0, 1.0, N_TRIALS) * np.sqrt(np.maximum(n, 0) * SOBS_2), 0.0)
        return n * X + noise

    est_now = posterior_mean(sum_of_records(n_now), n_now)
    est_fut = posterior_mean(sum_of_records(n_fut), n_fut)

    sq_now = (est_now - X) ** 2
    sq_fut = (est_fut - X) ** 2
    adv = sq_now - sq_fut

    # paired residuals vs analytic MMSE (the correct P4 estimator-validation test):
    # for the optimal estimator, E[(est-X)^2 - mmse(n)] = 0.
    resid_now = sq_now - mmse(n_now)
    resid_fut = sq_fut - mmse(n_fut)

    idx = rng.integers(0, N_TRIALS, size=(N_BOOT, N_TRIALS))

    def ci(arr, lo=2.5, hi=97.5):
        b = arr[idx].mean(axis=1)
        return [float(np.percentile(b, lo)), float(np.percentile(b, hi))]

    # Bonferroni family-wise 95% over the 16 simultaneous residual tests
    # (8 gammas x 2 observers): per-test two-sided alpha = 0.05/16 -> 0.15625 / 99.84375
    BONF_LO, BONF_HI = 0.15625, 99.84375

    return {
        "gamma": gamma,
        "mean_N_now": float(n_now.mean()),
        "mean_N_future": float(n_fut.mean()),
        "error_forecaster": float(sq_now.mean()),
        "error_forecaster_ci": ci(sq_now),
        "error_future": float(sq_fut.mean()),
        "error_future_ci": ci(sq_fut),
        "advantage": float(adv.mean()),
        "advantage_ci": ci(adv),
        "analytic_error_forecaster": float(mmse(n_now).mean()),
        "analytic_error_future": float(mmse(n_fut).mean()),
        "resid_forecaster_ci": ci(resid_now, BONF_LO, BONF_HI),   # Bonferroni; should contain 0
        "resid_future_ci": ci(resid_fut, BONF_LO, BONF_HI),        # Bonferroni; should contain 0
        "mi_bits_future": float(mutual_info_bits(n_fut).mean()),
    }


def main():
    rng = np.random.default_rng(SEED)
    rows = [simulate(g, rng) for g in GAMMAS]

    advs = [r["advantage"] for r in rows]
    g0 = rows[0]
    # P1 non-negative & monotonically non-decreasing (MC-noise aware: "non-negative"
    # means never SIGNIFICANTLY negative, i.e. each advantage CI upper bound >= 0).
    nondec = all(advs[i + 1] >= advs[i] - 2e-3 for i in range(len(advs) - 1))
    not_sig_neg = all(r["advantage_ci"][1] >= 0.0 for r in rows)
    p1 = nondec and not_sig_neg
    # P2 decisive falsifier: advantage vanishes at gamma=0
    p2 = (g0["advantage_ci"][0] <= 0.0 <= g0["advantage_ci"][1]) and abs(g0["advantage"]) < 0.02
    # P4 estimator validation: paired residual consistent with 0 at every gamma
    p4 = all(r["resid_forecaster_ci"][0] <= 0.0 <= r["resid_forecaster_ci"][1]
             and r["resid_future_ci"][0] <= 0.0 <= r["resid_future_ci"][1] for r in rows)
    verdict = "PASS" if (p1 and p2 and p4) else "FAIL"

    result = {
        "experiment": "retrodiction_demo", "model_version": "v2",
        "date": datetime.date.today().isoformat(),
        "prereg": "plans/retrodiction-prereg-2026-06-21.md",
        "v1_preserved": "memory/research/retrodiction_results_20260621.json",
        "params": {"S0_2": S0_2, "SOBS_2": SOBS_2, "N0": N0, "T": T, "gammas": GAMMAS,
                   "n_trials": N_TRIALS, "n_boot": N_BOOT, "seed": SEED},
        "rows": rows,
        "checks": {"P1_monotonic_gating": bool(p1),
                   "P2_falsifier_vanishes_at_zero": bool(p2),
                   "P4_estimator_validation": bool(p4)},
        "verdict": verdict,
    }

    outdir = Path("memory/research")
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.date.today().strftime("%Y%m%d")
    jpath = outdir / f"retrodiction_results_v2_{stamp}.json"
    jpath.write_text(json.dumps(result, indent=2))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        gs = np.array(GAMMAS)
        ef = np.array([r["error_forecaster"] for r in rows])
        eu = np.array([r["error_future"] for r in rows])
        ad = np.array([r["advantage"] for r in rows])
        mi = np.array([r["mi_bits_future"] for r in rows])
        ad_lo = np.array([r["advantage_ci"][0] for r in rows])
        ad_hi = np.array([r["advantage_ci"][1] for r in rows])

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))
        ax1.plot(gs, ef, "o-", label="contemporaneous forecaster error (fixed look)")
        ax1.plot(gs, eu, "s-", label="future observer error")
        ax1.fill_between(gs, ad_lo, ad_hi, alpha=0.2, color="green")
        ax1.plot(gs, ad, "^-", color="green", label="retrodictive advantage (95% CI)")
        ax1.axhline(0, color="k", lw=0.6)
        ax1.set_xlabel("record-production rate  gamma  (dissipation knob)")
        ax1.set_ylabel("squared error / advantage")
        ax1.set_title("v2: advantage gated by record production, monotonic")
        ax1.legend(fontsize=8)
        ax1.annotate("gamma=0: no post-event records,\nadvantage -> 0 (falsifier)",
                     xy=(0, 0), xytext=(6, 0.15), fontsize=8, arrowprops=dict(arrowstyle="->"))
        ax2.plot(mi, ad, "^-", color="green")
        ax2.set_xlabel("info about past in present records  I(X; records)  [bits]")
        ax2.set_ylabel("retrodictive advantage")
        ax2.set_title("advantage tracks stored past-information")
        fig.tight_layout()
        ppath = outdir / f"retrodiction_demo_v2_{stamp}.png"
        fig.savefig(ppath, dpi=130)
        result["plot"] = str(ppath)
        jpath.write_text(json.dumps(result, indent=2))
    except Exception as e:
        result["plot_error"] = repr(e)

    print(f"VERDICT: {verdict}   checks: P1={p1} P2={p2} P4={p4}")
    print(f"{'gamma':>7} {'N_fut':>7} {'err_F':>8} {'err_R':>8} {'advantage':>11} {'adv_95CI':>22} {'MI_bits':>8}")
    for r in rows:
        ci = f"[{r['advantage_ci'][0]:+.4f},{r['advantage_ci'][1]:+.4f}]"
        print(f"{r['gamma']:>7.1f} {r['mean_N_future']:>7.2f} {r['error_forecaster']:>8.4f} "
              f"{r['error_future']:>8.4f} {r['advantage']:>11.4f} {ci:>22} {r['mi_bits_future']:>8.4f}")
    print(f"\nwrote {jpath}")
    if "plot" in result:
        print(f"wrote {result['plot']}")


if __name__ == "__main__":
    main()
