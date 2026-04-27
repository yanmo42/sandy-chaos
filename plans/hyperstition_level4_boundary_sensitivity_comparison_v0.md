# Hyperstition Level-4 Boundary/Sensitivity Comparison v0

**Date:** 2026-04-27  
**Owner surface:** sandy-chaos  
**Targets:** `SC-CONCEPT-0003`  
**Status:** bounded stricter-separator pass — complete  
**Depends on:** `plans/hyperstition_level4_temporal_driver_comparison_v0.md`, `scripts/hyperstition_boundary_sensitivity_compare.py`

---

## Purpose

The temporal-driver comparator showed that bidirectional corridor coverage is too weak to separate Arm A from Arm E.
This pass tests the smallest stricter criteria named by the 2026-04-25 frontier note:

1. corridor-boundary geometry, and
2. initial-condition sensitivity.

The governing question is narrow:

> Does narrative-conditioned feedback produce a clean, inspectable separator against the open-loop temporal-driver comparator once simple corridor presence is no longer allowed as the winning criterion?

---

## Arms

### Arm A — narrative-on active model

```text
action = tanh(action_gain * (m + temporal_bias_gain * Δ))
observation = (1 - observer_coupling) * truth + observer_coupling * action
m_next = tanh(narrative_inertia * m + observation_gain * observation)
```

### Arm E — open-loop temporal-driver comparator

```text
action = tanh(action_gain * (temporal_bias_gain * Δ))
observation = (1 - observer_coupling) * truth + observer_coupling * action
m_next = tanh(narrative_inertia * m + observation_gain * observation)
```

Arm E still removes current narrative state from the action channel while preserving temporal asymmetry and observer coupling.

---

## Shared setup

- baseline initial narrative state for boundary geometry: `initial_m = 0.6`
- initial-condition sweep: `m₀ ∈ [-0.8, 0.8]`, 9 points
- steps: `80`
- truth sweep: `T ∈ [-0.8, 0.8]`, 81 points
- temporal-asymmetry sweep: `Δ ∈ [-0.8, 0.8]`, 81 points
- clean-gap threshold for candidate separation: `0.10` absolute fraction

Artifacts written:

- `memory/research/hyperstition-v0/boundary_sensitivity_comparison_v0.json`
- `memory/research/hyperstition-v0/boundary_sensitivity_comparison_v0_boundary_rows.csv`

Verification command:

```bash
python3 scripts/hyperstition_boundary_sensitivity_compare.py \
  --out-dir memory/research/hyperstition-v0 \
  --stem boundary_sensitivity_comparison_v0
```

---

## Results

| Metric | Arm A — narrative-on | Arm E — open-loop temporal driver | Absolute gap |
|---|---:|---:|---:|
| Boundary-edge fraction | 0.0125 | 0.0123 | 0.0002 |
| Terminal-state standard deviation | 0.8947 | 0.8634 | 0.0313 |
| Mean pairwise initial-condition regime disagreement | 0.3690 | 0.3252 | 0.0438 |
| Max pairwise initial-condition regime disagreement | 0.5850 | 0.4877 | 0.0972 |

Configured verdict: **`NO_CLEAN_SEPARATOR_FOUND`**.

The largest observed gap is max initial-condition sensitivity at `0.0972`, just below the configured `0.10` clean-gap threshold. That is suggestive enough to record, but not clean enough to rescue the active benchmark criterion without taste-language.

---

## Interpretation

### Defensible now

- Boundary-edge geometry is effectively indistinguishable between Arm A and Arm E under this grid.
- Initial-condition sensitivity is stronger in Arm A, but the measured separation does not clear the configured clean-gap threshold.
- The tested stricter criteria do **not** provide a clean replacement for the failed simple-corridor criterion.

### Plausible but unproven

- Narrative-conditioned feedback may still matter under a different criterion, such as path-dependence under perturbation, time-to-lock-in, or hysteresis across changing truth/temporal-asymmetry schedules.
- The observed sensitivity gap may become meaningful under a more carefully motivated benchmark, but this pass does not earn that claim.

### Speculative

- Any broad claim that this toy family uniquely isolates narrative feedback as the source of hyperstitional regime structure.
- Any claim that Arm E is theoretically superior rather than simply a strong stress-test comparator.

---

## Frontier implication

This satisfies the 2026-04-25 failure condition:

> If Arm A and Arm E cannot be cleanly separated by a stricter criterion without taste-language, then `SC-CONCEPT-0003` should lose the active frontier slot and the inventory should be reranked.

Therefore `SC-CONCEPT-0003` should remain a useful executable result surface, but it should not retain the active frontier slot by default.

---

## Disposition

- **result:** stricter-separator pass failed to find a clean Arm A vs Arm E separator
- **frontier effect:** demote `SC-CONCEPT-0003` from active frontier; rerank rather than defend rhetorically
- **promotion posture:** hold at bounded Level-4 pressure; do not broaden claims

---

## Smallest honest next move

Rerank the proof frontier.

Given the existing inventory, the strongest next candidate is likely `SC-CONCEPT-0004` because it has:

- executable substrate,
- named flat-baseline failure conditions,
- a real continuity/retrieval benchmark shape,
- and a clear skeptical reader question: does topology-aware retrieval beat at least one flat baseline while preserving readable path traces?

Do not reopen `SC-CONCEPT-0006` schema hardening as a reflex.
Do not continue adding ad hoc hyperstition comparators unless a new criterion is motivated before execution.
