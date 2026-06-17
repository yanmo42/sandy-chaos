# SC-CONCEPT-0004 — Archival Result Surface

**Concept:** `topological-memory-continuity-retrieval`
**Archived:** 2026-06-17
**Author:** autonomous proof-frontier pass (Ygg / Sandy Chaos)
**Proof-path level at archive:** Level 4 (discriminating test, bounded fixture)
**Headline claim tier:** **[Defensible]** for one frozen fixture only

---

## 1. What this surface is

SC-CONCEPT-0004 asks a narrow, attackable question:

> Does **topology-aware retrieval** over a small typed memory graph beat **flat
> (non-structural) baselines** on a continuity-retrieval benchmark, while keeping
> its ranking decisions **interpretable** via explicit path traces?

"Continuity retrieval" = the operational problem of a dispatched agent finding the
right prior node (archive draft, concept node, session checkpoint, runtime module,
contract) when resuming work. The hypothesis under test is that *how nodes are
connected* (the corridor / edge structure) carries retrieval-relevant information
that node-local content alone (keyword) or freshness alone (recency) does not.

---

## 2. What was actually proven — [Defensible]

Re-run and reproduced byte-identically on 2026-06-17 (deterministic pipeline:
`scripts/topological_memory_v0.py` → `scripts/topological_memory_compare_v0.py`).

**Fixture:** frozen 12-node / 13-edge / 4-trace typed graph (`graph_v0.json`),
30-query benchmark (`benchmark_queries_v0.json`), top-k = 3.

**Retrieval metrics (hit@3 / MRR):**

| baseline   | hit@3 | MRR   | available |
|------------|-------|-------|-----------|
| topology   | 1.000 | 0.867 | yes       |
| keyword    | 0.967 | 0.789 | yes       |
| recency    | 0.667 | 0.300 | yes       |
| embedding  | —     | —     | **no** (sentence-transformers not installed) |

**Pairwise (topology vs baseline), hit win/loss/tie over 30 queries:**

- topology vs keyword: 1 / 0 / 29 (plus 6/3/21 on reciprocal-rank)
- topology vs recency: 10 / 0 / 20 (plus 26/0/4 on reciprocal-rank)

**Interpretability:** every topology result row carries `path_nodes`, `path_edges`,
a human-readable `path_summary`, and a score decomposition
(`topology` + `lexical` + `trace` + `anchor`). Example (Q-024):
`N_RUNTIME_ADOPTION --[implemented_by:E_ADOPTION_PROMPT]--> N_PROMPT_SC0001`.

**Promotion gate:** PASS, explicitly **bounded to this fixture**
(`promotion_gate_v0.json`, claim tier `defensible for bounded fixture only`).

So the defensible statement is precise and small:

> **[Defensible]** On this single frozen fixture, topology-aware retrieval strictly
> beats both flat baselines (keyword, recency) on hit@3 and MRR, never loses a query
> to them, and exposes interpretable path evidence for each ranking decision.

---

## 3. What was NOT shown — failure boundaries

These are explicit non-claims. Do not let them be promoted by association.

1. **[NOT shown] Generalization beyond the frozen fixture.** Results rest on one
   hand-built 12-node graph and 30 curated queries. No held-out graph, no second
   fixture, no cross-validation. The advantage could be fixture-fit.
2. **[NOT shown] Topology beats a semantic embedding retriever.** The embedding
   baseline never ran (`sentence-transformers` absent on host). Keyword already
   reaches 0.967 hit@3, so the *meaningful* competitor — dense semantic retrieval —
   is untested. Beating keyword/recency is a **weak bar**.
3. **[NOT shown — corrected here] Perturbation robustness.** Until 2026-06-17,
   SC-CONCEPT-0004 had **no robustness/perturbation pass of its own**. See §5.
4. **[NOT shown] Real runtime utility.** Runtime traces exist
   (`topological-memory-v0/runtime_traces/`) but there is no end-to-end measurement
   that topology retrieval improved an actual planner/dispatch outcome.
5. **[NOT shown] Scale behavior.** 12 nodes is far below any realistic memory graph;
   nothing here speaks to behavior at 10^3–10^6 nodes.

---

## 4. State-integrity correction (important)

`state/active-work.json` (lane `sandy-chaos-proof-frontier`) and the dispatching task
both described SC-CONCEPT-0004 as having earned **"two consecutive STABLE robustness
verdicts (2026-06-06 and 2026-06-13, 0/20 collapses, ±10% perturbations, bidirectional
corridor structure intact)."**

On inspection, those two robustness artifacts are internally labeled
**`SC-CONCEPT-0003`** (hyperstition-policy-attractor-dynamics), not 0004:

- `memory/research/hyperstition-v0/robustness_pass_stress_v0.json` — `concept: SC-CONCEPT-0003`, 0/40 collapses, STABLE (mtime 2026-06-06)
- `memory/research/hyperstition-v0/robustness_pass_ygg_pulse.json` — `concept: SC-CONCEPT-0003`, 0/20 collapses, STABLE (mtime 2026-06-13)

The "bidirectional corridor structure" language belongs to the SC-CONCEPT-0003
self-fulfilling/self-defeating belief-corridor model, which is a **different surface**
from the 0004 retrieval graph. The two were conflated in lane state.

**Consequence:** the robustness credibility that justified promoting 0004 to "defensible
operational component" was, until today, borrowed from 0003. The 0004 retrieval result
is still independently defensible (§2), but its robustness claim required a real pass —
which is why §5 was run as the next frontier step rather than treated as already done.

---

## 5. New robustness pass for SC-CONCEPT-0004 (2026-06-17)

To close the gap in §4.3, a perturbation pass specific to the retrieval graph was
designed and executed: `scripts/topological_memory_robustness_pass_v0.py`
(output: `robustness_pass_v0.json` / `.md`). Because the flat baselines (keyword,
recency) never read edges, edge perturbations stress **only** the topology scorer —
a clean adversarial test of the structural-coherence hypothesis. 20 deterministic
perturbations: 13 single-edge drops + 7 ±10% weight-jitter seeds. Collapse definition
(stated in advance): topology hit@3 ≤ keyword hit@3, or path evidence absent.

**Verdict (2026-06-17): WEAKENED — collapsed 4/20.** [Defensible]

- Gate advantage (topology > recency) retained **20/20** — robust.
- Strong advantage (topology > keyword) retained **16/20** — fragile.
- Weight jitter (±10%): **0/7 collapses** — numerically robust.
- The 4 collapses are all single-edge drops of:
  `E_ADOPTION_PROMPT`, `E_PROMPT_RUNTIME`, `E_PROMPT_EVAL`, `E_VALIDATION_CONCEPT`.
  Dropping any one moves topology from hit@3 = 1.000 → 0.967, exactly **tying** keyword.

**What this teaches (and corrects):** topology's entire advantage *over the strongest
flat baseline* is carried by a **single bridge query** (Q-025, "Which node bridges
adoption docs into code work?") whose 2-hop path can be severed by any of 4 corridor
edges. So the "beats keyword" claim from §2 is real but **razor-thin and structurally
fragile**; the "beats recency" claim is genuinely robust. This is a more honest picture
than the borrowed "STABLE ×2, 0/20" framing in §4: 0004's own robustness is **WEAKENED**,
not STABLE. The structural-coherence hypothesis is *supported* (the advantage is
carried by specific edges, and survives weight noise) but the *margin* is thin — which
is exactly why the next step (§6) is to widen the margin, not declare victory.

---

## 6. Selected next frontier step

The WEAKENED result sharpens the frontier question. Two facts now dominate:

1. Topology's advantage over the *strongest* flat baseline (keyword) is **one query**
   and **structurally fragile** (§5).
2. The genuinely strong competitor — **dense semantic / embedding retrieval** — has
   **never run** (§3.2). Keyword at 0.967 is a weak bar; an embedding retriever might
   also resolve Q-025 lexically-by-meaning, which would collapse topology's marginal
   win to a tie.

**Next discriminating test (ranked #1): topology vs embedding baseline.**

> Run the existing embedding baseline (`embedding_baseline` in
> `nfem_suite/intelligence/ygg/topological_memory.py`, currently dark because
> `sentence-transformers` is not installed) against topology on the same 30-query
> fixture, with path traces required. If embedding also resolves the bridge query
> Q-025, topology's "beats the strongest baseline" claim **falsifies** down to a tie,
> and the surface stays archive-bounded. If topology still uniquely wins bridge/2-hop
> queries that embeddings miss, that is the first *real* (non-keyword) evidence that
> structural connectivity carries retrieval signal a semantic model does not.

- **Why this and not "more queries first":** widening the fixture without a strong
  baseline just re-confirms a weak bar. The embedding comparison is the cleanest
  falsifier and directly tests the structural-coherence hypothesis against the model
  most likely to explain the result away.
- **Dependency / gate:** `sentence-transformers` is a **local, free** package
  (consistent with the no-paid-API constraint), but it is a large download (~torch).
  It was **not** installed in this autonomous session; installing it is the first
  concrete action of the next step and is left for an explicit go-ahead.
- **Failure condition (stated in advance):** if the embedding baseline ties or beats
  topology on hit@3 *and* on the bridge queries (Q-025 and the topology-only set
  Q-001/002/012/014/017/018/020/023/024), SC-CONCEPT-0004 should **not** be promoted
  beyond "defensible vs weak flat baselines on one fixture" and the frontier should
  rerank.

**Ranked #2 (only after #1):** expand to a second, independently-built graph + query
fixture to test whether the topology advantage is more than a single bridge query.

## 7. Why this surface still matters (directional, not a claim)

The interesting direction — *coherence carried by connection rather than by node-local
content* — is a toy instantiation of a relational view (Rovelli-style: what is "real"
is what can be tied into further observations). SC-CONCEPT-0004 is a small, honest place
to ask whether structural connectivity survives perturbation as a retrieval carrier.
That is **direction-finding**, not a proven claim, and is kept out of the defensible tier
on purpose.

---

## 8. Reproduction

```
cd /home/ian/projects/sandy-chaos
python3 scripts/topological_memory_v0.py --out /tmp/baseline.json --top-k 3
python3 scripts/topological_memory_compare_v0.py --report /tmp/baseline.json \
    --out-json /tmp/cmp.json --out-md /tmp/cmp.md
python3 scripts/topological_memory_robustness_pass_v0.py   # §5 robustness pass
```

Artifacts: `memory/research/topological-memory-v0/` (graph, queries, baseline report,
comparison summary/report, promotion gate, runtime traces, robustness pass).
