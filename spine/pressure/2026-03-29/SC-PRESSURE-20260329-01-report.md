# SC-PRESSURE-20260329-01 Report

## Run target
- Concept: `SC-CONCEPT-0007` (`concept-pressure-lane-v1`)
- Lane type: workflow-review

## Planner output quality
- Claim tier selected: `plausible`
- Falsification framing present: yes
- Missing assumptions explicit: yes
- Next test explicit: yes

## Verifier outcome
- Structural schema compatibility: pass
- Required fields: pass
- Evidence references: pass (path-level)
- Disposition coherence: pass (`partial-support` + `KEEP_EXPLORING`)

## What worked
1. The lane now has clear stage boundaries.
2. The template reduced packet variability.
3. The pressure event captured disposition and next action in a compact format.

## Defects found (lane-level)
1. **Cross-run calibration gap**
   - One run is insufficient to trust disposition consistency.
   - Fix: run at least two existing concept nodes through the same lane and compare outcomes.

2. **Evidence quality depth not scored**
   - Current verifier checks presence of evidence links, not evidentiary strength.
   - Fix: add a simple evidence-strength heuristic in a follow-up validator pass.

## Immediate follow-up
- Execute next lane runs for `SC-CONCEPT-0003` and `SC-CONCEPT-0006`.
- Add a verifier warning threshold for sparse evidence with strong promotion recommendations.
