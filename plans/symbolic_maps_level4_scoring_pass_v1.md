# Symbolic Maps Level-4 Scoring Pass v1

**Date:** 2026-04-08  
**Owner surface:** sandy-chaos  
**Status:** active frontier bounded follow-on  
**Targets:** `SC-CONCEPT-0006`  
**Depends on:** `plans/symbolic_maps_level4_benchmark_v1.md`

---

## Purpose

Run the smallest honest four-artifact follow-on after the v0 scoring pass.

This note exists to answer one question:

> Does the Arm A advantage survive the addition of a semi-structured atlas artifact, or did the earlier result depend too heavily on prose-shaped sources?

Do not expand scope beyond this.

---

## Inputs

### Prior benchmark artifacts
- `plans/symbolic_maps_level4_benchmark_v0.md`
- `plans/symbolic_maps_level4/comparison_note_v0.md`
- `plans/symbolic_maps_level4_scoring_pass_v0.md`
- `plans/symbolic_maps_level4_benchmark_v1.md`

### Artifact 4 packets
- `plans/symbolic_maps_level4/extraction_04_starter_atlas.md`
- `plans/symbolic_maps_level4/baseline_04_starter_atlas.md`

---

## Scoring dimensions

Keep the same four dimensions:

1. **Cross-artifact consistency**
2. **Round-trip reconstructability**
3. **Schema completeness / structural coverage**
4. **Downstream reuse value**

### Score scale
- `0` = weak / absent
- `1` = partial / mixed
- `2` = clear strength

---

## What to look for in artifact 4

### Cross-artifact consistency
- Does Arm A align the atlas with the earlier role/operator/constraint/failure vocabulary cleanly?
- Does Arm B preserve the row logic but drift more in reusable slot alignment?

### Round-trip reconstructability
- Expect this to stay mixed or tied.
- The source is already structured, so a good baseline should remain strong here.

### Schema completeness / structural coverage
- Does Arm A capture all meaningful atlas structure without inflating vocabulary?
- Does Arm B preserve the logic but blur field-to-field comparability?

### Downstream reuse value
- Does Arm A create a more obvious bridge to later normalization, loader, or taxonomy work?
- Or does the semi-structured source erase most of that advantage?

---

## Artifact 4 scorecard

| Dimension | Arm A | Arm B | Notes |
| --- | --- | --- | --- |
| Cross-artifact consistency | 2 | 1 | Arm A aligns the atlas directly with the benchmark’s role/operator/constraint/failure vocabulary, which makes it easier to compare against the earlier three artifacts. Arm B preserves the row logic, but more of the reusable slot alignment dissolves back into summary prose. |
| Round-trip reconstructability | 2 | 2 | Both arms reconstruct the atlas well because the source is already compact, fielded, and semantically explicit. |
| Schema completeness / structural coverage | 2 | 1 | Arm A preserves nearly every meaningful slot in explicitly comparable form, including exclusion boundaries and reuse posture. Arm B captures the main logic faithfully, but field-to-field structural comparability becomes less inspectable once collapsed into prose. |
| Downstream reuse value | 2 | 1 | Arm A creates a clearer bridge to later normalization, lightweight loading, and taxonomy pressure. Arm B remains good for orientation, but weaker as a direct substrate for follow-on comparison or tooling. |

---

## Four-artifact totals

### Artifact totals

| Artifact | Arm A | Arm B |
| --- | --- | --- |
| Naming note | 8 | 5 |
| Rimuru specimen translation | 5 | 3 |
| Modules roadmap | 8 | 5 |
| Starter atlas | 8 | 5 |
| **Total** | **29** | **18** |

### Dimension totals

| Dimension | Arm A | Arm B |
| --- | --- | --- |
| Cross-artifact consistency | 7 | 3 |
| Round-trip reconstructability | 8 | 8 |
| Schema completeness / structural coverage | 7 | 4 |
| Downstream reuse value | 7 | 3 |

---

## Interpretation

The semi-structured atlas did **not** collapse Arm A’s advantage.
That is the main result of this pass.

### Confirmed again
- Arm A still has the clearest advantage in **cross-artifact consistency**.
- Arm A still has the clearest advantage in **structural coverage**.
- Arm A still has the clearest advantage in **downstream reuse**.

### Still mixed
- **Round-trip reconstructability** remains tied.
- The tie is more informative now, not less, because artifact 4 is exactly the kind of source where a fair loose baseline should remain strong.

### What changed relative to v0
The new artifact removes one easy explanation for Arm A’s earlier success.
It is no longer plausible to say the method only looked good because it imposed order on looser prose notes.

On a semi-structured atlas object, Arm A still adds value, mainly by:
- aligning the source to a reusable invariant vocabulary,
- preserving comparison-ready slots more explicitly,
- and making later normalization / loading pressure easier to imagine without pretending that hardening is already earned.

---

## Result

- **result:** stronger partial-support
- **disposition:** KEEP_ACTIVE_UNDER_BOUNDED_PRESSURE
- **promotion posture:** no broad hardening yet

`SC-CONCEPT-0006` still clearly justifies active-frontier status after the four-artifact pass.

The strongest currently supportable claim is now:

> Narrative-invariant / symbolic-map extraction continues to earn its keep primarily through comparison stability, structural coverage, and downstream reuse, and that advantage survives at least one slightly more heterogeneous semi-structured artifact rather than appearing only on prose-heavy notes.

---

## Hardening read

This pass does **not** justify broad validator/schema buildout yet.
But it does expose one repeated structural skeleton worth watching closely:

- role
- operator bundle
- constraint pattern
- failure mode
- boundary / exclusion condition

That is the first slot-family that looks plausibly hardenable later.
It is not yet a command to harden it now.
It is a candidate for the next narrow technical follow-on **if** you choose to convert bounded proof pressure into one small formalization move.

---

## Recommendation

### Recommended next move
Choose **one narrow structural-slot test** rather than broad schema expansion.

Best candidate:
- test whether the repeated `role / operators / constraints / failure / boundary` skeleton can be expressed in one tiny normalization draft without overfitting the current four artifacts.

### Do not do next
- do not reopen frontier ranking
- do not broaden the corpus dramatically
- do not build a large validator stack
- do not pretend Level 5 has been earned

---

## Immediate next action

Keep `SC-CONCEPT-0006` as the active frontier.
If you want to continue pressing it, the cleanest next move is:

1. draft one **minimal normalization sketch** for the repeated structural skeleton,
2. test it against these four artifacts only,
3. and reject it immediately if it creates hollow formality instead of cleaner comparison leverage.
