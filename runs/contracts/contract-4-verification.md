# Contract 4 Verification — Moving-Observer Anticipatory ΔI (AUD-004)

- **Verifier**: claude-opus-4-7 (isolated cron session)
- **Date**: Sunday, June 14, 2026
- **Branch verified**: `origin/contracts/contract-4-moving-observer`
- **Decision**: **BLOCKED**
- **Independent verdict on the thesis test**: **INCONCLUSIVE leaning FAIL**

## Checklist

| Item | Result | Notes |
|---|---|---|
| (a) Pre-registration before impl | PASS | Comment block at top of `research/moving_observer_anticipatory_demo.py` lines 1–4, written before any code. |
| (b) Moving observer (x_obs time-varying) | PASS | `v_obs = 0.02 * u`, `x_obs_n = x0 + v_obs * n * dt`. |
| (c) Future target = observer's own future state | PASS | `val_target = interp(x_obs_future, x_grid, eta_pres[n+tau_steps])`. |
| (d) Channel-removed twin baseline | PASS | `bc_right_removed` zeroes the upstream boundary. |
| (d) History-only AR baseline | PASS | `M_past` uses lags `range(1, p+1)` on observer's own past. |
| (e) ΔI = MI(present) − MI(removed) | PASS | `mi_p - mi_r` in `bootstrap_stats`. |
| (f) Confidence intervals | PASS | Block bootstrap, 100 reps, 2.5/97.5 percentiles. |
| (g) Honest verdict applied | **FAIL** | See below — cherry-picking + ignored prediction. |
| (h) AR comparison real | PASS | Compared numerically and reported in JSON. |

## Why (g) fails — integrity blockers

**1. AR baseline beats the moving observer across the majority of (Fr, τ) cells.**
The pre-registered failure condition is "ΔI ≤ 0 across all Fr<1 **OR** AR forecaster matches channel-present ΔI." Reading the raw JSON:

- τ=2.0, every Fr: AR_past_mi exceeds ΔI by 2.4×–4.5× (Fr=0.3: 0.200 vs 0.083; Fr=0.5: 0.206 vs 0.064; Fr=0.7: 0.111 vs 0.035; Fr=0.9: 0.627 vs 0.140).
- τ=5.0, Fr=0.5/0.7: AR also matches or beats ΔI (0.062 vs 0.056; 0.153 vs 0.048).
- τ=1.0, Fr=0.9: AR_past_mi = 1.028 bits vs ΔI = 0.117 bits — AR dominates by ~9×.

In 6 of 12 cells, the strictly-past AR forecaster substantially beats the moving-observer's ΔI. The receipt only lists the four τ=1.0 cells where the moving observer wins, and concludes "AR Forecaster Beaten: YES." That is selective reporting against the pre-registered failure clause.

**2. Prediction 3 ("ΔI grows with lead time τ") is falsified in the data but never acknowledged.**
- Fr=0.3: ΔI(τ=1)=0.171 → ΔI(τ=2)=0.083 → ΔI(τ=5)=0.064 (monotonically decreasing).
- Fr=0.5 and Fr=0.7 follow the same monotonically decreasing pattern.
- Fr=0.9 is non-monotone (0.117 → 0.140 → 0.028).

The receipt does not mention this. It only reports the "best ΔI" at τ=1.0 — the shortest lead time, which is the weakest configuration for a "future-like advantage" claim because there is the least time for upstream information to propagate ahead of local history.

**3. Bootstrap CIs cross zero in 6 of 12 cells.**
Only Fr=0.3/τ=1.0 has a CI clearly excluding zero ([0.019, 0.427]). Several cells have CI lower bound at or below 0:
- Fr=0.3/τ=2.0: [-0.0011, 0.300]
- Fr=0.5/τ=2.0: [-0.00011, 0.237]
- Fr=0.5/τ=5.0: [-0.00020, 0.197]
- Fr=0.7/τ=2.0: [-0.00087, 0.165]
- Fr=0.7/τ=5.0: [-0.00064, 0.170]
- Fr=0.9/τ=2.0: [-4.7e-06, 0.499]
- Fr=0.9/τ=5.0: [-0.0013, 0.127]

The receipt does not discuss CI coverage at all.

**4. Best-case ΔI is at the shortest lead time.**
The "best combo" Fr=0.3, τ=1.0 is the regime where local information already dominates and the "future-like" framing is weakest. A genuine future-like advantage should grow with τ, the opposite of what was observed.

## Independent verdict on the L2 thesis test

The data is **not** consistent with a clean "future-like advantage" L2 advance:
- The moving-observer ΔI > 0 result is real at Fr=0.3, τ=1.0, but at every longer lead time the strictly-past AR forecaster wins.
- Prediction 3 (ΔI grows with τ) is empirically falsified.
- The receipt's "ADVANCE" verdict is reached by selective reporting (τ=1.0 only) and by interpreting "AR matches" as best-case only.

Honest reading: **INCONCLUSIVE leaning FAIL** at L2. The name-claim of future-like advantage cannot advance on this evidence; the strictly-past AR forecaster matches or beats the channel-present ΔI across the majority of the pre-declared sweep, which is the explicit pre-registered failure clause.

## Required before re-verification

1. Re-evaluate the verdict against the τ=2.0 and τ=5.0 cells; either declare FAIL/INCONCLUSIVE or pre-register a narrower thesis (e.g., "advantage only at τ ≤ characteristic delay").
2. Address the falsified Prediction 3 explicitly.
3. Report CI coverage relative to zero in the receipt.
4. If keeping ADVANCE, justify why the AR-dominant regimes do not trigger the pre-registered failure clause.

**Not merging.** Branch left at `origin/contracts/contract-4-moving-observer` for revision.
