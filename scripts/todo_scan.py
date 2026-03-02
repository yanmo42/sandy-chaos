#!/usr/bin/env python3
"""Lightweight TODO/progress scanner for markdown project lists.

Scans markdown files for:
- checkboxes: - [ ] / - [x]
- status markers in text/tables: ✅, 🟡, ⬜, Open, Partial, Resolved

Usage:
  python scripts/todo_scan.py plans/todo.md
  python scripts/todo_scan.py plans docs
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from dataclasses import dataclass

CHECKBOX_RE = re.compile(r"^\s*[-*]\s*\[(?P<mark>[ xX])\]\s+")

@dataclass
class Counts:
    done: int = 0
    open: int = 0
    partial: int = 0

    @property
    def total(self) -> int:
        return self.done + self.open + self.partial

    @property
    def pct(self) -> float:
        return (self.done / self.total * 100.0) if self.total else 0.0


def scan_text(text: str) -> Counts:
    c = Counts()

    for line in text.splitlines():
        m = CHECKBOX_RE.match(line)
        if m:
            if m.group("mark").strip().lower() == "x":
                c.done += 1
            else:
                c.open += 1
            continue

        # Table/status line heuristics
        # Prioritize explicit emoji signals first.
        if "✅" in line:
            c.done += 1
            continue
        if "🟡" in line:
            c.partial += 1
            continue
        if "⬜" in line:
            c.open += 1
            continue

        # Fallback plain-language statuses.
        low = line.lower()
        if "status" in low and "|" in line:
            if "resolved" in low:
                c.done += 1
            elif "partial" in low:
                c.partial += 1
            elif "open" in low:
                c.open += 1

    return c


def iter_markdown_files(inputs: list[str]):
    for item in inputs:
        p = Path(item)
        if not p.exists():
            continue
        if p.is_file() and p.suffix.lower() == ".md":
            yield p
        elif p.is_dir():
            yield from sorted(p.rglob("*.md"))


def main(argv: list[str]) -> int:
    targets = argv[1:] or ["plans"]
    files = list(iter_markdown_files(targets))
    if not files:
        print("No markdown files found.")
        return 1

    grand = Counts()
    print("TODO Scan Report")
    print("=" * 60)

    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        c = scan_text(text)
        if c.total == 0:
            continue

        grand.done += c.done
        grand.open += c.open
        grand.partial += c.partial

        print(f"{f}:")
        print(f"  done={c.done}  partial={c.partial}  open={c.open}  total={c.total}  completion={c.pct:.1f}%")

    print("-" * 60)
    print(
        f"TOTAL: done={grand.done}  partial={grand.partial}  open={grand.open}  total={grand.total}  completion={grand.pct:.1f}%"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
