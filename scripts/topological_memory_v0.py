#!/usr/bin/env python3
"""Run Topological Memory v0 baseline evaluation.

Example:
  python3 scripts/topological_memory_v0.py \
    --graph memory/research/topological-memory-v0/graph_v0.json \
    --queries memory/research/topological-memory-v0/benchmark_queries_v0.json \
    --out memory/research/topological-memory-v0/baseline_report_v0.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nfem_suite.intelligence.ygg.topological_memory import (
    evaluate_queries,
    load_benchmark_queries,
    load_graph_bundle,
    write_report,
)

DEFAULT_GRAPH = ROOT / "memory" / "research" / "topological-memory-v0" / "graph_v0.json"
DEFAULT_QUERIES = ROOT / "memory" / "research" / "topological-memory-v0" / "benchmark_queries_v0.json"
DEFAULT_OUT = ROOT / "memory" / "research" / "topological-memory-v0" / "baseline_report_v0.json"


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Topological Memory v0 benchmark runner")
    ap.add_argument("--graph", default=str(DEFAULT_GRAPH), help="Graph JSON path")
    ap.add_argument("--queries", default=str(DEFAULT_QUERIES), help="Benchmark query JSON path")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="Output report JSON path")
    ap.add_argument("--top-k", type=int, default=3, help="Top-k cutoff for hit-rate")
    ap.add_argument(
        "--no-topology",
        action="store_true",
        help="Disable topology-aware scorer (flat baselines only)",
    )
    ap.add_argument(
        "--no-embedding",
        action="store_true",
        help="Disable optional embedding baseline",
    )
    ap.add_argument(
        "--inspect-query",
        help="Query id to print ranked results for (e.g., Q-001)",
    )
    ap.add_argument(
        "--inspect-baseline",
        default="topology",
        help="Baseline to inspect when --inspect-query is set (default: topology)",
    )
    ap.add_argument(
        "--inspect-top-n",
        type=int,
        default=3,
        help="How many ranked rows to print in inspect mode (default: 3)",
    )
    return ap.parse_args()


def main() -> int:
    args = parse_args()

    graph = load_graph_bundle(args.graph)
    queries = load_benchmark_queries(args.queries)

    report = evaluate_queries(
        graph,
        queries,
        top_k=max(1, int(args.top_k)),
        include_topology=not bool(args.no_topology),
        include_embedding=not bool(args.no_embedding),
    )
    out_path = write_report(report, args.out)

    print(f"Loaded graph nodes={len(graph.nodes)} edges={len(graph.edges)} traces={len(graph.traces)}")
    print(f"Loaded benchmark queries={len(queries)}")

    for name, metrics in report.get("baselines", {}).items():
        if metrics.get("available") is False:
            print(f"- {name}: unavailable ({metrics.get('reason', 'no reason provided')})")
            continue
        hit_rate = float(metrics.get("hit_rate", 0.0))
        mrr = float(metrics.get("mrr", 0.0))
        print(f"- {name}: hit@{report['top_k']}={hit_rate:.3f}, mrr={mrr:.3f}")

    if args.inspect_query:
        baseline_name = str(args.inspect_baseline)
        baseline = report.get("baselines", {}).get(baseline_name)
        if baseline is None:
            print(f"\n[inspect] baseline '{baseline_name}' not found")
        elif baseline.get("available") is False:
            print(f"\n[inspect] baseline '{baseline_name}' unavailable: {baseline.get('reason', 'unknown reason')}")
        else:
            ranked = baseline.get("ranked_results", {}).get(str(args.inspect_query), [])
            print(f"\n[inspect] query={args.inspect_query} baseline={baseline_name} rows={len(ranked)}")
            if not ranked:
                print("(no ranked rows)")
            for idx, row in enumerate(ranked[: max(1, int(args.inspect_top_n))], start=1):
                print(f"{idx}. {row.get('node_id')} score={float(row.get('score', 0.0)):.4f}")
                print(f"   reason: {row.get('reason', '')}")
                summary = row.get('path_summary', '')
                if summary:
                    print(f"   path:   {summary}")
                elif row.get('path_nodes'):
                    print(f"   path_nodes: {row.get('path_nodes')}")
                if row.get('path_edges'):
                    print(f"   path_edges: {row.get('path_edges')}")

    try:
        report_path = str(out_path.resolve().relative_to(ROOT))
    except ValueError:
        report_path = str(out_path.resolve())

    print(json.dumps({"status": "ok", "report": report_path}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
