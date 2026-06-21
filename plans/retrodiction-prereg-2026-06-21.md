# Pre-Registration — Retrodiction Experiment (2026-06-21)

**Authoritative, dated, written BEFORE the evaluation code exists.**
Evaluation script: `research/retrodiction_demo.py` (written after this file).
Parent plan: `plans/defensible-frontier-2026-06-21.md`, Steps 1–2.

This file fixes the E1 weakness flagged in the 2026-06-10 audit: predictions and
pass/fail thresholds are committed here, in a separate artifact, *before* results
are seen.

---

## 1) Definition of the observable (the gateway — Step 1)

Let `X` be a hidden **past event** value, set at event time `t0` and drawn from a
prior `X ~ N(0, σ0²)`.

Define an observer's **reconstruction error** as the expected squared error of its
Bayes-optimal estimate of `X` given the information available to that observer.

- **Contemporaneous forecaster F** — has access to all records/evidence that exist
  within a short window at the event time `[t0, t0 + ε]`, plus the prior. Uses
  Bayes-optimal inference.
- **Future observer R** — has access to all records that exist at a later readout
  time `T ≫ ε`. Uses the **same** Bayes-optimal inference, the **same** prior, and
  the **same** noise model as F.

**Retrodictive extractive advantage:**  `A = Error_F − Error_R`.

### Anti-triviality requirement (why this is not just "a sensor helps")
F and R differ in **exactly one** thing: how many records exist at their respective
observation times. Same estimator, same prior, same noise. Therefore any `A > 0` is
attributable *solely to record accumulation between t0 and T* — not to a smarter
observer and not to a handicapped baseline. A plain sensor cannot manufacture `A`,
because at the event time the later records **do not exist yet**; they form
irreversibly afterward. This is the test that a thermometer fails: a thermometer
reading the present cannot beat itself, and at t0 the future records are simply
absent.

---

## 2) Model

- Records form as a **Poisson process with rate γ** (the control knob). Each record
  is a noisy copy `y_i = X + ε_i`, `ε_i ~ N(0, σobs²)`, independent.
- `γ` is a **dissipation / entropy-production rate**: each record is an irreversible
  imprint of `X` into the environment (a Landauer-style copy). `γ = 0` is the
  reversible, record-free regime.
- Records by event window: `N_now ~ Poisson(γ·ε)` (≈ 0 for small ε).
  Records by readout: `N_future ~ Poisson(γ·T)`.
- Bayes-optimal posterior given `n` records → posterior variance (the MMSE):
  `mmse(n) = 1 / (1/σ0² + n/σobs²)`. For the Gaussian conjugate model the expected
  squared error of the optimal estimator equals this posterior variance exactly.
- Information about the past held in the present records:
  `I(X; n records) = ½ log₂(1 + n·σ0²/σobs²)` bits.

### Fixed parameters (locked)
`σ0² = 1.0`, `σobs² = 1.0`, `ε = 0.02`, `T = 1.0`,
`γ ∈ {0, 0.5, 1, 2, 4, 8, 16, 32}` records/unit-time,
`n_trials = 20000`, bootstrap `= 1000` resamples, seed fixed in script.

---

## 3) Pre-registered predictions (locked before any run)

- **P1 — Monotonic gating.** `A(γ)` is non-negative and monotonically increasing in
  `γ` across the swept range.
- **P2 — FALSIFIER, vanishing at zero dissipation.** `A(γ→0) → 0` within Monte-Carlo
  error (the 95% CI at `γ = 0` includes 0; point estimate `|A| < 0.02`). **If `A`
  stays bounded away from 0 when records are suppressed, the effect is not
  record-driven and the retrodiction claim FAILS.**
- **P3 — Information accounting.** `I(X; present records)` is ≈ 0 at `γ = 0` and rises
  with `γ`; the advantage `A` rises together with it (the gap is bought by stored
  information about the past).
- **P4 — Estimator validation.** The Monte-Carlo measured errors for both observers
  match the analytic `mean_i mmse(N_i)` within the 95% CI at every `γ`. (This is the
  real reason to run the safe direction first: it proves the inference machinery and
  the forecaster baseline before we turn them on the harder anticipation test.)

### Pass/fail
**PASS** iff P1, P2, and P4 all hold. **P2 is the decisive falsifier.** P3 is
corroborating. A clean failure of P2 is itself a valid, reportable result (the
retrodictive advantage would then reduce to ordinary inference).

---

## 4) What a PASS does and does not buy

- **Does:** establishes — forward-causally, with a working estimator and an honest
  baseline — that a future observer extracts past information a contemporaneous
  observer could not, *and that the advantage is gated by irreversible record
  production* (vanishes with no dissipation). This is the defensible foundation.
- **Does not:** say anything about the *future*. That is the separate, harder
  moving-observer test (Step 3), which reuses this validated machinery.

---

## 5) Outcome (2026-06-21, appended after running — history annotated, not rewritten)

**Run v1** (`memory/research/retrodiction_results_20260621.json`): **FAIL.**
- P2 (decisive falsifier) **passed** — advantage exactly 0 at γ=0.
- P1 (monotonic) **falsified** — and correctly so. v1 coupled the *contemporaneous*
  forecaster's record count to γ (`N_now ~ Poisson(γ·ε)`), so at extreme dissipation
  the forecaster caught up and the advantage *peaked at γ=8 then declined*. This is
  unphysical: at the event instant no records have formed yet, regardless of γ. The
  pre-registration caught my own naive model. This is the self-correcting loop working.
- P4 machinery was sound (MC vs analytic agreed to ~0.003); the strict CI-containment
  test was mis-specified.

**Run v2** (`memory/research/retrodiction_results_v2_20260621.json`,
plot `retrodiction_demo_v2_20260621.png`): **PASS (P1, P2, P4).**
- Corrected model: forecaster gets a fixed contemporaneous look (N0=1, γ-independent);
  the future observer inherits it plus post-event records. The two now differ *only*
  by record accumulation.
- Corrected statistics: non-negativity is MC-noise-aware; the 16 simultaneous residual
  tests use a Bonferroni family-wise 95% correction.
- **Result:** forecaster error flat at 0.50; future-observer error falls 0.498 → 0.030;
  retrodictive advantage rises monotonically 0 → 0.473 (saturating toward the 0.50
  information ceiling), and **vanishes at γ=0** (−0.0005, CI [−0.008, +0.007]). The
  advantage tracks the stored past-information `I(X; records)` (0 → 2.53 bits).

**What this establishes (defensible):** a future observer extracts past information a
contemporaneous observer cannot, the advantage is **gated by irreversible record
production** (zero dissipation → zero advantage), and the inference machinery +
honest forecaster baseline are validated. Ready for **Step 3** (moving-observer
anticipation), which reuses this machinery in the harder forward-time direction.
