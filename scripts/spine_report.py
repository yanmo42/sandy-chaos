#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
import sys

from scripts import spine_common


def main() -> int:
    if not spine_common.CONCEPT_DIR.exists():
        print("No spine concepts directory found.", file=sys.stderr)
        return 1

    concepts = [item.data for item in spine_common.load_concepts()]
    if not concepts:
        print("No concept files found.")
        return 0

    status_counts = Counter(str(c.get("status", "unknown")) for c in concepts)
    tier_counts = Counter(str(c.get("claim_tier", "unknown")) for c in concepts)
    lane_counts = Counter(str(c.get("lane", "unknown")) for c in concepts)

    print("SANDY CHAOS SPINE REPORT")
    print("=" * 24)
    print(f"Concept count: {len(concepts)}")
    print()

    print("By status:")
    for key, value in sorted(status_counts.items()):
        print(f"  {key}: {value}")
    print()

    print("By claim tier:")
    for key, value in sorted(tier_counts.items()):
        print(f"  {key}: {value}")
    print()

    print("By lane:")
    for key, value in sorted(lane_counts.items()):
        print(f"  {key}: {value}")
    print()

    missing_tests = [c for c in concepts if not c.get("tested_by")]
    missing_failures = [c for c in concepts if not c.get("failure_conditions")]
    ygg_bound = [c for c in concepts if str(c.get("promotion_target", "")).startswith("ygg") or c.get("owner_surface") in {"shared-with-ygg", "ygg-candidate"}]

    print("Missing tests:")
    for c in missing_tests:
        print(f"  {c.get('id')}: {c.get('name')}")
    if not missing_tests:
        print("  none")
    print()

    print("Missing failure conditions:")
    for c in missing_failures:
        print(f"  {c.get('id')}: {c.get('name')}")
    if not missing_failures:
        print("  none")
    print()

    print("Ygg-bound / shared concepts:")
    for c in ygg_bound:
        print(f"  {c.get('id')}: {c.get('name')} -> {c.get('promotion_target')}")
    if not ygg_bound:
        print("  none")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
