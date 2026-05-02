#!/usr/bin/env python3
"""Write and print the Lux–Nyx pilot measurement report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nfem_suite.intelligence.narrative_invariants.lux_nyx_metrics import (  # noqa: E402
    PilotMetrics,
    build_pilot_report,
    write_pilot_report,
)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Write Lux–Nyx pilot report")
    ap.add_argument("--root", default=str(ROOT), help="Repo root containing state/lux_nyx")
    ap.add_argument("--summary", action="store_true", help="Print compact summary instead of full report JSON")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root)
    metrics = PilotMetrics.load(root)
    report_path = write_pilot_report(root, metrics)
    report = build_pilot_report(metrics)

    if args.summary:
        payload = {
            "status": "ok",
            "baseline_configured": report["baseline_configured"],
            "counts": report["counts"],
            "metrics": report["metrics"],
            "promotion_verdict": report["promotion_verdict"],
            "report_path": str(report_path.resolve()),
        }
    else:
        payload = {"status": "ok", "report_path": str(report_path.resolve()), "report": report}

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
