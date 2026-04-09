#!/usr/bin/env python3
"""Evaluate the minimal symbolic-maps normalization sketch for SC-CONCEPT-0006."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nfem_suite.intelligence.narrative_invariants.benchmark import (  # noqa: E402
    load_invariant_sketch,
    summarize_invariant_sketch,
)

DEFAULT_INPUT = ROOT / "memory" / "research" / "symbolic-maps-level4" / "normalization_sketch_v0.json"
DEFAULT_OUT_JSON = ROOT / "memory" / "research" / "symbolic-maps-level4" / "normalization_sketch_v0_summary.json"
DEFAULT_OUT_MD = ROOT / "memory" / "research" / "symbolic-maps-level4" / "normalization_sketch_v0_summary.md"


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Evaluate symbolic-maps normalization sketch v0")
    ap.add_argument("--input", default=str(DEFAULT_INPUT))
    ap.add_argument("--out-json", default=str(DEFAULT_OUT_JSON))
    ap.add_argument("--out-md", default=str(DEFAULT_OUT_MD))
    return ap.parse_args()


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Symbolic Maps Normalization Sketch v0",
        "",
        "- Targets: `SC-CONCEPT-0006`",
        f"- Artifact count: **{summary['artifact_count']}**",
        f"- All artifacts fully populated across role/operator/constraint/failure/boundary slots: **{summary['all_artifacts_fully_populated']}**",
        "",
        "## Slot-family coverage",
        "",
    ]
    family_presence = summary["family_presence"]
    family_avg_counts = summary["family_avg_counts"]
    artifact_count = int(summary["artifact_count"])
    for field in summary["slot_families"]:
        lines.append(
            f"- `{field}`: present in **{family_presence[field]}/{artifact_count}** artifacts, avg count **{family_avg_counts[field]:.2f}**"
        )
    lines.extend(["", "## Per-artifact slot counts", ""])
    for row in summary["per_artifact"]:
        counts = row["slot_counts"]
        lines.append(f"### `{row['artifact_id']}`")
        lines.append("")
        lines.append(f"- Role: `{row['artifact_role']}`")
        lines.append(f"- Source mode: `{row['source_mode']}`")
        lines.append(
            "- Slot counts: "
            f"roles={counts['role_slots']}, operators={counts['operator_slots']}, constraints={counts['constraint_slots']}, failures={counts['failure_slots']}, boundaries={counts['boundary_slots']}"
        )
        lines.append(f"- Total slots: {row['total_slots']}")
        lines.append("")
    lines.extend(["## Bounds", ""])
    for note in summary["bounds"]:
        lines.append(f"- {note}")
    lines.append("")
    lines.extend(["## Read", ""])
    if summary["all_artifacts_fully_populated"]:
        lines.append(
            "The current four-artifact set survives one tiny normalization sketch without needing ad hoc extra field families."
        )
        lines.append(
            "That is bounded support for the claim that a repeated comparison skeleton is real enough to pressure further."
        )
    else:
        lines.append(
            "The sketch failed to cover the current artifact set cleanly, so the repeated skeleton should be revised or rejected before any hardening move."
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    rows = load_invariant_sketch(args.input)
    summary = summarize_invariant_sketch(rows)

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(render_markdown(summary), encoding="utf-8")

    print(json.dumps({"status": "ok", "json": str(out_json), "md": str(out_md)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
