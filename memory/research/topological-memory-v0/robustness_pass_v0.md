# SC-CONCEPT-0004 — Robustness Pass v0 (2026-06-17)

- Surface: topological-memory-continuity-retrieval
- Total perturbations: **20** (13 edge-drops + 7 weight-jitter)
- Collapsed: **4**
- Strong advantage (beats keyword) retained: **16/20**
- Gate advantage (beats recency) retained: **20/20**
- **Structural verdict: WEAKENED**

## Baseline (unperturbed)

- topology hit@3 = 1.000, keyword = 0.967, recency = 0.667

## Collapse definition (stated in advance)

- topology hit@3 <= keyword hit@3 (loses/ties strongest flat baseline) OR topology path evidence absent

## Collapsed perturbations

- drop_edge:E_ADOPTION_PROMPT: topology=0.967 keyword=0.967 path=True
- drop_edge:E_PROMPT_RUNTIME: topology=0.967 keyword=0.967 path=True
- drop_edge:E_PROMPT_EVAL: topology=0.967 keyword=0.967 path=True
- drop_edge:E_VALIDATION_CONCEPT: topology=0.967 keyword=0.967 path=True

## Interpretation

Flat baselines are edge-invariant; only topology is stressed. A STABLE verdict means topology's structural advantage survives dropping any single edge and +/-10% weight jitter — evidence the advantage is carried by connectivity rather than fixture memorization, **bounded to this fixture**.

