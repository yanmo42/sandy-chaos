# Topological Memory v0 — Promotion Gate

Status: **PASS (bounded fixture only)**

Conditions:

- Topology-aware retrieval beats at least one flat baseline: yes.
- Topology-aware retrieval beats keyword hit@3 on the frozen 30-query fixture: yes.
- Topology-aware retrieval beats recency hit@3 on the frozen 30-query fixture: yes.
- Topology rows contain interpretable `path_nodes`, `path_edges`, and `path_summary`: yes.
- Embedding baseline available in this host: no; rerun when `sentence-transformers` is available.

Claim tier: **defensible for this bounded fixture only**.

Failure / demotion conditions:

1. Rerun no longer beats at least one flat baseline.
2. Path evidence becomes absent or uninterpretable.
3. Graph/query fixtures change without regenerating `baseline_report_v0.json`, `comparison_summary_v0.json`, and this gate.
