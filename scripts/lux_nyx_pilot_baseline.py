#!/usr/bin/env python3
"""Freeze explicit Lux–Nyx pilot baseline metrics.

Baselines are deliberately opt-in. If historical pre-Lux/Nyx data is absent,
use `--from-current` only as a named proxy and keep the source label honest.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nfem_suite.intelligence.narrative_invariants.lux_nyx_metrics import (  # noqa: E402
    HEADLINE_METRIC_KEYS,
    PilotMetrics,
    build_pilot_report,
    set_baseline_metrics,
)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Freeze Lux–Nyx pilot baseline metrics")
    ap.add_argument("--root", default=str(ROOT), help="Repo root containing state/lux_nyx")
    ap.add_argument("--source", required=True, help="Human-readable baseline source/provenance")
    ap.add_argument("--observed-at", default="", help="Optional ISO timestamp for baseline observation")
    ap.add_argument(
        "--from-current",
        action="store_true",
        help="Use current measured metric values as an explicit proxy baseline",
    )
    ap.add_argument("--suggestion-acceptance-rate", type=float)
    ap.add_argument("--correction-burden-per-suggestion", type=float)
    ap.add_argument("--archive-to-promotion-conversion-quality", type=float)
    return ap.parse_args()


def _validate_unit_interval(name: str, value: float) -> None:
    if value < 0.0 or value > 1.0:
        raise ValueError(f"{name} must be in [0, 1]")


def main() -> int:
    args = parse_args()
    root = Path(args.root)

    provided = {
        "suggestion_acceptance_rate": args.suggestion_acceptance_rate,
        "correction_burden_per_suggestion": args.correction_burden_per_suggestion,
        "archive_to_promotion_conversion_quality": args.archive_to_promotion_conversion_quality,
    }

    if args.from_current:
        baseline_values = PilotMetrics.load(root).current_metric_values()
    else:
        missing = [key for key, value in provided.items() if value is None]
        if missing:
            print(
                "baseline values required unless --from-current is set; missing: " + ", ".join(missing),
                file=sys.stderr,
            )
            return 2
        baseline_values = {key: float(value) for key, value in provided.items() if value is not None}

    try:
        for key in HEADLINE_METRIC_KEYS:
            _validate_unit_interval(key, float(baseline_values[key]))
    except (KeyError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    metrics = set_baseline_metrics(
        root,
        baseline_values,
        baseline_source=args.source,
        baseline_observed_at=args.observed_at,
    )
    report = build_pilot_report(metrics)
    print(json.dumps({
        "status": "ok",
        "baseline_source": report["baseline_source"],
        "baseline_observed_at": report["baseline_observed_at"],
        "baseline_configured": report["baseline_configured"],
        "baseline_metrics": metrics.baseline_metrics,
        "promotion_verdict": report["promotion_verdict"],
        "metrics_path": str((root / "state" / "lux_nyx" / "metrics.json").resolve()),
        "report_path": str((root / "state" / "lux_nyx" / "pilot_report.json").resolve()),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
