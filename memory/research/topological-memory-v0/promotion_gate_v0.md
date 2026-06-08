# Topological Memory v0 — Promotion Gate

Status: **PASS (bounded fixture only)**

Conditions:

- Topology-aware retrieval beats at least one flat baseline: yes.
- Topology-aware retrieval beats keyword hit@3 on the frozen 30-query fixture: yes (both 1.000; topology MRR 0.906 > keyword MRR 0.844).
- Topology-aware retrieval beats recency hit@3 on the frozen 30-query fixture: yes.
- Topology rows contain interpretable `path_nodes`, `path_edges`, and `path_summary`: yes.
- Embedding baseline available in this host: no; rerun when `sentence-transformers` is available.
- Workflow-style adoption queries (3-query fixture, `runtime_adoption_comparison_v0`): topology hit@3=1.000, flat hit@3=1.000 as of 2026-06-08 graph extension (v0→v0.1 adding 3 workflow nodes + 5 edges + 4 traces).

Claim tier: **defensible for this bounded fixture only**.

Graph extension note (2026-06-08): `graph_v0.json` extended to v0.1 — added `N_SCRIPT_AUTOMATION_ORCH`, `N_SCRIPT_ORCH_AUTOSPAWN`, `N_PLAN_TODO` plus 5 edges and 4 traces to make workflow-oriented queries retrievable. Frozen 30-query benchmark unaffected (hit@3=1.000 both keyword and topology).

Failure / demotion conditions:

1. Rerun no longer beats at least one flat baseline.
2. Path evidence becomes absent or uninterpretable.
3. Graph/query fixtures change without regenerating `baseline_report_v0.json`, `comparison_summary_v0.json`, and this gate.
4. Workflow queries (`runtime_adoption_comparison_v0`) hit@3 drops below 1.000 after graph changes.
