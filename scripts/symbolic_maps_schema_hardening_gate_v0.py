#!/usr/bin/env python3
"""Run a bounded schema-hardening gate on the current SC-CONCEPT-0006 sketch."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nfem_suite.intelligence.narrative_invariants.benchmark import (  # noqa: E402
    load_invariant_sketch,
    summarize_invariant_sketch,
)

DEFAULT_INPUT = ROOT / "memory" / "research" / "symbolic-maps-level4" / "normalization_sketch_v0.json"
DEFAULT_OUT_JSON = ROOT / "memory" / "research" / "symbolic-maps-level4" / "schema_hardening_gate_v0.json"
DEFAULT_OUT_MD = ROOT / "memory" / "research" / "symbolic-maps-level4" / "schema_hardening_gate_v0_summary.md"

SLOT_FIELDS = (
    "role_slots",
    "operator_slots",
    "constraint_slots",
    "failure_slots",
    "boundary_slots",
)

SCAFFOLD_STOPWORDS = {
    "about",
    "across",
    "after",
    "again",
    "already",
    "also",
    "because",
    "before",
    "being",
    "between",
    "beyond",
    "boundaries",
    "boundary",
    "build",
    "buildout",
    "candidate",
    "comparison",
    "comparisons",
    "compare",
    "compared",
    "constraint",
    "constraints",
    "current",
    "does",
    "each",
    "enough",
    "failure",
    "failures",
    "family",
    "fields",
    "future",
    "hardening",
    "into",
    "later",
    "look",
    "make",
    "maps",
    "mode",
    "more",
    "most",
    "must",
    "need",
    "normalization",
    "normalized",
    "operator",
    "operators",
    "output",
    "outputs",
    "rather",
    "real",
    "repeated",
    "role",
    "roles",
    "same",
    "schema",
    "should",
    "signals",
    "sketch",
    "slot",
    "slots",
    "source",
    "sources",
    "still",
    "symbolic",
    "than",
    "that",
    "their",
    "them",
    "these",
    "they",
    "this",
    "through",
    "used",
    "useful",
    "using",
    "value",
    "values",
    "where",
    "which",
    "with",
    "without",
    "work",
}

TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z_-]+")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run symbolic-maps schema hardening gate v0")
    ap.add_argument("--input", default=str(DEFAULT_INPUT))
    ap.add_argument("--out-json", default=str(DEFAULT_OUT_JSON))
    ap.add_argument("--out-md", default=str(DEFAULT_OUT_MD))
    return ap.parse_args()


def tokenize(values: Iterable[str]) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        for token in TOKEN_RE.findall(value.lower().replace("/", " ")):
            token = token.strip("_-")
            if len(token) < 4:
                continue
            if token in SCAFFOLD_STOPWORDS:
                continue
            tokens.add(token)
    return tokens


def build_gate_summary(input_path: Path) -> dict[str, object]:
    rows = load_invariant_sketch(input_path)
    base_summary = summarize_invariant_sketch(rows)
    artifact_ids = [row.artifact_id for row in rows]

    families: dict[str, object] = {}
    hardening_ready_families: list[str] = []

    for field in SLOT_FIELDS:
        per_artifact_tokens = {
            row.artifact_id: tokenize(getattr(row, field))
            for row in rows
        }
        token_artifacts: dict[str, set[str]] = defaultdict(set)
        for artifact_id, tokens in per_artifact_tokens.items():
            for token in tokens:
                token_artifacts[token].add(artifact_id)

        recurring_ge2 = sorted(token for token, seen in token_artifacts.items() if len(seen) >= 2)
        recurring_ge3 = sorted(token for token, seen in token_artifacts.items() if len(seen) >= 3)

        pairwise_overlap = []
        overlap_pair_count = 0
        for left, right in combinations(artifact_ids, 2):
            shared = sorted(per_artifact_tokens[left] & per_artifact_tokens[right])
            if shared:
                overlap_pair_count += 1
            pairwise_overlap.append(
                {
                    "left": left,
                    "right": right,
                    "shared_tokens": shared,
                    "shared_count": len(shared),
                }
            )

        family_summary = {
            "distinct_non_scaffold_tokens": sum(len(tokens) for tokens in per_artifact_tokens.values()),
            "artifact_tokens": {artifact_id: sorted(tokens) for artifact_id, tokens in per_artifact_tokens.items()},
            "recurring_tokens_ge2": recurring_ge2,
            "recurring_tokens_ge3": recurring_ge3,
            "overlap_pair_count": overlap_pair_count,
            "pairwise_overlap": pairwise_overlap,
            "hardening_ready": len(recurring_ge2) >= 2 and overlap_pair_count >= 3,
        }
        if family_summary["hardening_ready"]:
            hardening_ready_families.append(field)
        families[field] = family_summary

    return {
        "target": "SC-CONCEPT-0006",
        "question": "Do current slot values converge enough across the four-artifact frontier to justify schema hardening?",
        "inputs": {
            "normalization_sketch": str(input_path.relative_to(ROOT)),
            "artifact_count": base_summary["artifact_count"],
            "slot_families": list(SLOT_FIELDS),
        },
        "method": {
            "tokenization": "lowercase, simple word split, ignore short tokens and scaffold terms",
            "note": "This gate measures value convergence, not slot-family coverage.",
        },
        "coverage_summary": base_summary,
        "families": families,
        "hardening_ready_families": hardening_ready_families,
    }


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Symbolic Maps Schema Hardening Gate v0",
        "",
        "- Targets: `SC-CONCEPT-0006`",
        f"- Input sketch: `{summary['inputs']['normalization_sketch']}`",
        f"- Artifact count: **{summary['inputs']['artifact_count']}**",
        f"- Hardening-ready families by this gate: **{len(summary['hardening_ready_families'])}/5**",
        "",
        "## Read",
        "",
        "This gate asks a harder question than the normalization sketch.",
        "The sketch proved repeated slot-family coverage.",
        "This pass asks whether the slot values themselves are converging enough to justify hardening.",
        "",
        "## Family summary",
        "",
    ]

    for field in SLOT_FIELDS:
        family = summary["families"][field]
        lines.append(f"### `{field}`")
        lines.append("")
        lines.append(f"- Hardening-ready by gate: **{family['hardening_ready']}**")
        lines.append(f"- Recurring non-scaffold tokens in >=2 artifacts: {', '.join(f'`{token}`' for token in family['recurring_tokens_ge2']) or 'none'}")
        lines.append(f"- Recurring non-scaffold tokens in >=3 artifacts: {', '.join(f'`{token}`' for token in family['recurring_tokens_ge3']) or 'none'}")
        lines.append(f"- Artifact pairs with any overlap: **{family['overlap_pair_count']}/6**")
        lines.append("")

    lines.extend(
        [
            "## Gate read",
            "",
            f"- Families clearing the minimal gate: {', '.join(f'`{field}`' for field in summary['hardening_ready_families']) or 'none'}",
            "- A family can still be comparison-useful without being hardening-ready.",
            "- If convergence appears mostly in warning or failure rhetoric, hold the lane even if one family looks promising.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    summary = build_gate_summary(input_path)

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
