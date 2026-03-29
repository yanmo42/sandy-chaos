#!/usr/bin/env python3
"""Deterministic two-bucket file search with safety excludes.

Bucket A: meaning artifacts (docs/data/specs)
Bucket B: execution machinery (code/tests/validators)

Exits non-zero if either bucket is empty.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_ARTIFACTS = r"docs/symbolic-maps|schemas/symbolic_operator\.schema|starter_atlas"
DEFAULT_MACHINERY = r"narrative_invariants|test_narrative_invariants|validator|normalize"
DEFAULT_EXCLUDES = {"venv", ".git", "__pycache__", ".pytest_cache", "node_modules"}


def iter_files(root: Path, excludes: set[str]):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in excludes for part in path.parts):
            continue
        yield path


def collect(root: Path, pattern: re.Pattern[str], excludes: set[str]) -> list[str]:
    out: list[str] = []
    for path in iter_files(root, excludes):
        rel = path.relative_to(root).as_posix()
        if pattern.search(rel):
            out.append(rel)
    return sorted(out)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Two-bucket search for artifacts and machinery")
    p.add_argument("--root", default=".", help="Repository root (default: current directory)")
    p.add_argument("--artifacts", default=DEFAULT_ARTIFACTS, help="Regex for artifact bucket")
    p.add_argument("--machinery", default=DEFAULT_MACHINERY, help="Regex for machinery bucket")
    p.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Extra path part to exclude (repeatable).",
    )
    p.add_argument("--quiet", action="store_true", help="Only set exit code, no listing")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()

    if not root.exists() or not root.is_dir():
        print(f"ERR: root is not a directory: {root}", file=sys.stderr)
        return 2

    excludes = set(DEFAULT_EXCLUDES)
    excludes.update(args.exclude)

    try:
        artifacts_re = re.compile(args.artifacts)
        machinery_re = re.compile(args.machinery)
    except re.error as exc:
        print(f"ERR: invalid regex: {exc}", file=sys.stderr)
        return 2

    artifacts = collect(root, artifacts_re, excludes)
    machinery = collect(root, machinery_re, excludes)

    if not artifacts:
        print("ERR: artifacts bucket empty", file=sys.stderr)
        return 1
    if not machinery:
        print("ERR: machinery bucket empty", file=sys.stderr)
        return 1

    if not args.quiet:
        print("== Artifacts ==")
        for p in artifacts:
            print(p)
        print("\n== Machinery ==")
        for p in machinery:
            print(p)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
