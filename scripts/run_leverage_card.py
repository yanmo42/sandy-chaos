#!/usr/bin/env python3
"""Score a causal leverage card and optionally emit its evidence payload.

Usage:
    python scripts/run_leverage_card.py path/to/card.json
    python scripts/run_leverage_card.py card.json --emit-evidence out.json
    python scripts/run_leverage_card.py --batch memory/research/leverage/

Exit codes:
    0 — all scored cards resolve to PASS or REVIEW
    1 — at least one card resolves to FAIL or fails to load
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from nfem_suite.intelligence.leverage import (  # noqa: E402
    evidence_payload,
    load_card,
    score_card,
)


def _score_one(path: Path, emit_evidence: Path | None) -> tuple[str, dict]:
    card = load_card(path)
    report = score_card(card)
    result = {
        "card_path": str(path),
        "card_id": card.card_id,
        "report": report.to_dict(),
        "evidence": evidence_payload(card, report),
    }
    if emit_evidence is not None:
        emit_evidence.parent.mkdir(parents=True, exist_ok=True)
        emit_evidence.write_text(
            json.dumps(result["evidence"], indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return report.decision, result


def _iter_cards(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(p for p in path.glob("*.json") if not p.name.endswith(".evidence.json"))
    return [path]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score sandy-chaos causal leverage cards")
    parser.add_argument("card", help="Path to a card JSON file or a directory of cards")
    parser.add_argument(
        "--emit-evidence",
        nargs="?",
        const="__sibling__",
        default=None,
        help=(
            "Write evidence payload(s). With no argument, writes <card>.evidence.json "
            "next to each card; otherwise treats the argument as an output path "
            "(single card) or directory (batch)."
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print final summary line and FAIL details.",
    )
    args = parser.parse_args(argv)

    root = Path(args.card)
    if not root.exists():
        print(f"card path does not exist: {root}", file=sys.stderr)
        return 1

    cards = _iter_cards(root)
    if not cards:
        print(f"no leverage cards found at {root}", file=sys.stderr)
        return 1

    summary = {"PASS": 0, "REVIEW": 0, "FAIL": 0}
    exit_code = 0

    for card_path in cards:
        if args.emit_evidence == "__sibling__":
            evidence_out: Path | None = card_path.with_suffix(".evidence.json")
        elif args.emit_evidence is not None:
            evidence_arg = Path(args.emit_evidence)
            if len(cards) > 1 or evidence_arg.is_dir():
                evidence_out = evidence_arg / (card_path.stem + ".evidence.json")
            else:
                evidence_out = evidence_arg
        else:
            evidence_out = None

        try:
            decision, result = _score_one(card_path, evidence_out)
        except Exception as exc:
            print(f"FAIL: {card_path}: {exc}", file=sys.stderr)
            summary["FAIL"] += 1
            exit_code = 1
            continue

        summary[decision] = summary.get(decision, 0) + 1
        if decision == "FAIL":
            exit_code = 1

        if not args.quiet or decision == "FAIL":
            print(json.dumps(result, indent=2, sort_keys=True))

    print(
        f"leverage-card summary: pass={summary['PASS']} "
        f"review={summary['REVIEW']} fail={summary['FAIL']}"
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
