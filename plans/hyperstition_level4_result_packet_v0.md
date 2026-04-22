# Hyperstition Level-4 Result Packet v0

**Date:** 2026-04-21  
**Owner surface:** sandy-chaos  
**Targets:** `SC-CONCEPT-0003`  
**Status:** compact Level-4 result packet  
**Depends on:** `plans/hyperstition_level4_null_model_comparison_v0.md`, `plans/hyperstition_level4_ablation_comparison_v0.md`, `nfem_suite/intelligence/cognition/hyperstition.py`, `scripts/hyperstition_ablation_compare.py`

---

## 1) Claim

### Defensible now
In the current hyperstition toy family, **narrative-conditioned feedback plus temporal asymmetry** yields a **bidirectional corridor structure** that the minimum comparator set does not reproduce.

More specifically:
- Arm A produces a dominant **self-fulfilling corridor** for `truth < 0`
- Arm A also produces a dominant **self-defeating corridor** for `truth > 0`
- the null and passive-observer baselines collapse to neutral
- the coupled no-temporal-bias baseline preserves only a one-sided self-fulfilling corridor and loses the self-defeating side entirely

This is a bounded toy-model result. It does **not** establish a general law of narrative causation.

### Plausible but not yet proven
For this surface, **bidirectional corridor coverage** is a better benchmark target than raw paradox counts.

### Still speculative
That the same corridor topology will survive materially different update families, richer agent models, or stronger competing baselines without redesign.

---

## 2) Mechanism surface

The executable mechanism lives in:
- `nfem_suite/intelligence/cognition/hyperstition.py`

The current bounded benchmark/packaging artifacts live in:
- `plans/hyperstition_level4_null_model_comparison_v0.md`
- `plans/hyperstition_level4_ablation_comparison_v0.md`
- `memory/research/hyperstition-v0/ablation_comparison_v0.json`
- `memory/research/hyperstition-v0/ablation_comparison_v0_delta_slices.csv`

This packet is about the **result shape**, not a broader theory rewrite.

---

## 3) Comparator set

All arms use:
- `initial_m = 0.6`
- `steps = 80`
- truth sweep `T ∈ [-0.8, 0.8]` on an 81-point grid
- temporal-asymmetry sweep `Δ ∈ [-0.8, 0.8]` on an 81-point grid
- total grid points per arm: `6561`

### Arm A — narrative-on active model
- `observer_coupling = 0.9`
- `temporal_bias_gain = 3.0`

### Arm B — null / narrative-off
- `observer_coupling = 0.0`
- `temporal_bias_gain = 0.0`

### Arm C — passive-observer
- `observer_coupling = 0.0`
- `temporal_bias_gain = 3.0`

### Arm D — coupled, no temporal bias
- `observer_coupling = 0.9`
- `temporal_bias_gain = 0.0`

---

## 4) Benchmark criteria

Primary criteria for this toy family:
1. **negative-truth self-fulfilling corridor present or absent**
2. **positive-truth self-defeating corridor present or absent**
3. **bidirectional corridor coverage present or absent**
4. **corridor-boundary intervals** under the declared dominance threshold
5. comparator collapse behavior

Secondary criteria only:
- aggregate self-fulfilling / self-defeating counts
- sign disagreement / magnitude-gap fractions

Reason: the stronger ablation pass showed that **more paradox volume is not the right win condition**.

---

## 5) Result table

Dominance threshold for corridor declaration: **80%** of a truth-band slice.

| Profile | Self-fulfilling | Self-defeating | Negative-truth fulfillment corridor | Positive-truth defeat corridor | Bidirectional coverage |
|---|---:|---:|---|---|---|
| Arm A narrative-on | 1886 | 1320 | `Δ ∈ [-0.12, 0.8]` | `Δ ∈ [-0.8, -0.16]` | Yes |
| Arm B null / narrative-off | 0 | 0 | none | none | No |
| Arm C passive-observer | 0 | 0 | none | none | No |
| Arm D coupled, no temporal bias | 3240 | 0 | `Δ ∈ [-0.8, 0.8]` | none | No |

Additional separation vs strongest partial baseline, Arm D:
- sign disagreement: `2707 / 6561` (`41.3%`)
- magnitude gap `> 0.25`: `2707 / 6561` (`41.3%`)
- regime disagreement: `2674 / 6561` (`40.8%`)

---

## 6) Discriminating read

### What the artifacts explicitly show
- Null and passive-observer baselines produce no dominant paradox corridors.
- The coupled no-temporal-bias baseline produces a broad one-sided self-fulfilling corridor and no self-defeating corridor.
- Arm A is the only arm in the current set that preserves **both** sides of the corridor structure.

### Interpretation
The active model’s surviving advantage is **structural specificity**.

Temporal asymmetry is not required to generate any paradox-like persistence at all.
It **is** required, in this toy family, to generate the more discriminating two-sided regime split that makes the surface worth carrying forward.

This is why the benchmark should now read:
- **Does the model preserve bidirectional corridor structure?**

not:
- **Does the model generate the largest number of paradox cases?**

---

## 7) Limits and failure envelope

This result packet would weaken sharply if any of the following occurs in the next bounded pass:
- Arm D reproduces the same bidirectional corridor structure as Arm A
- passive-observer or null baselines recover non-trivial paradox corridors under matched conditions
- corridor boundaries prove unstable under small parameter drift, making the present intervals accidental rather than structural
- a stronger baseline preserves the same two-sided structure with less mechanism baggage

Important current limits:
- one toy family only
- no multi-family replication yet
- no robustness sweep around the current profile yet
- still an internal result packet, not an external publication-grade benchmark

---

## 8) Disposition

### Defensible now
`SC-CONCEPT-0003` has a real Level-4-style proof object:
- executable mechanism
- explicit comparator set
- corridor-based benchmark criteria
- completed null and ablation result package
- declared failure envelope

### Not yet earned
- broad theoretical promotion
- claims of generality beyond the toy family
- any move into validator/schema hardening or adjacent-lane expansion from this result alone

### Frontier effect
Keep `SC-CONCEPT-0003` in the active slot.
The current pressure bottleneck is now **result legibility and tighter scoring language**, not missing evidence of any kind.

---

## 9) Smallest honest next move

If this lane receives one more bounded pass, it should be:
- a narrow robustness check around the current Arm A profile to test whether the corridor boundaries remain qualitatively stable under small parameter perturbations

Do **not** broaden theory first.
Do **not** reopen symbolic-maps pressure from here.
Do **not** treat this toy result as a general framework validation.
