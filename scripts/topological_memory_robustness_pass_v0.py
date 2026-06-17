#!/usr/bin/env python3
"""Robustness / perturbation pass for SC-CONCEPT-0004 (topological-memory-continuity-retrieval).

Motivation
----------
Until 2026-06-17 the SC-CONCEPT-0004 retrieval result rested on ONE frozen 12-node /
13-edge fixture with no perturbation test of its own. (The "STABLE x2" robustness
verdicts in lane state belonged to SC-CONCEPT-0003, a different surface — see
memory/research/sc-concept-0004-archival.md §4.) This pass gives 0004 a robustness
statement it actually owns.

What it tests
-------------
The topology-aware advantage is *structural*: it comes from edges. The two flat
baselines (keyword, recency) do not read edges at all, so edge perturbations degrade
ONLY the topology scorer. That makes edge perturbation a clean, adversarial stress test
of the structural-coherence hypothesis: if topology's advantage survives dropping and
jittering edges, the advantage is carried by connectivity, not by fixture memorization.

Perturbation families (20 total, deterministic / seeded)
--------------------------------------------------------
  A. single-edge drop x N: remove one edge at a time (structural fragility).
  B. random per-edge weight jitter +/-10% x seeds (numerical robustness).

Collapse definition (stated in advance)
---------------------------------------
For each perturbation, re-run evaluate_queries and compare topology hit@3 against the
flat baselines (which are invariant to edge edits):
  * STRONG advantage retained  : topology hit@3 > keyword hit@3  (beats strongest flat)
  * GATE advantage retained     : topology hit@3 > recency hit@3  (promotion-gate bar:
                                  "beats at least one flat baseline")
  * COLLAPSE (headline)         : topology hit@3 <= keyword hit@3 (loses/ties the
                                  strongest flat baseline) OR path evidence absent.

structural_verdict = STABLE if collapsed_count == 0 else WEAKENED/COLLAPSED.

Usage
-----
  python3 scripts/topological_memory_robustness_pass_v0.py
"""
from __future__ import annotations

import copy
import json
import random
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nfem_suite.intelligence.ygg.topological_memory import (  # noqa: E402
    evaluate_queries,
    load_benchmark_queries,
    load_graph_bundle,
)

CONCEPT_DIR = ROOT / "memory" / "research" / "topological-memory-v0"
GRAPH_PATH = CONCEPT_DIR / "graph_v0.json"
QUERIES_PATH = CONCEPT_DIR / "benchmark_queries_v0.json"
OUT_JSON = CONCEPT_DIR / "robustness_pass_v0.json"
OUT_MD = CONCEPT_DIR / "robustness_pass_v0.md"

TOP_K = 3
JITTER_FRACTION = 0.10
JITTER_SEEDS = list(range(7))  # 7 weight-jitter perturbations


def _prune_orphan_edge_traces(graph_dict: dict) -> dict:
    """Drop traces whose subject is an edge that no longer exists (loader requires this)."""
    edge_ids = {e["id"] for e in graph_dict.get("edges", [])}
    graph_dict["traces"] = [
        t
        for t in graph_dict.get("traces", [])
        if not (t.get("subject_type") == "edge" and t.get("subject_id") not in edge_ids)
    ]
    return graph_dict


def _eval_graph_dict(graph_dict: dict, queries) -> dict:
    """Write a perturbed graph dict to a temp file, load it, and evaluate."""
    graph_dict = _prune_orphan_edge_traces(graph_dict)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(graph_dict, fh)
        tmp_path = fh.name
    try:
        bundle = load_graph_bundle(tmp_path)
        return evaluate_queries(
            bundle, queries, top_k=TOP_K, include_topology=True, include_embedding=False
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def _path_evidence_present(report: dict) -> bool:
    """At least one topology row exposes a non-empty path (path_nodes/path_edges)."""
    ranked = report.get("baselines", {}).get("topology", {}).get("ranked_results", {})
    for rows in ranked.values():
        for row in rows:
            if row.get("path_nodes") or row.get("path_edges"):
                return True
    return False


def _summarize(report: dict) -> dict:
    b = report["baselines"]
    return {
        "topology": b["topology"]["hit_rate"],
        "keyword": b["keyword"]["hit_rate"],
        "recency": b["recency"]["hit_rate"],
        "topology_mrr": b["topology"]["mrr"],
        "path_evidence": _path_evidence_present(report),
    }


def _classify(s: dict) -> dict:
    strong = s["topology"] > s["keyword"]
    gate = s["topology"] > s["recency"]
    collapsed = (not strong) or (not s["path_evidence"])
    return {
        "strong_advantage_retained": strong,
        "gate_advantage_retained": gate,
        "collapsed": collapsed,
    }


def main() -> int:
    base_graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    queries = load_benchmark_queries(QUERIES_PATH)

    baseline_report = _eval_graph_dict(base_graph, queries)
    base_summary = _summarize(baseline_report)

    perturbations: list[dict] = []

    # Family A: single-edge drop
    for idx, edge in enumerate(base_graph["edges"]):
        g = copy.deepcopy(base_graph)
        del g["edges"][idx]
        rep = _eval_graph_dict(g, queries)
        s = _summarize(rep)
        cls = _classify(s)
        perturbations.append(
            {
                "label": f"drop_edge:{edge.get('id', idx)}",
                "family": "single_edge_drop",
                "dropped_edge": edge.get("id"),
                "metrics": s,
                **cls,
            }
        )

    # Family B: random per-edge weight jitter +/-10%
    for seed in JITTER_SEEDS:
        rng = random.Random(seed)
        g = copy.deepcopy(base_graph)
        for e in g["edges"]:
            w = float(e.get("weight", 0.5))
            e["weight"] = max(0.01, w * (1.0 + rng.uniform(-JITTER_FRACTION, JITTER_FRACTION)))
        rep = _eval_graph_dict(g, queries)
        s = _summarize(rep)
        cls = _classify(s)
        perturbations.append(
            {
                "label": f"weight_jitter_pm10_seed{seed}",
                "family": "weight_jitter",
                "seed": seed,
                "metrics": s,
                **cls,
            }
        )

    collapsed = [p for p in perturbations if p["collapsed"]]
    strong = [p for p in perturbations if p["strong_advantage_retained"]]
    gate = [p for p in perturbations if p["gate_advantage_retained"]]

    if not collapsed:
        verdict = "STABLE"
    elif len(collapsed) <= len(perturbations) // 2:
        verdict = "WEAKENED"
    else:
        verdict = "COLLAPSED"

    out = {
        "pass": "robustness",
        "concept": "SC-CONCEPT-0004",
        "surface": "topological-memory-continuity-retrieval",
        "date": "2026-06-17",
        "top_k": TOP_K,
        "jitter_fraction": JITTER_FRACTION,
        "collapse_definition": (
            "topology hit@3 <= keyword hit@3 (loses/ties strongest flat baseline) "
            "OR topology path evidence absent"
        ),
        "baseline": base_summary,
        "total_perturbations": len(perturbations),
        "collapsed_count": len(collapsed),
        "collapsed_labels": [p["label"] for p in collapsed],
        "strong_advantage_retained_count": len(strong),
        "gate_advantage_retained_count": len(gate),
        "structural_verdict": verdict,
        "perturbations": perturbations,
        "notes": [
            "Flat baselines (keyword, recency) do not read edges, so they are invariant "
            "to these perturbations; only the topology scorer is stressed.",
            "STRONG = topology still beats keyword (the strongest flat baseline).",
            "GATE = topology still beats recency (promotion-gate 'beats at least one').",
            "This pass is owned by SC-CONCEPT-0004; it does not inherit the SC-CONCEPT-0003 "
            "corridor robustness verdicts (see sc-concept-0004-archival.md §4).",
        ],
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    md = []
    md.append("# SC-CONCEPT-0004 — Robustness Pass v0 (2026-06-17)\n")
    md.append(f"- Surface: topological-memory-continuity-retrieval")
    md.append(f"- Total perturbations: **{len(perturbations)}** "
              f"({sum(1 for p in perturbations if p['family']=='single_edge_drop')} edge-drops + "
              f"{sum(1 for p in perturbations if p['family']=='weight_jitter')} weight-jitter)")
    md.append(f"- Collapsed: **{len(collapsed)}**")
    md.append(f"- Strong advantage (beats keyword) retained: **{len(strong)}/{len(perturbations)}**")
    md.append(f"- Gate advantage (beats recency) retained: **{len(gate)}/{len(perturbations)}**")
    md.append(f"- **Structural verdict: {verdict}**\n")
    md.append("## Baseline (unperturbed)\n")
    md.append(f"- topology hit@3 = {base_summary['topology']:.3f}, "
              f"keyword = {base_summary['keyword']:.3f}, recency = {base_summary['recency']:.3f}\n")
    md.append("## Collapse definition (stated in advance)\n")
    md.append(f"- {out['collapse_definition']}\n")
    if collapsed:
        md.append("## Collapsed perturbations\n")
        for p in collapsed:
            md.append(f"- {p['label']}: topology={p['metrics']['topology']:.3f} "
                      f"keyword={p['metrics']['keyword']:.3f} path={p['metrics']['path_evidence']}")
        md.append("")
    md.append("## Interpretation\n")
    md.append("Flat baselines are edge-invariant; only topology is stressed. "
              "A STABLE verdict means topology's structural advantage survives dropping any "
              "single edge and +/-10% weight jitter — evidence the advantage is carried by "
              "connectivity rather than fixture memorization, **bounded to this fixture**.\n")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"verdict={verdict} collapsed={len(collapsed)}/{len(perturbations)} "
          f"strong={len(strong)} gate={len(gate)}")
    print(f"wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
