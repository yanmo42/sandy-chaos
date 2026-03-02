#!/usr/bin/env python3
"""Verify claim-to-source mapping completeness for research artifacts.

Rule set (lightweight by design):
- Evidence CSV must include a `source_id` column.
- Every claim line in synthesis markdown (bullet lines under a "Claims" section)
  must reference at least one source id token like [S001].
- Every referenced source id must exist in evidence CSV.

This provides a minimal reproducibility gate for AI-assisted synthesis.
"""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path

SOURCE_TAG_RE = re.compile(r"\[(S\d{3,})\]")


@dataclass
class VerificationResult:
    claim_lines: int
    claim_lines_with_tags: int
    missing_source_tags: list[str]
    unknown_source_ids: list[str]

    @property
    def ok(self) -> bool:
        return not self.missing_source_tags and not self.unknown_source_ids


def load_evidence_source_ids(evidence_csv: Path) -> set[str]:
    with evidence_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if "source_id" not in (reader.fieldnames or []):
            raise ValueError("evidence CSV missing required 'source_id' column")

        ids = set()
        for row in reader:
            sid = (row.get("source_id") or "").strip()
            if sid:
                ids.add(sid)
        return ids


def iter_claim_lines(synthesis_md: Path) -> list[str]:
    lines = synthesis_md.read_text(encoding="utf-8", errors="ignore").splitlines()
    in_claims = False
    out: list[str] = []

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("## "):
            in_claims = stripped.lower().startswith("## claims")
            continue

        if not in_claims:
            continue

        if stripped.startswith("- "):
            out.append(stripped)

    return out


def verify_claim_source_mapping(synthesis_md: Path, evidence_csv: Path) -> VerificationResult:
    evidence_ids = load_evidence_source_ids(evidence_csv)
    claims = iter_claim_lines(synthesis_md)

    missing_tags: list[str] = []
    unknown_ids: set[str] = set()
    with_tags = 0

    for claim in claims:
        tags = SOURCE_TAG_RE.findall(claim)
        if not tags:
            missing_tags.append(claim)
            continue

        with_tags += 1
        for tag in tags:
            if tag not in evidence_ids:
                unknown_ids.add(tag)

    return VerificationResult(
        claim_lines=len(claims),
        claim_lines_with_tags=with_tags,
        missing_source_tags=missing_tags,
        unknown_source_ids=sorted(unknown_ids),
    )


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Verify claim-to-source row mapping completeness")
    ap.add_argument("--synthesis", required=True, help="Path to synthesis markdown")
    ap.add_argument("--evidence", required=True, help="Path to evidence CSV")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    result = verify_claim_source_mapping(Path(args.synthesis), Path(args.evidence))

    print(f"claim_lines={result.claim_lines}")
    print(f"claim_lines_with_tags={result.claim_lines_with_tags}")

    if result.missing_source_tags:
        print("missing_source_tags:")
        for line in result.missing_source_tags:
            print(f"  - {line}")

    if result.unknown_source_ids:
        print("unknown_source_ids:")
        for sid in result.unknown_source_ids:
            print(f"  - {sid}")

    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
