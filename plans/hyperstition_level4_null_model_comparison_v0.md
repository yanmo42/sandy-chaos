# Hyperstition Level-4 Null-Model Comparison v0

**Date:** 2026-04-20  
**Owner surface:** sandy-chaos  
**Status:** bounded follow-on pass  
**Targets:** `SC-CONCEPT-0003`  
**Depends on:** `plans/today_frontier_2026-04-18.md`, `spine/concepts/SC-CONCEPT-0003.yaml`, `nfem_suite/intelligence/cognition/hyperstition.py`, `scripts/hyperstition_phase_sweep.py`, `tests/test_hyperstition_dynamics.py`

---

## Purpose

Run the smallest discriminating follow-on that the 2026-04-18 frontier note demanded:

> matched initialization, narrative-on vs narrative-off or null-model comparison, regime-difference reporting, explicit failure envelope.

This note does **not** broaden the theory.
It asks whether the currently implemented hyperstition toy model actually produces regime structure that disappears under a minimal null.

---

## Comparison shape

### Arm A — narrative-on hyperstition model
Parameter profile matched to the existing paradox tests:

- `narrative_inertia = 0.3`
- `social_coupling = 0.0`
- `observation_gain = 1.4`
- `observer_coupling = 0.9`
- `action_gain = 2.5`
- `temporal_bias_gain = 3.0`
- `noise_std = 0.0`

### Arm B — null / narrative-off baseline
Keep the same rollout shape and initialization, but remove the narrative-feedback and temporal-asymmetry machinery:

- same `narrative_inertia`, `social_coupling`, `observation_gain`, `action_gain`, `noise_std`
- set `observer_coupling = 0.0`
- set `temporal_bias_gain = 0.0`

Interpretation:
Arm B still rolls forward causally, but it no longer lets narrative-conditioned action feedback or temporal asymmetry reshape attractor entry.

### Shared setup

- `initial_m = 0.6`
- `steps = 80`
- truth sweep: `T ∈ [-0.8, 0.8]` on an 81-point grid
- temporal-asymmetry sweep: `Δ ∈ [-0.8, 0.8]` on an 81-point grid
- total grid points: `6561`

---

## What was executed

### Existing executable checks

Confirmed the current test surface still passes:

```bash
./venv/bin/python -m unittest tests.test_hyperstition_dynamics -q
```

Result: `Ran 4 tests ... OK`

Those tests already establish that the active profile can exhibit:
- unstable center + stable outer branches,
- symmetry breaking under temporal asymmetry,
- self-fulfilling regime construction,
- self-defeating regime construction.

### Additional bounded comparison pass

Executed a grid comparison over the full `(truth, temporal_asymmetry)` surface for both arms and recorded:
- self-fulfilling counts,
- self-defeating counts,
- sign-disagreement rate between Arm A and Arm B terminal states,
- large-magnitude disagreement rate (`|m_A - m_B| > 0.25`),
- quadrant behavior for truth-sign / asymmetry-sign combinations.

Also generated the current Arm A artifact package with the existing phase-sweep script:
- `memory/research/hyperstition-v0/paradox_phase_diagram_v0.csv`
- `memory/research/hyperstition-v0/paradox_phase_diagram_v0_summary.json`
- `memory/research/hyperstition-v0/paradox_phase_diagram_v0.png`

---

## Results

## Aggregate counts

Across all `6561` grid points:

### Arm A — narrative-on
- self-fulfilling: `1886`
- self-defeating: `1320`
- neutral: `3355`

### Arm B — null baseline
- self-fulfilling: `0`
- self-defeating: `0`
- neutral: `6561`

### Cross-arm separation
- terminal sign disagreement: `3239 / 6561` (`49.4%`)
- large terminal magnitude difference (`> 0.25`): `4999 / 6561` (`76.2%`)

This is a real discriminating separation, not a cosmetic one.

---

## Regime structure by quadrant

### `truth < 0`, `Δ > 0`
- Arm A: `1600 / 1600` self-fulfilling
- Arm B: `0 / 1600` paradox cases
- sign disagreement: `1600 / 1600`

This is the cleanest fulfillment corridor.
A positive asymmetry bias preserves the initially positive narrative even against opposing truth.

### `truth > 0`, `Δ < 0`
- Arm A: `1320 / 1600` self-defeating
- Arm B: `0 / 1600` paradox cases
- sign disagreement: `1320 / 1600`

This is the cleanest defeat corridor.
A negative asymmetry bias flips an initially truth-aligned narrative into the opposite basin across most of the quadrant.

### `truth > 0`, `Δ > 0`
- Arm A: `0 / 1600` paradox cases
- Arm B: `0 / 1600` paradox cases
- sign disagreement: `0 / 1600`

This is the aligned corridor.
Both arms settle compatibly when truth and asymmetry do not oppose the initial narrative.

### `truth < 0`, `Δ < 0`
- Arm A: `246 / 1600` self-fulfilling
- Arm B: `0 / 1600` paradox cases
- sign disagreement: `246 / 1600`

This is a mixed corridor rather than a clean paradox block.
The active model still produces a minority fulfillment wedge here, but not the broad clean separation seen in the two primary opposing-sign quadrants.

---

## What this supports

### Defensible now
- The currently implemented hyperstition toy model produces a bounded bifurcation-like regime surface that is absent in the null baseline.
- Narrative-conditioned action feedback plus temporal asymmetry create discriminable self-fulfilling and self-defeating regions without requiring backward causation.
- `SC-CONCEPT-0003` now has a real Level-4-style comparison artifact rather than only a named toy mechanism.

### Plausible but not yet proven
- The regime boundary is structured enough to support a more formal bifurcation-oriented reporting layer.
- This toy result may be outsider-legible if rendered cleanly as phase diagrams / tables rather than kept as raw counts.

### Still speculative
- Any claim that this toy surface generalizes beyond the present mean-field attractor construction.
- Any claim that hyperstition has been validated as a broad explanatory law rather than a bounded operational model.

---

## Failure envelope

The pass would have failed the frontier pressure test if any of the following had occurred:

- Arm B reproduced the same paradox regimes after narrative feedback and temporal asymmetry were removed.
- Cross-arm separation collapsed to tiny local pockets with no legible corridor structure.
- The result depended on retrocausal language rather than forward action-selection differences.
- Existing tests failed, implying the comparison sat on unstable code rather than an executable substrate.

That failure did **not** happen here.

But important limits remain:

- this is still one toy family, not a multi-model replication
- the null is intentionally minimal, not a strong competing controller baseline
- the current pass reports strong counts, but not yet a formal boundary estimator or figure package in-repo

---

## Disposition

- **result:** bounded null-model discrimination confirmed
- **frontier effect:** supports keeping `SC-CONCEPT-0003` in the active slot
- **promotion posture:** stronger than pure framing, but not yet ready for broad theoretical promotion

This is enough to justify the 2026-04-18 rerank.
The hyperstition surface now clearly outperforms an immediate null in regime expressivity.

---

## Next move

Do **one** narrow follow-on, not a broad expansion:

1. package this pass into a stable artifact set, preferably with a saved CSV/JSON/PNG output path under `memory/research/`, and
2. add one explicit boundary-summary layer that names where fulfillment, defeat, and neutral regions begin/end.

Do **not** jump yet to larger theory rewrite or claim inflation.
Do **not** reopen `SC-CONCEPT-0006` hardening pressure.

If a stronger baseline later erases the current separation, rerank again honestly.
If the separation survives figure packaging and one stronger comparator, `SC-CONCEPT-0003` has a credible case for a more mature Level-4 result packet.
