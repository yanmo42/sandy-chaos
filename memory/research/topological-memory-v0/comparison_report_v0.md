# Topological Memory v0 — Task 5 Comparison

- Query count: **30**
- Top-k: **3**

## Baseline metrics

- **embedding**: unavailable (sentence-transformers unavailable: ModuleNotFoundError)
- **keyword**: hit@k=0.967, mrr=0.789
- **recency**: hit@k=0.667, mrr=0.300
- **topology**: hit@k=1.000, mrr=0.867

## Pairwise comparison

### topology_vs_keyword

- RR win/loss/tie: 6/3/21
- Hit win/loss/tie: 1/0/29
- Topology-only hit queries:
  - Q-025: Which node bridges adoption docs into code work?

### topology_vs_recency

- RR win/loss/tie: 26/0/4
- Hit win/loss/tie: 10/0/20
- Topology-only hit queries:
  - Q-001: Where is the original archive draft for continuity retrieval?
  - Q-002: Which concept node owns the topological memory frontier?
  - Q-012: Where should a dispatched agent look for session resume context?
  - Q-014: From the prompt packet, what code module handles runtime retrieval?
  - Q-017: From the validation note, which concept receives provisional promotion?
  - Q-018: From the frontier note, which concept should be resumed?
  - Q-020: From the orchestrator contract, which checkpoint resumes the lane?
  - Q-023: Which doc provides continuity contract architecture for this retrieval lane?
  - Q-024: Which node links the archive draft to runtime adoption?
  - Q-025: Which node bridges adoption docs into code work?

## Verdict for Task 5

Topology retrieval beats keyword, recency on both hit-rate and MRR for this frozen fixture.
That is enough to mark Task 5 complete and proceed to promotion gating, bounded to this benchmark.
