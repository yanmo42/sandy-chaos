# Topological Memory v0 — Task 5 Comparison

- Query count: **30**
- Top-k: **3**

## Baseline metrics

- **embedding**: unavailable (sentence-transformers unavailable: ModuleNotFoundError)
- **keyword**: hit@k=0.800, mrr=0.750
- **recency**: hit@k=0.567, mrr=0.467
- **topology**: hit@k=0.867, mrr=0.728

## Pairwise comparison

### topology_vs_keyword

- RR win/loss/tie: 4/5/21
- Hit win/loss/tie: 3/1/26
- Topology-only hit queries:
  - Q-011: Where is the topology-aware retrieval scorer implementation located?
  - Q-026: Which artifact should anchor promotion decisions before moving topological-memory claims out of archive?
  - Q-028: What implementation-and-test pair currently grounds the topology-aware retriever?
- Baseline-only hit queries:
  - Q-002: Which TODO surface currently tracks the execution steps for topological memory?

### topology_vs_recency

- RR win/loss/tie: 11/5/14
- Hit win/loss/tie: 10/1/19
- Topology-only hit queries:
  - Q-006: Which document defines the canonical Ygg continuity architecture?
  - Q-007: What CLI surface provides status/checkpoint/promote for continuity operations?
  - Q-008: Where is the continuity checkpoint helper implementation for Ygg?
  - Q-015: Where is the protocol for pre-registration and scoring of predictive claims?
  - Q-016: Which doc catalogs paradox stress tests for informational and causal edge cases?
  - Q-018: What script checks claim-to-source mapping completeness in research syntheses?
  - Q-019: Which tests confirm the research verifier behavior?
  - Q-021: What script builds lane-aware task contracts from TODO surfaces?
  - Q-022: What script dispatches orchestrator task contracts through the gateway bridge?
  - Q-023: What script drives daily/weekly cadence summaries for self-improvement loops?
- Baseline-only hit queries:
  - Q-002: Which TODO surface currently tracks the execution steps for topological memory?

## Verdict for Task 5

Topology retrieval outperforms at least one flat baseline (recency) on both hit-rate and MRR, and beats keyword on hit-rate while trailing slightly on MRR.
That is enough to mark Task 5 complete and proceed to deeper evaluation/promotion gating.
