# Research Backlog (Literature-Integrated Sandy Chaos)

Status legend: `[ ]` todo · `[~]` in progress · `[x]` done

## North Star

Build a repeatable pipeline that turns scientific literature into:

1. source-grounded claim graphs,
2. falsifiable Sandy Chaos hypotheses,
3. executable experiment tasks.

---

## Phase 0 — Protocol + Infrastructure (Foundational)

### 0.1 Ingestion protocolization

- [x] Create canonical ingestion protocol doc (`docs/research_ingestion_protocol.md`)
- [ ] Add protocol references to top-level docs index and workflow docs
- [ ] Define canonical cycle-id naming convention and artifact lifecycle

### 0.2 Data contracts

- [ ] Freeze `sources.csv` schema and validator
- [ ] Freeze `claims.csv` schema and validator
- [ ] Add migration note for schema version bumps (`schema_version` field)

### 0.3 Toolchain bridge (`ferroelectric-materials-project`)

- [ ] Add adapter spec for importing source metadata and extracted claim units
- [ ] Define stable ID mapping strategy (`source_id`, `claim_id`) across reruns
- [ ] Add smoke test: import 10 papers and generate deterministic artifact bundle

---

## Phase 1 — First production ingestion lane

### 1.1 Pilot topic (narrow)

- [ ] Topic: **Temporal asymmetry metrics under observer-coupled channels**
- [ ] Build `memory/research/<cycle-id>-query.md`
- [ ] Populate `<cycle-id>-sources.csv` with at least 15 high-quality sources
- [ ] Produce `<cycle-id>-claims.csv` with at least 60 atomic claims

### 1.2 Mapping and synthesis

- [ ] Map all claims to Sandy Chaos ontology anchors
- [ ] Generate dual-expression hypothesis blocks (formal + language)
- [ ] Label all hypotheses with claim tier and confidence

### 1.3 Falsification queue

- [ ] Define at least 5 high-value hypotheses with explicit null models
- [ ] Assign each hypothesis a measurable fail condition and threshold
- [ ] Emit implementation-ready experiment cards for simulation/tests

---

## Phase 2 — Verification + contradiction handling

### 2.1 Verifier extensions

- [ ] Extend verifier to check claim-tier consistency in hypothesis docs
- [ ] Add contradiction detector (claim-to-claim conflict scan)
- [ ] Add missing-citation detector for synthesis statements

### 2.2 Quality dashboards

- [ ] Add cycle-level metrics:
  - source count,
  - claim count,
  - contradiction count,
  - defensible/plausible/speculative distribution,
  - experiment queue depth
- [ ] Add trend snapshots in cycle summaries

---

## Phase 3 — Literature-grounded theory advancement

### 3.1 Open theoretical priorities (from `plans/todo.md`)

- [x] Specify hyperstition update function `\mathcal{G}` with toy model + fixed-point analysis (`nfem_suite/intelligence/cognition/hyperstition.py`, `tests/test_hyperstition_dynamics.py`)
- [ ] Benchmark Nested Temporal Domains neighbor-layer transfer against all-to-all and uncoupled baselines (`docs/13_nested_temporal_domains.md`)
- [ ] Anchor epistemic retro-influence framing in formal literature baseline
- [ ] Advance observer read-write `\Phi` from structural placeholder to concrete fluid-domain implementation
- [ ] Build entropy-causality literature synthesis lane (Wissner-Gross / Verlinde / Penrose / Carroll, etc.)

### 3.2 Integration to canonical docs

- [ ] Promote defensible results into docs with citations and failure conditions
- [ ] Keep speculative threads in clearly labeled roadmap sections
- [ ] Maintain the canonical split across `04` neuro evidence, `13` nested temporal domains, and `14` cognitive tempo orchestration
- [ ] Add changelog section for claim-tier promotions/demotions

### 3.3 Topological memory continuity retrieval (bounded)

- [x] Land provisional ratification note in `docs/archive/topological_memory_continuity_retrieval_v0.md`
- [x] Freeze a v0 node / edge / trace schema for bounded ecosystem topology (`schemas/topological_memory_graph_v0.schema.json`, `schemas/topological_memory_queries_v0.schema.json`)
- [x] Build a ~30-query continuity benchmark from real repo/session/checkpoint questions (`memory/research/topological-memory-v0/benchmark_queries_v0.json`)
- [ ] Implement baseline retrievals: keyword, recency, and embedding (if available)
- [ ] Implement topology-aware retrieval with inspectable path output
- [ ] Evaluate whether promotion/disposition metadata improves retrieval quality
- [ ] Promote only if topology-aware retrieval beats at least one flat baseline with interpretable paths

---

## Recurring operating checklist (per cycle)

- [ ] Question scoped with inclusion/exclusion criteria
- [ ] Sources collected and normalized
- [ ] Atomic claims extracted with assumptions/limitations
- [ ] Ontology mapping completed
- [ ] Dual-expression hypotheses generated
- [ ] Falsification cards emitted
- [ ] Quality gates run and recorded
- [ ] Next concrete experiment selected

---

## Immediate next 3 tasks

1. [ ] Add docs/workflow references to `research_ingestion_protocol.md`
2. [ ] Build adapter stub for `ferroelectric-materials-project` output import
3. [ ] Run first pilot cycle on temporal asymmetry topic and publish full artifact bundle

## Topological memory next 3 tasks

1. [ ] Define the v0 node / edge / trace schema
2. [ ] Assemble the 30-query benchmark set from real continuity questions
3. [ ] Implement baseline scorers before building the topology-aware retriever
