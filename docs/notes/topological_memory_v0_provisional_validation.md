# Topological Memory v0 — Provisional Validation Note

## Status
Provisional promotion beyond archive (2026-03-28).

This note records that the bounded topological-memory lane met its initial promotion gate.
It is **not** a full canonical claim and does not replace stronger future validation.

## What passed
Using the frozen v0 graph + 30-query benchmark, topology-aware retrieval:
- beat **recency** on hit-rate and MRR,
- beat **keyword** on hit-rate,
- and emitted inspectable path evidence (`path_nodes`, `path_edges`, `path_summary`).

Artifacts:
- `memory/research/topological-memory-v0/comparison_report_v0.md`
- `memory/research/topological-memory-v0/comparison_summary_v0.json`
- `memory/research/topological-memory-v0/promotion_gate_v0.md`
- `memory/research/topological-memory-v0/promotion_gate_v0.json`

Reproducibility: trace decay is pinned to the graph fixture `generated_at` timestamp, so baseline reruns are stable over time.

## Claim tier
### Defensible now
A topology-aware retriever can outperform at least one flat baseline on this bounded continuity benchmark while producing interpretable path traces.

### Plausible but unproven
Topology may remain superior after adding stronger semantic baselines (embedding available) and larger query sets.

### Speculative
This result transfers broadly across other ecosystems without additional adaptation.

## Failure / demotion conditions
Demote this note if reruns show any of:
1. topology no longer beats at least one flat baseline,
2. path evidence becomes non-interpretable,
3. reproducibility breaks against frozen artifacts.

## Immediate next step
Run the same benchmark with embedding backend available, then reassess promotion level.
