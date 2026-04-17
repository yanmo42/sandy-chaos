#!/usr/bin/env python3
"""Pressure-test operator vocabulary convergence for SC-CONCEPT-0006."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "memory" / "research" / "symbolic-maps-level4" / "normalization_sketch_v0.json"
DEFAULT_OUT_JSON = ROOT / "memory" / "research" / "symbolic-maps-level4" / "operator_vocabulary_pressure_v0.json"
DEFAULT_OUT_MD = ROOT / "memory" / "research" / "symbolic-maps-level4" / "operator_vocabulary_pressure_v0_summary.md"

TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z_-]+")

QUERY_FAMILIES = {
    "structural_normalization": {
        "anchors": {"normalize"},
        "aliases": {"extract", "ingest", "translate", "labeling", "packetization"},
        "question": "Can the vocabulary answer structure-extraction / normalization queries without manual stitching?",
    },
    "constraint_discipline": {
        "anchors": {"constraint", "boundary", "failure", "validate"},
        "aliases": {"annotate", "binding", "projection", "exclusion"},
        "question": "Can the vocabulary answer operator-discipline queries directly?",
    },
    "comparison_reuse": {
        "anchors": {"retrieve", "compose", "bridge"},
        "aliases": {"bundle", "bundling"},
        "question": "Can the vocabulary answer retrieval / composition / reuse queries directly?",
    },
}


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run symbolic-maps operator vocabulary pressure v0")
    ap.add_argument("--input", default=str(DEFAULT_INPUT))
    ap.add_argument("--out-json", default=str(DEFAULT_OUT_JSON))
    ap.add_argument("--out-md", default=str(DEFAULT_OUT_MD))
    return ap.parse_args()


def split_tokens(text: str) -> set[str]:
    tokens: set[str] = set()
    for token in TOKEN_RE.findall(text.lower().replace("/", " ")):
        for part in re.split(r"[_-]+", token):
            if part:
                tokens.add(part)
    return tokens


def load_rows(path: Path) -> list[dict[str, object]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("expected a list of normalization rows")
    return rows


def matching_ops(operators: Iterable[str], match_tokens: set[str]) -> list[str]:
    matches = []
    for op in operators:
        if split_tokens(str(op)) & match_tokens:
            matches.append(str(op))
    return matches


def build_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    artifact_count = len(rows)
    family_summaries: dict[str, object] = {}
    direct_clear_count = 0
    alias_rescue_families: list[str] = []

    for family_name, spec in QUERY_FAMILIES.items():
        direct_artifacts: list[dict[str, object]] = []
        alias_only_artifacts: list[dict[str, object]] = []
        direct_names: list[str] = []
        alias_names: list[str] = []

        for row in rows:
            artifact_id = str(row["artifact_id"])
            operators = [str(value) for value in row["operator_slots"]]
            direct_matches = matching_ops(operators, set(spec["anchors"]))
            alias_matches = matching_ops(operators, set(spec["aliases"]))

            if direct_matches:
                direct_names.append(artifact_id)
                direct_artifacts.append(
                    {
                        "artifact_id": artifact_id,
                        "direct_matches": direct_matches,
                        "alias_matches": alias_matches,
                    }
                )
            elif alias_matches:
                alias_names.append(artifact_id)
                alias_only_artifacts.append(
                    {
                        "artifact_id": artifact_id,
                        "alias_matches": alias_matches,
                    }
                )

        direct_support_count = len(direct_names)
        alias_assisted_support_count = direct_support_count + len(alias_names)
        clears_direct = direct_support_count >= 3
        if clears_direct:
            direct_clear_count += 1
        if direct_support_count < 3 and alias_assisted_support_count >= 3:
            alias_rescue_families.append(family_name)

        family_summaries[family_name] = {
            "question": spec["question"],
            "anchors": sorted(spec["anchors"]),
            "aliases": sorted(spec["aliases"]),
            "direct_support_count": direct_support_count,
            "alias_assisted_support_count": alias_assisted_support_count,
            "direct_artifacts": direct_artifacts,
            "alias_only_artifacts": alias_only_artifacts,
            "clears_direct_threshold": clears_direct,
            "needs_alias_rescue": direct_support_count < 3 and alias_assisted_support_count >= 3,
        }

    if direct_clear_count >= 2 and not alias_rescue_families:
        decision = "advance"
    elif direct_clear_count <= 1:
        decision = "hold"
    else:
        decision = "hold"

    return {
        "target": "SC-CONCEPT-0006",
        "artifact_count": artifact_count,
        "query_families": family_summaries,
        "direct_clear_count": direct_clear_count,
        "alias_rescue_families": alias_rescue_families,
        "decision": decision,
        "read": {
            "summary": "This pass checks whether cross-artifact operator queries work mostly through direct lexical reuse or only after manual alias stitching.",
            "success_rule": "At least two query families must clear three-artifact support directly, with only minor alias help.",
        },
    }


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Symbolic Maps Operator Vocabulary Pressure v0",
        "",
        "- Targets: `SC-CONCEPT-0006`",
        f"- Artifact count: **{summary['artifact_count']}**",
        f"- Query families clearing direct threshold: **{summary['direct_clear_count']}/3**",
        f"- Alias-rescued families: {', '.join(f'`{name}`' for name in summary['alias_rescue_families']) or 'none'}",
        f"- Decision: **{str(summary['decision']).upper()}**",
        "",
        "## Family results",
        "",
    ]

    for family_name, family in summary["query_families"].items():
        lines.append(f"### `{family_name}`")
        lines.append("")
        lines.append(f"- Question: {family['question']}")
        lines.append(f"- Direct support: **{family['direct_support_count']}** artifacts")
        lines.append(f"- Alias-assisted support: **{family['alias_assisted_support_count']}** artifacts")
        lines.append(f"- Clears direct threshold: **{family['clears_direct_threshold']}**")
        lines.append(f"- Needs alias rescue: **{family['needs_alias_rescue']}**")
        if family["direct_artifacts"]:
            lines.append("- Direct matches:")
            for item in family["direct_artifacts"]:
                matches = ", ".join(f"`{value}`" for value in item["direct_matches"])
                lines.append(f"  - `{item['artifact_id']}` → {matches}")
        if family["alias_only_artifacts"]:
            lines.append("- Alias-only matches:")
            for item in family["alias_only_artifacts"]:
                matches = ", ".join(f"`{value}`" for value in item["alias_matches"])
                lines.append(f"  - `{item['artifact_id']}` → {matches}")
        lines.append("")

    lines.extend(
        [
            "## Read",
            "",
            "If useful coverage appears only after alias stitching, the vocabulary is still comparison-helpful but not schema-ready.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    rows = load_rows(Path(args.input))
    summary = build_summary(rows)

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
