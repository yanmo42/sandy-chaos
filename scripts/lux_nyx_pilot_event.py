#!/usr/bin/env python3
"""Record one Lux–Nyx pilot measurement event.

The CLI is intentionally thin over `lux_nyx_metrics`: it records causal events
that actually happened in the workflow and rewrites the pilot report after each
update.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nfem_suite.intelligence.narrative_invariants.lux_nyx_metrics import (  # noqa: E402
    PilotMetrics,
    build_pilot_report,
    record_acceptance,
    record_archive_to_promotion,
    record_correction,
    record_promotion,
    record_suggestion,
)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Record a Lux–Nyx pilot metric event")
    ap.add_argument(
        "event",
        choices=("suggestion", "acceptance", "correction", "promotion", "archive-to-promotion"),
        help="Event type to record",
    )
    ap.add_argument("--root", default=str(ROOT), help="Repo root containing state/lux_nyx")
    ap.add_argument("--count", type=int, default=1, help="Positive event count")
    ap.add_argument("--action", default="", help="Optional suggestion action label for traceability")
    return ap.parse_args()


def _record_many(root: Path, count: int, fn: Callable[[], PilotMetrics]) -> PilotMetrics:
    metrics = PilotMetrics.load(root)
    for _ in range(count):
        metrics = fn()
    return metrics


def main() -> int:
    args = parse_args()
    root = Path(args.root)
    count = int(args.count)
    if count <= 0:
        print("--count must be positive", file=sys.stderr)
        return 2

    try:
        if args.event == "suggestion":
            metrics = _record_many(root, count, lambda: record_suggestion(root, action=args.action or None))
        elif args.event == "acceptance":
            metrics = record_acceptance(root, count=count)
        elif args.event == "correction":
            metrics = record_correction(root, count=count)
        elif args.event == "promotion":
            metrics = record_promotion(root, count=count)
        elif args.event == "archive-to-promotion":
            metrics = record_archive_to_promotion(root, count=count)
        else:  # pragma: no cover - argparse prevents this
            raise AssertionError(args.event)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    report = build_pilot_report(metrics)
    print(json.dumps({
        "status": "ok",
        "event": args.event,
        "count": count,
        "counts": report["counts"],
        "metrics": report["metrics"],
        "promotion_verdict": report["promotion_verdict"],
        "metrics_path": str((root / "state" / "lux_nyx" / "metrics.json").resolve()),
        "report_path": str((root / "state" / "lux_nyx" / "pilot_report.json").resolve()),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
