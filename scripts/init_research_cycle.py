#!/usr/bin/env python3
"""Initialize a dated research automation artifact bundle.

Creates four files under memory/research by default:
- <date>-query.md
- <date>-evidence.csv
- <date>-synthesis.md
- <date>-falsification.md

Usage:
  python3 scripts/init_research_cycle.py
  python3 scripts/init_research_cycle.py --date 2026-03-02
  python3 scripts/init_research_cycle.py --slug frame-asymmetry
  python3 scripts/init_research_cycle.py --dry-run
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Initialize research-cycle artifact files")
    p.add_argument("--date", help="Date label (YYYY-MM-DD). Defaults to today.")
    p.add_argument("--slug", help="Optional suffix (e.g., frame-asymmetry)")
    p.add_argument(
        "--outdir",
        default="memory/research",
        help="Output directory (default: memory/research)",
    )
    p.add_argument("--dry-run", action="store_true", help="Print paths without writing files")
    return p.parse_args()


def build_prefix(date_label: str, slug: str | None) -> str:
    if slug:
        cleaned = slug.strip().lower().replace(" ", "-")
        return f"{date_label}-{cleaned}"
    return date_label


def main() -> int:
    args = parse_args()
    date_label = args.date or datetime.now().strftime("%Y-%m-%d")
    prefix = build_prefix(date_label, args.slug)

    outdir = Path(args.outdir)
    files = {
        f"{prefix}-query.md": "# Query\n\n## Question\n\n## Scope\n\n## Claim tier\n\n## Failure condition\n",
        f"{prefix}-evidence.csv": "source_id,url_or_doi,query,claim_supported,method_type,dataset_or_context,key_result,limitation,extraction_confidence,reviewer_status,notes\n",
        f"{prefix}-synthesis.md": (
            "# Synthesis\n\n"
            "## Claims\n"
            "- <claim 1> [S001]\n"
            "- <claim 2> [S001][S002]\n\n"
            "## Supportive synthesis\n\n"
            "## Adversarial synthesis\n\n"
            "## Confidence\n"
        ),
        f"{prefix}-falsification.md": "# Falsification\n\n## Primary claim\n\n## Disproof conditions\n1. \n2. \n3. \n\n## Decisive next check\n",
    }

    if args.dry_run:
        for name in files:
            print((outdir / name).as_posix())
        return 0

    outdir.mkdir(parents=True, exist_ok=True)
    created = 0
    skipped = 0

    for name, content in files.items():
        path = outdir / name
        if path.exists():
            skipped += 1
            continue
        path.write_text(content, encoding="utf-8")
        created += 1

    print(f"created={created} skipped={skipped} dir={outdir.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
