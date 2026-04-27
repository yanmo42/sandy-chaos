# Hyperstition Level-4 Temporal-Driver Comparison v0

**Date:** 2026-04-25  
**Owner surface:** sandy-chaos  
**Targets:** `SC-CONCEPT-0003`  
**Status:** bounded stronger-comparator pass — complete  
**Depends on:** `plans/hyperstition_level4_robustness_pass_v0.md`, `scripts/hyperstition_temporal_driver_compare.py`, `nfem_suite/intelligence/cognition/hyperstition.py`

---

## Purpose

The robustness pass closed the small-perturbation stability concern, but left one stronger failure condition open:

> a stronger baseline preserves the same two-sided structure with less mechanism baggage.

This pass tests exactly one such comparator.
It preserves temporal asymmetry and observer coupling, but breaks narrative-conditioned feedback specifically.

The question is narrow:

> Does bidirectional corridor coverage require current narrative state inside the action channel, or can an open-loop temporal driver reproduce the same headline signature?

---

## Arms

### Arm A — narrative-on active model

Implemented model:

```text
action = tanh(action_gain * (m + temporal_bias_gain * Δ))
observation = (1 - observer_coupling) * truth + observer_coupling * action
m_next = tanh(narrative_inertia * m + observation_gain * observation)
```

This is the current Level-4 benchmark arm from the null, ablation, and robustness passes.

### Arm E — open-loop temporal-driver comparator

New comparator:

```text
action = tanh(action_gain * (temporal_bias_gain * Δ))
observation = (1 - observer_coupling) * truth + observer_coupling * action
m_next = tanh(narrative_inertia * m + observation_gain * observation)
```

Arm E keeps:
- `observer_coupling = 0.9`
- `temporal_bias_gain = 3.0`
- the same observation/update envelope
- the same grid and initial condition

Arm E removes:
- current narrative state `m` from the action channel

Interpretation: this is not a dead null and not just `observer_coupling = 0`.
It asks whether temporal asymmetry, when allowed to directly drive the action observation, is already sufficient to reproduce the two-sided corridor structure.

---

## Shared setup

- `initial_m = 0.6`
- `steps = 80`
- truth sweep `T ∈ [-0.8, 0.8]` on an 81-point grid
- temporal-asymmetry sweep `Δ ∈ [-0.8, 0.8]` on an 81-point grid
- total points per arm: `6561`
- corridor dominance threshold: `80%`

Artifacts written:
- `memory/research/hyperstition-v0/temporal_driver_comparison_v0.json`
- `memory/research/hyperstition-v0/temporal_driver_comparison_v0_delta_slices.csv`

Verification command:

```bash
python3 scripts/hyperstition_temporal_driver_compare.py \
  --out-dir memory/research/hyperstition-v0 \
  --stem temporal_driver_comparison_v0
```

---

## Results

## Aggregate regime counts

| Profile | Self-fulfilling | Self-defeating | Neutral |
|---|---:|---:|---:|
| Arm A — narrative-on | 1886 | 1320 | 3355 |
| Arm E — open-loop temporal driver | 1600 | 1600 | 3361 |

Arm E does not collapse to neutral.
It produces both paradox classes at roughly the same total volume as Arm A, but with a more symmetric split.

---

## Corridor signature

Using the same 80% dominance threshold:

| Profile | Negative-truth fulfillment corridor | Positive-truth defeat corridor | Bidirectional coverage |
|---|---|---|---|
| Arm A — narrative-on | present | present | Yes |
| Arm E — open-loop temporal driver | present | present | Yes |

Arm E reproduces the headline corridor criterion that the earlier result packet treated as Arm A's discriminating benchmark target.

---

## Separation from Arm A

Compared pointwise against Arm A across the 6561-grid:

- terminal sign disagreement: `573 / 6561` (`8.7%`)
- terminal magnitude gap `> 0.25`: `846 / 6561` (`12.9%`)
- terminal magnitude gap `> 0.50`: `711 / 6561` (`10.8%`)
- regime disagreement: `566 / 6561` (`8.6%`)

This is not identical behavior, but it is close enough to invalidate the stronger uniqueness claim.

---

## Interpretation

### Defensible now

- A stronger comparator that preserves temporal asymmetry while removing narrative-conditioned action feedback **does reproduce bidirectional corridor coverage** under the current benchmark.
- Therefore, bidirectional corridor coverage by itself is no longer a sufficient discriminating criterion for the current Arm A mechanism.
- The earlier result remains useful as an executable toy surface, but its strongest interpretation must be narrowed.

### Plausible but not yet proven

- Arm A may still differ from Arm E in boundary geometry, local transition shape, path dependence, or sensitivity to initial narrative state.
- Narrative-conditioned feedback may matter for a stricter criterion than simple corridor presence/absence.

### Still speculative

- Any broad claim that the current toy family uniquely isolates narrative feedback as the source of hyperstitional regime structure.
- Any claim that the open-loop comparator is a better model rather than a sharper stress test.

---

## Failure envelope update

The previous open failure condition was:

> stronger baseline preserves the same two-sided structure with less mechanism baggage.

Status: **observed under Arm E for the present corridor-presence criterion.**

This does not kill `SC-CONCEPT-0003`, but it does falsify the too-strong read:

> Arm A wins because only narrative-conditioned feedback plus temporal asymmetry can produce bidirectional corridor coverage.

That sentence should no longer be used.

---

## Disposition

- **result:** stronger-comparator stress test weakens the current benchmark target
- **frontier effect:** `SC-CONCEPT-0003` remains proof-bearing, but its active proof question must be reframed before promotion
- **promotion posture:** hold / revise; do not broaden claims

The lane still has value because the comparator result is informative and executable.
But the proof pressure has shifted from "confirm the corridor" to "find a stricter discriminating criterion, or rerank honestly."

---

## Smallest honest next move

Do **not** add another ad hoc comparator immediately.
First revise the benchmark criterion.

One bounded next step:

1. compare Arm A and Arm E on corridor-boundary geometry and initial-condition sensitivity,
2. keep only criteria that cleanly separate the two without taste-language,
3. if no such criterion appears, rerank the frontier instead of defending `SC-CONCEPT-0003` rhetorically.

Do **not** reopen symbolic-maps schema hardening as a reflex.
Do **not** promote the hyperstition result beyond Level 4 on the current evidence.
