# Topological Memory v0 — Promotion Gate Decision

## Date
2026-03-28

## Scope
Task 6 gate for:

> Only promote beyond archive if topology-aware retrieval beats at least one baseline with interpretable paths.

## Inputs frozen for this decision
- Graph fixture: `memory/research/topological-memory-v0/graph_v0.json`
- Query set: `memory/research/topological-memory-v0/benchmark_queries_v0.json`
- Baseline report: `memory/research/topological-memory-v0/baseline_report_v0.json`
- Comparison report: `memory/research/topological-memory-v0/comparison_report_v0.md`
- Comparison summary: `memory/research/topological-memory-v0/comparison_summary_v0.json`

Reproducibility note: trace decay scoring is anchored to the graph fixture `generated_at` timestamp (not wall-clock now), so reruns remain stable against frozen artifacts.

## Gate rubric
1. **Quantitative threshold:** topology must beat at least one flat baseline on benchmark metrics.
2. **Interpretability threshold:** topology outputs must expose inspectable path evidence.
3. **Boundedness threshold:** result remains explicitly provisional (not full canonical doctrine).

## Results
### Quantitative
- keyword: hit@3 `0.800`, MRR `0.750`
- recency: hit@3 `0.567`, MRR `0.467`
- topology: hit@3 `0.867`, MRR `0.728`
- embedding: unavailable in this environment (`sentence-transformers` missing)

Topology clearly beats **recency** on both hit-rate and MRR.
Topology also beats **keyword** on hit-rate, while trailing keyword slightly on MRR.

### Interpretability
Topology outputs include:
- `path_nodes`
- `path_edges`
- `path_summary` (human-readable relation chain)

Inspection surface:
```bash
python scripts/topological_memory_v0.py --inspect-query Q-001 --inspect-baseline topology
```

### Boundedness
Promotion target is intentionally conservative:
- Add a provisional validation note under `docs/notes/`
- Keep thesis draft in `docs/archive/` until stronger evidence (especially embedding + larger benchmark) is available.

## Verdict
**PASS (provisional)**

Task 6 criterion is met: topology beats at least one flat baseline and exposes interpretable path outputs.

## Failure conditions (for possible demotion)
Demote this promotion if any of the following occur on rerun:
1. Topology no longer beats at least one flat baseline.
2. Path outputs become non-interpretable or are removed.
3. Reproducibility fails against frozen artifacts.

## Next action
Run the same benchmark with an available embedding backend and re-check whether topology remains competitive on both hit-rate and MRR.
