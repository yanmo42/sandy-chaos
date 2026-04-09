# Topological Memory Runtime Adoption v0

Interface:
- `nfem_suite/intelligence/ygg/topological_memory_runtime.py`
- entrypoints:
  - `retrieve_continuity_context(query, mode=auto|topology|flat, top_k=...)`
  - `write_retrieval_trace(...)`

Workflow consumer:
- `scripts/automation_orchestrator.py`
- bounded use: continuity-lane task preparation only
- retrieval output is attached as advisory continuity context plus an inspectable trace artifact

What changed:
- continuity task preparation now performs a live retrieval call instead of only attaching static topological-memory references
- each successful retrieval writes a trace artifact under `memory/research/topological-memory-v0/runtime_traces/`
- flat retrieval remains available and is the fallback path if topology is unavailable or produces no usable result
- a workflow-style comparison harness now writes side-by-side topology vs flat outputs

Evidence produced:
- runtime retrieval traces under `memory/research/topological-memory-v0/runtime_traces/`
- workflow comparison artifacts:
  - `memory/research/topological-memory-v0/runtime_adoption_comparison_v0.json`
  - `memory/research/topological-memory-v0/runtime_adoption_comparison_v0.md`
- current bounded comparison snapshot:
  - topology hit-rate: `0.667`
  - flat hit-rate: `1.000`
  - flat-only hit: `WQ-003`, where the expected TODO node is found at rank 2 while the top node remains a nearby but wrong doc node

What did not work / should not be inferred:
- this does not prove topological retrieval is generally superior
- this does not grant retrieval outputs authority over planning, promotion, governance, or dispatch policy
- current comparison scope is narrow and graph-quality dependent
- if the graph is missing or stale, the workflow degrades to static continuity refs or flat retrieval rather than failing closed
