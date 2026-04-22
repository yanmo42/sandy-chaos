# Hyperstition Level-4 Ablation Comparison v0

**Date:** 2026-04-21  
**Owner surface:** sandy-chaos  
**Targets:** `SC-CONCEPT-0003`  
**Status:** bounded follow-on benchmark pass  
**Depends on:** `plans/hyperstition_level4_null_model_comparison_v0.md`, `spine/concepts/SC-CONCEPT-0003.yaml`, `nfem_suite/intelligence/cognition/hyperstition.py`, `scripts/hyperstition_ablation_compare.py`

---

## Purpose

The null-model pass already showed that the active hyperstition toy surface does something a dead baseline cannot.

That was necessary, but no longer sufficient.

This follow-on asks a harder question:

> Does Arm A still look meaningfully better when compared against stronger partial baselines rather than only a fully narrative-off null?

The goal is not to maximize raw paradox counts.
The goal is to see whether the active model preserves the more specific structural signature it claims to represent.

---

## Comparison family

### Arm A — narrative-on active model
Same parameter profile as the null-model pass:
- `observer_coupling = 0.9`
- `temporal_bias_gain = 3.0`
- other parameters matched to `paradox-v1`

### Arm B — null / narrative-off baseline
- `observer_coupling = 0.0`
- `temporal_bias_gain = 0.0`

### Arm C — passive-observer baseline
- `observer_coupling = 0.0`
- `temporal_bias_gain = 3.0`

Interpretation: temporal asymmetry is left nominally present, but cannot matter because action no longer feeds observation.

### Arm D — coupled observer, no temporal bias
- `observer_coupling = 0.9`
- `temporal_bias_gain = 0.0`

Interpretation: keep narrative-conditioned action feedback, remove the asymmetry channel that should create directional regime structure.

---

## Shared setup

- `initial_m = 0.6`
- `steps = 80`
- truth sweep `T ∈ [-0.8, 0.8]` on an 81-point grid
- temporal-asymmetry sweep `Δ ∈ [-0.8, 0.8]` on an 81-point grid
- total points per arm: `6561`

Artifacts written:
- `memory/research/hyperstition-v0/ablation_comparison_v0.json`
- `memory/research/hyperstition-v0/ablation_comparison_v0_delta_slices.csv`

Verification run:
```bash
./venv/bin/python -m unittest tests.test_hyperstition_dynamics -q
./venv/bin/python scripts/hyperstition_ablation_compare.py --out-dir memory/research/hyperstition-v0 --stem ablation_comparison_v0
```

Result: tests passed, comparison completed.

---

## Results

## Aggregate regime counts

### Arm A — narrative-on
- self-fulfilling: `1886`
- self-defeating: `1320`
- neutral: `3355`

### Arm B — null / narrative-off
- self-fulfilling: `0`
- self-defeating: `0`
- neutral: `6561`

### Arm C — passive-observer
- self-fulfilling: `0`
- self-defeating: `0`
- neutral: `6561`

### Arm D — coupled observer, no temporal bias
- self-fulfilling: `3240`
- self-defeating: `0`
- neutral: `3321`

---

## What changed under the stronger baseline

The important result is not that Arm A simply produces "more paradox" than every comparator.
That claim would be false.

Arm D produces **more self-fulfilling cases** than Arm A.
But it does so by collapsing the structure into a one-sided pattern:
- broad self-fulfilling corridor for `truth < 0`
- **no** self-defeating corridor for `truth > 0`

Arm A keeps the more specific two-sided structure:
- dominant self-fulfilling corridor for `truth < 0` across `Δ ∈ [-0.12, 0.8]`
- dominant self-defeating corridor for `truth > 0` across `Δ ∈ [-0.8, -0.16]`

So the active model’s advantage survives, but it survives as a **structural specificity** win, not as a raw-count win.

---

## Structural signature read

Using an 80%-dominance corridor threshold:

### Arm A
- negative-truth self-fulfilling corridor: **present**
- positive-truth self-defeating corridor: **present**
- bidirectional paradox coverage: **present**

### Arm B
- no dominant paradox corridors

### Arm C
- no dominant paradox corridors

### Arm D
- negative-truth self-fulfilling corridor: **present**
- positive-truth self-defeating corridor: **absent**
- bidirectional paradox coverage: **absent**

This is the cleanest discriminating result in the pass.
Temporal asymmetry is not needed to generate some paradoxical persistence at all.
It **is** needed, in the current toy family, to generate the more specific bidirectional regime split that makes the surface interesting rather than merely sticky.

---

## Separation vs Arm D

Compared with the strongest partial baseline (`arm_d_coupled_no_temporal_bias`):
- terminal sign disagreement: `2707 / 6561` (`41.3%`)
- terminal magnitude gap `> 0.25`: `2707 / 6561` (`41.3%`)
- regime disagreement: `2674 / 6561` (`40.8%`)

So the asymmetry channel is not a cosmetic tweak.
Removing it changes a large fraction of the grid and erases the self-defeating half of the paradox structure.

---

## What this supports

### Defensible now
- Passive-observer and fully narrative-off baselines collapse to neutral everywhere under this setup.
- Narrative-conditioned feedback alone can generate one-sided self-fulfilling persistence.
- The active Arm A profile still has a real discriminating advantage over stronger baselines, but the advantage is specifically **bidirectional corridor structure**, not maximal paradox volume.
- Temporal asymmetry currently appears to be the ingredient that opens the self-defeating corridor instead of merely amplifying persistence.

### Plausible but not yet proven
- Bidirectional paradox coverage is a better benchmark target for this surface than raw paradox counts.
- A compact Level-4 result packet for `SC-CONCEPT-0003` should probably foreground corridor topology and ablation structure rather than only aggregate totals.

### Still speculative
- Any claim that this toy family captures a general law of narrative causation.
- Any claim that the current corridor pattern will survive materially different update families without redesign.

---

## Failure envelope

This pass would have weakened the lane sharply if:
- Arm D reproduced the same bidirectional corridor structure as Arm A,
- passive-observer runs preserved paradox corridors,
- or the active model only beat weaker baselines on cosmetic magnitude differences.

That did **not** happen.

But the pass did falsify one lazier reading:
- "the active model is better because it creates more paradox regimes"

That is not the right benchmark language anymore.

---

## Disposition

- **result:** bounded follow-on pass supports keeping `SC-CONCEPT-0003` active
- **refined benchmark read:** evaluate for bidirectional corridor structure and directional regime specificity, not just paradox count
- **frontier effect:** the lane remains proof-bearing, but the next packet should tighten the scoring language before any broader promotion

---

## Next move

Do one narrow follow-on only:

1. write a compact Level-4 summary artifact that promotes **bidirectional corridor coverage** and corridor-boundary intervals as the primary benchmark criteria for this toy family,
2. include the null, passive-observer, and no-temporal-bias ablations as the minimum comparator set,
3. stop there unless a single clearer scalar metric falls out naturally.

Do **not** jump to schema hardening or broader theory expansion from this pass alone.
