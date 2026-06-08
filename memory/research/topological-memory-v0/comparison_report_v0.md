# Topological Memory v0 — Task 5 Comparison

- Query count: **30**
- Top-k: **3**

## Baseline metrics

- **embedding**: unavailable (sentence-transformers unavailable: ModuleNotFoundError)
- **keyword**: hit@k=1.000, mrr=0.844
- **recency**: hit@k=0.100, mrr=0.100
- **topology**: hit@k=1.000, mrr=0.906

## Pairwise comparison

### topology_vs_keyword

- RR win/loss/tie: 5/2/23
- Hit win/loss/tie: 0/0/30

### topology_vs_recency

- RR win/loss/tie: 27/0/3
- Hit win/loss/tie: 27/0/3
- Topology-only hit queries:
  - Q-001: Where is the original archive draft for continuity retrieval?
  - Q-002: Which concept node owns the topological memory frontier?
  - Q-003: What note records runtime adoption for retrieval traces?
  - Q-004: Which prompt packet applies implementation pressure to this lane?
  - Q-005: Where is the bounded promotion gate summarized?
  - Q-006: Which todo checklist tracked the graph benchmark and comparison?
  - Q-007: What frontier file says SC-CONCEPT-0004 was active?
  - Q-008: Which architecture doc governs branch dispositions and cadence?
  - Q-009: What runtime code writes retrieval traces?
  - Q-010: What evaluator code compares keyword recency and topology?
  - Q-012: Where should a dispatched agent look for session resume context?
  - Q-013: After reading the runtime adoption note, what prompt should implement it?
  - Q-014: From the prompt packet, what code module handles runtime retrieval?
  - Q-015: From the prompt packet, what code module evaluates baselines?
  - Q-016: From the todo checklist, where is the provisional validation written?
  - Q-017: From the validation note, which concept receives provisional promotion?
  - Q-018: From the frontier note, which concept should be resumed?
  - Q-020: From the orchestrator contract, which checkpoint resumes the lane?
  - Q-021: Which evidence artifact names demotion conditions for this benchmark?
  - Q-022: Which file stores the frozen graph benchmark comparison checklist?
  - Q-023: Which doc provides continuity contract architecture for this retrieval lane?
  - Q-024: Which node links the archive draft to runtime adoption?
  - Q-025: Which node bridges adoption docs into code work?
  - Q-026: Which code path should produce inspectable path evidence?
  - Q-027: Which code path should preserve retrieval trace provenance?
  - Q-029: Which checkpoint says Symbolic Maps continuity work can resume?
  - Q-030: Which active frontier document should be reconciled after promotion?

## Verdict for Task 5

Topology retrieval beats recency on both hit-rate and MRR for this frozen fixture.
That is enough to mark Task 5 complete and proceed to promotion gating, bounded to this benchmark.
