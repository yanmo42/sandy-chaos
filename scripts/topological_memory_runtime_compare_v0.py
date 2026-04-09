#!/usr/bin/env python3
"""Compare workflow-style continuity retrieval in flat vs topology modes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nfem_suite.intelligence.ygg.topological_memory_runtime import retrieve_continuity_context

DEFAULT_OUT_JSON = ROOT / "memory" / "research" / "topological-memory-v0" / "runtime_adoption_comparison_v0.json"
DEFAULT_OUT_MD = ROOT / "memory" / "research" / "topological-memory-v0" / "runtime_adoption_comparison_v0.md"

WORKFLOW_QUERIES = [
    {
        "id": "WQ-001",
        "question": "What script builds lane-aware task contracts from TODO surfaces?",
        "expected_nodes": ["N_SCRIPT_AUTOMATION_ORCH"],
    },
    {
        "id": "WQ-002",
        "question": "What script dispatches orchestrator task contracts through the gateway bridge?",
        "expected_nodes": ["N_SCRIPT_ORCH_AUTOSPAWN"],
    },
    {
        "id": "WQ-003",
        "question": "Which TODO surface currently tracks the execution steps for topological memory?",
        "expected_nodes": ["N_PLAN_TODO"],
    },
]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Compare runtime adoption retrieval modes")
    ap.add_argument("--out-json", default=str(DEFAULT_OUT_JSON))
    ap.add_argument("--out-md", default=str(DEFAULT_OUT_MD))
    return ap.parse_args()


def _match_details(expected_nodes: list[str], result: dict[str, Any]) -> dict[str, Any]:
    ranked = result.get("ranked_results", [])
    expected = set(expected_nodes)
    matched = [row.get("node_id") for row in ranked if row.get("node_id") in expected]
    first_match_rank = None
    for idx, row in enumerate(ranked, start=1):
        if row.get("node_id") in expected:
            first_match_rank = idx
            break
    return {
        "hit": bool(matched),
        "matched_nodes": matched,
        "first_match_rank": first_match_rank,
    }


def build_report() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    topology_hits = 0
    flat_hits = 0
    topology_only: list[str] = []
    flat_only: list[str] = []

    for query in WORKFLOW_QUERIES:
        topology = retrieve_continuity_context(query["question"], mode="topology", top_k=3).to_dict()
        flat = retrieve_continuity_context(query["question"], mode="flat", top_k=3).to_dict()
        topology_match = _match_details(query["expected_nodes"], topology)
        flat_match = _match_details(query["expected_nodes"], flat)

        topology_hits += int(topology_match["hit"])
        flat_hits += int(flat_match["hit"])
        if topology_match["hit"] and not flat_match["hit"]:
            topology_only.append(query["id"])
        if flat_match["hit"] and not topology_match["hit"]:
            flat_only.append(query["id"])

        rows.append(
            {
                "id": query["id"],
                "question": query["question"],
                "expected_nodes": query["expected_nodes"],
                "topology": {
                    "mode_used": topology["mode_used"],
                    "hit": topology_match["hit"],
                    "matched_nodes": topology_match["matched_nodes"],
                    "first_match_rank": topology_match["first_match_rank"],
                    "top_node": (topology.get("ranked_results") or [{}])[0].get("node_id"),
                    "trace": topology.get("ranked_results", []),
                },
                "flat": {
                    "mode_used": flat["mode_used"],
                    "baseline_mode": flat["baseline_mode"],
                    "hit": flat_match["hit"],
                    "matched_nodes": flat_match["matched_nodes"],
                    "first_match_rank": flat_match["first_match_rank"],
                    "top_node": (flat.get("ranked_results") or [{}])[0].get("node_id"),
                    "trace": flat.get("ranked_results", []),
                },
            }
        )

    return {
        "workflow_consumer": "scripts/automation_orchestrator.py task preparation for continuity-lane tasks",
        "query_count": len(WORKFLOW_QUERIES),
        "topology_hit_rate": topology_hits / max(1, len(WORKFLOW_QUERIES)),
        "flat_hit_rate": flat_hits / max(1, len(WORKFLOW_QUERIES)),
        "topology_only_hits": topology_only,
        "flat_only_hits": flat_only,
        "rows": rows,
        "notes": [
            "This is a bounded workflow-style comparison, not a promotion argument.",
            "Flat mode remains a live fallback path.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Topological Memory Runtime Adoption v0",
        "",
        f"- Workflow consumer: `{report['workflow_consumer']}`",
        f"- Query count: **{report['query_count']}**",
        f"- Topology hit-rate: **{report['topology_hit_rate']:.3f}**",
        f"- Flat hit-rate: **{report['flat_hit_rate']:.3f}**",
        f"- Topology-only hits: `{report['topology_only_hits']}`",
        f"- Flat-only hits: `{report['flat_only_hits']}`",
        "",
        "## Per-query traces",
        "",
    ]
    for row in report["rows"]:
        lines.append(f"### {row['id']}")
        lines.append("")
        lines.append(f"- Question: {row['question']}")
        lines.append(f"- Expected nodes: {row['expected_nodes']}")
        lines.append(
            f"- Topology: hit={row['topology']['hit']} first_match_rank={row['topology']['first_match_rank']} matched_nodes={row['topology']['matched_nodes']} top_node={row['topology']['top_node']} mode={row['topology']['mode_used']}"
        )
        lines.append(
            f"- Flat: hit={row['flat']['hit']} first_match_rank={row['flat']['first_match_rank']} matched_nodes={row['flat']['matched_nodes']} top_node={row['flat']['top_node']} mode={row['flat']['mode_used']}/{row['flat']['baseline_mode']}"
        )
        lines.append("")
    lines.append("## Bounds")
    lines.append("")
    lines.extend(f"- {note}" for note in report["notes"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    report = build_report()

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(render_markdown(report), encoding="utf-8")

    print(json.dumps({"status": "ok", "json": str(out_json), "md": str(out_md)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
