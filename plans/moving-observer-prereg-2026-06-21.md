# Pre-Registration — Moving-Observer Anticipation Experiment (2026-06-21)

**Authoritative, dated, written BEFORE the evaluation code exists.**
Evaluation script: `research/moving_observer_demo.py`.
Parent plan: `plans/defensible-frontier-2026-06-21.md`, Step 3. This is the name-claim.

Reuses the inference machinery validated in the retrodiction experiment (Step 2),
turned now on the harder *forward-time* direction.

---

## 1) Setup (plain physics)

A boundary sits at `x = L = 1` and carries a fluctuating state `B(t)`, an
Ornstein–Uhlenbeck process with correlation time `T_c` (so `corr(B_s, B_t) =
exp(-|t-s|/T_c)`, variance `σ² = 1`). The flow moves downstream at speed `u`; surface
waves travel at `c = 1`, so the **Froude number is `Fr = u`** and boundary news
propagates *upstream* at `c_up = c - u = 1 - Fr`.

An **observer advects downstream with the flow** toward the boundary. Its **own future
arrival-state** is `B(t_arr)` — the boundary condition it will physically experience.
At a fixed lead time `ℓ` before arrival, it predicts `B(t_arr)` using the freshest
upstream news it has received. That news concerns boundary-time `t_arr - Δ`, where the
propagation geometry gives the **boundary-time gap**

```
    Δ(Fr) = ℓ / (1 - Fr).
```

As `Fr → 1` the upstream channel pinches shut (`c_up → 0`), `Δ → ∞`, and the freshest
news concerns a boundary-time infinitely far from the target.

## 2) Observers

- **Anticipator (channel on):** knows `B(t_arr - Δ)`; Bayes-optimal predictor
  `ρ_Δ · B(t_arr - Δ)` with `ρ_Δ = exp(-Δ/T_c)`. MSE `= σ²(1 - ρ_Δ²)`.
- **Channel-removed twin:** no upstream news; predicts the prior mean 0. MSE `= σ²`.
- **History-only forecaster:** uses only the observer's own local advected state, which
  is uncorrelated with the exogenous boundary. MSE `= σ²`.

**Anticipatory advantage:** `A(Fr) = σ² - MSE_anticipator = σ² · ρ_Δ² =
exp(-2ℓ / ((1 - Fr) · T_c))`.

### Locked parameters
`σ² = 1`, `T_c = 1.0`, `ℓ = 0.5`,
`Fr ∈ {0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99}`,
`n_trials = 50000`, bootstrap `= 1000`, seed fixed in script.

---

## 3) Pre-registered predictions (locked before any run)

- **P1 — Monotonic regime-gating.** `A(Fr)` is non-negative and monotonically
  **decreasing** in `Fr`.
- **P2 — FALSIFIER, collapse at criticality.** `A(Fr → 1) → 0`: at `Fr = 0.99` the
  advantage is within Monte-Carlo noise of 0 (95% CI includes 0, point `< 0.01`). **If
  the advantage does NOT collapse as the flow approaches critical, the effect is coming
  from inference rather than the channel, and the anticipation claim FAILS.**
- **P3 — Real anticipation at low Fr.** At `Fr = 0.1` the advantage is significantly
  positive (95% CI excludes 0): the channel delivers genuine advance information about
  the observer's own future arrival-state.
- **P4 — Estimator validation.** MC-measured `A(Fr)` matches the analytic `ρ_Δ²` within
  a Bonferroni family-wise 95% CI at every `Fr`.

### Pass/fail
**PASS** iff P1, P2, P3, P4 all hold. **P2 is the decisive falsifier**: it is the
regime-gating — an advantage that switches off exactly where the physical channel
closes, which a pure forecaster has no reason to reproduce.

---

## 4) What this does and does NOT show (claim discipline)

- **Shows (defensible):** an advecting observer gains anticipatory information about its
  own future state through the upstream channel, and that advantage is **gated by the
  flow regime** — it collapses precisely as the channel physically closes at `Fr → 1`.
  This is the discriminating signature (mechanism, not inference).
- **Does NOT show:** superiority over a forecaster that *also* has channel access. Under
  Markovian (OU) dynamics the freshest channel sample is a sufficient statistic, so
  "history of channel readings" and "anticipator" coincide; the honest contrast is
  channel vs. no-channel, with the exogenous target making both baselines equal `σ²`.
- **Open (next):** a *partially predictable* boundary (a slow inferable trend plus
  noise) would give a history-only forecaster a real foothold. Testing whether the
  channel advantage survives *above* that forecaster — and whether it stays Fr-gated —
  is the genuinely hard follow-up. Flagged, not claimed.

---

## 5) Outcome (2026-06-21, appended after running)

`research/moving_observer_demo.py` → `memory/research/moving_observer_results_20260621.json`,
plot `moving_observer_demo_20260621.png`. **VERDICT: PASS (P1, P2, P3, P4).**

| Fr | c_up | gap Δ | advantage | analytic ρ² |
|----|------|-------|-----------|-------------|
| 0.10 | 0.90 | 0.556 | **0.330** (CI [0.322,0.340]) | 0.329 |
| 0.50 | 0.50 | 1.000 | 0.137 | 0.135 |
| 0.80 | 0.20 | 2.500 | 0.008 | 0.007 |
| 0.90 | 0.10 | 5.000 | 0.0001 | 0.000 |
| 0.99 | 0.01 | 50.0 | **0.000** (CI [0,0]) | 0.000 |

- **P3 holds:** genuine anticipatory information about the observer's own future
  arrival-state at low Fr (advantage 0.33, CI excludes 0).
- **P2 (decisive falsifier) holds:** the advantage **collapses to 0 exactly as the
  flow approaches critical** — the upstream channel pinches shut (c_up → 0), and the
  anticipation switches off with it. This Fr-gating is the discriminating signature: a
  pure forecaster's accuracy has no reason to depend on the Froude number; the
  channel's does.
- **P1, P4 hold:** monotonic gating; MC matches analytic ρ² to ~0.006 (worst, mid-Fr)
  and to machine precision near criticality.

**Established (defensible):** anticipation of one's own future state via the upstream
channel is real and **physically regime-gated**. This is the temporal analogue of the
retrodiction result — same self-correcting machinery, now in the forward direction,
with the criticality collapse as the falsifiable fingerprint. The Markov-limit caveat
in §4 stands as the named next frontier.
