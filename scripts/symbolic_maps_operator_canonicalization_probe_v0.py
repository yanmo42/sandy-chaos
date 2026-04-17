#!/usr/bin/env python3
"""Final tiny canonical-operator probe for SC-CONCEPT-0006."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "memory" / "research" / "symbolic-maps-level4" / "normalization_sketch_v0.json"
DEFAULT_OUT_JSON = ROOT / "memory" / "research" / "symbolic-maps-level4" / "operator_canonicalization_probe_v0.json"
DEFAULT_OUT_MD = ROOT / "memory" / "research" / "symbolic-maps-level4" / "operator_canonicalization_probe_v0_summary.md"

TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z_-]+")

CANONICAL_VOCAB = {
    "structural_normalization": ["normalize", "extract", "translate", "label", "packetize"],
    "constraint_discipline": ["validate", "constrain", "annotate", "project-failure", "exclude-boundary"],
    "comparison_reuse": ["retrieve", "compose", "bridge", "bundle"],
}

DIRECT_SYNONYM_MAP = {
    "normalize": {"normalize"},
    "extract": {"extract", "ingest"},
    "translate": {"translate"},
    "label": {"label", "labeling"},
    "packetize": {"packetize", "packetization"},
    "validate": {"validate"},
    "constrain": {"constraint", "constrain", "constraints"},
    "annotate": {"annotate"},
    "project-failure": {"failure"},
    "exclude-boundary": {"boundary", "exclusion", "exclude"},
    "retrieve": {"retrieve"},
    "compose": {"compose"},
    "bridge": {"bridge"},
    "bundle": {"bundle", "bundling"},
}

SEMANTIC_TRANSLATIONS = {
    "detect_threshold_crossing": "translate",
    "reorganize_behavior": "compose",
    "externalize_coherence": "bridge",
    "separate_metaphor_model_mechanism": "annotate",
    "constraint_binding": "constrain",
    "failure_projection": "project-failure",
    "boundary_exclusion": "exclude-boundary",
    "operator_bundling": "bundle",
}


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run symbolic-maps operator canonicalization probe v0")
    ap.add_argument("--input", default=str(DEFAULT_INPUT))
    ap.add_argument("--out-json", default=str(DEFAULT_OUT_JSON))
    ap.add_argument("--out-md", default=str(DEFAULT_OUT_MD))
    return ap.parse_args()


def subtokens(text: str) -> set[str]:
    found: set[str] = set()
    for token in TOKEN_RE.findall(text.lower().replace("/", " ")):
        for part in re.split(r"[_-]+", token):
            if part:
                found.add(part)
    return found


def classify_operator(label: str) -> dict[str, str | bool]:
    tokens = subtokens(label)
    for canonical, direct_tokens in DIRECT_SYNONYM_MAP.items():
        if tokens & direct_tokens:
            return {"canonical": canonical, "mode": "direct", "matched": True}
    if label in SEMANTIC_TRANSLATIONS:
        return {"canonical": SEMANTIC_TRANSLATIONS[label], "mode": "semantic", "matched": True}
    return {"canonical": "", "mode": "unmapped", "matched": False}


def load_rows(path: Path) -> list[dict[str, object]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("expected list input")
    return rows


def build_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    total = 0
    direct = 0
    semantic = 0
    unmapped = 0
    per_artifact = []
    family_artifact_support = {family: {} for family in CANONICAL_VOCAB}

    reverse_family = {}
    for family, canonicals in CANONICAL_VOCAB.items():
        for canonical in canonicals:
            reverse_family[canonical] = family

    for row in rows:
        artifact_id = str(row["artifact_id"])
        mapped = []
        for op in row["operator_slots"]:
            total += 1
            label = str(op)
            result = classify_operator(label)
            mode = str(result["mode"])
            canonical = str(result["canonical"])
            if mode == "direct":
                direct += 1
            elif mode == "semantic":
                semantic += 1
            else:
                unmapped += 1
            mapped.append({"label": label, **result})
            if canonical:
                family = reverse_family[canonical]
                family_artifact_support[family].setdefault(canonical, set()).add(artifact_id)
        per_artifact.append({"artifact_id": artifact_id, "mapped": mapped})

    shared_multi_artifact = {}
    for family, canonical_map in family_artifact_support.items():
        shared_multi_artifact[family] = {
            canonical: sorted(artifacts)
            for canonical, artifacts in canonical_map.items()
            if len(artifacts) >= 2
        }

    direct_pct = direct / total if total else 0.0
    semantic_pct = semantic / total if total else 0.0
    unmapped_pct = unmapped / total if total else 0.0
    families_with_shared = [f for f, data in shared_multi_artifact.items() if data]

    if semantic_pct > 0.25 or len(families_with_shared) < 3:
        decision = "demote-hardening-candidacy"
    elif direct_pct >= 0.70 and semantic_pct <= 0.20:
        decision = "hold-hardening-candidacy"
    else:
        decision = "hold-hardening-candidacy"

    return {
        "target": "SC-CONCEPT-0006",
        "canonical_vocabulary": CANONICAL_VOCAB,
        "total_operator_labels": total,
        "direct_mapped": direct,
        "semantic_mapped": semantic,
        "unmapped": unmapped,
        "direct_pct": direct_pct,
        "semantic_pct": semantic_pct,
        "unmapped_pct": unmapped_pct,
        "per_artifact": per_artifact,
        "shared_multi_artifact": shared_multi_artifact,
        "families_with_shared_multi_artifact": families_with_shared,
        "decision": decision,
    }


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Symbolic Maps Operator Canonicalization Probe v0",
        "",
        "- Targets: `SC-CONCEPT-0006`",
        f"- Total operator labels: **{summary['total_operator_labels']}**",
        f"- Direct mapped: **{summary['direct_mapped']}** ({summary['direct_pct']:.1%})",
        f"- Semantic mapped: **{summary['semantic_mapped']}** ({summary['semantic_pct']:.1%})",
        f"- Unmapped: **{summary['unmapped']}** ({summary['unmapped_pct']:.1%})",
        f"- Decision: **{summary['decision'].upper()}**",
        "",
        "## Shared multi-artifact canonicals",
        "",
    ]
    for family, data in summary["shared_multi_artifact"].items():
        lines.append(f"### `{family}`")
        if data:
            for canonical, artifacts in data.items():
                lines.append(f"- `{canonical}` → {len(artifacts)} artifacts")
        else:
            lines.append("- none")
        lines.append("")
    lines.extend([
        "## Read",
        "",
        "If shared canonicals remain thin and semantic mapping stays high, the vocabulary is being imposed more than discovered.",
        "",
    ])
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
