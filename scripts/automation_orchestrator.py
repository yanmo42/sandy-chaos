#!/usr/bin/env python3
"""Sandy automation orchestrator (v1).

Purpose:
- Select high-priority TODO items
- Build explicit subagent task contracts
- Emit task plan JSONL for OpenClaw `sessions_spawn`
- Write cycle summary for human + reporter lane

This script is intentionally transport-agnostic: it prepares task contracts that
can be executed by OpenClaw subagents from chat or TUI.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class TodoItem:
    state: str  # open|partial
    text: str
    section: str


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_todo(todo_path: Path) -> List[TodoItem]:
    section = "(root)"
    items: List[TodoItem] = []
    checkbox = re.compile(r"^\s*-\s*\[(.| )\]\s+(.*)$")

    for raw in todo_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        m = checkbox.match(line)
        if not m:
            continue

        mark, text = m.group(1), m.group(2).strip()
        if mark in {"x", "X", "✅"}:
            continue
        state = "partial" if mark == "🟡" else "open"
        items.append(TodoItem(state=state, text=text, section=section))

    return items


def git_status_short(cwd: Path) -> list[str]:
    try:
        out = subprocess.check_output(["git", "status", "--short"], cwd=cwd, text=True)
        return [ln for ln in out.splitlines() if ln.strip()]
    except Exception:
        return []


def rank_items(items: List[TodoItem], prefer_sections: list[str], include_partial: bool, limit: int) -> List[TodoItem]:
    ranked = []
    for item in items:
        if item.state == "partial" and not include_partial:
            continue
        score = 0
        if any(pref.lower() in item.section.lower() for pref in prefer_sections):
            score += 10
        if "agency" in item.text.lower() or "temporal" in item.text.lower():
            score += 4
        if "test" in item.text.lower() or "falsification" in item.text.lower():
            score += 2
        ranked.append((score, item))

    ranked.sort(key=lambda x: x[0], reverse=True)
    return [it for _, it in ranked[:limit]]


def task_contract(item: TodoItem) -> dict:
    lane = "sandy-builder"
    if "document" in item.text.lower() or "claim tier" in item.text.lower():
        lane = "sandy-planner"
    if "test" in item.text.lower() or "falsification" in item.text.lower() or "verify" in item.text.lower():
        lane = "sandy-verifier"

    validation = "./venv/bin/python -m unittest -q || true"
    if lane == "sandy-planner":
        validation = "python3 scripts/todo_scan.py plans/todo.md"

    return {
        "lane": lane,
        "goal": item.text,
        "section": item.section,
        "constraints": [
            "Use openai-codex/gpt-5.3-codex",
            "Keep strict causality; no retrocausal claims",
            "Update tests/docs for any behavioral change",
            "Commit scoped changes with clear message"
        ],
        "definition_of_done": [
            "Relevant files updated",
            "Validation command executed",
            "Short completion note prepared"
        ],
        "validation_command": validation,
    }


def write_jsonl(path: Path, tasks: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for t in tasks:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")


def write_summary(path: Path, selected: List[TodoItem], git_lines: list[str], plan_path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Orchestrator Cycle Summary ({now()})",
        "",
        "## Selected tasks",
    ]
    if selected:
        for i, it in enumerate(selected, 1):
            lines.append(f"{i}. [{it.state}] {it.text} ({it.section})")
    else:
        lines.append("- none")

    lines += ["", "## Git working tree"]
    if git_lines:
        lines.extend([f"- {g}" for g in git_lines])
    else:
        lines.append("- clean")
    lines += ["", f"Task plan JSONL: `{plan_path}`", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config" / "orchestrator.json"))
    args = ap.parse_args()

    cfg = load_json(Path(args.config))
    repo = Path(cfg["repoRoot"])
    todo = repo / cfg["todoPath"]

    items = parse_todo(todo)
    selected = rank_items(
        items,
        prefer_sections=cfg["taskSelection"]["prefer"],
        include_partial=bool(cfg["taskSelection"].get("includePartial", True)),
        limit=int(cfg.get("maxTasksPerCycle", 3)),
    )
    tasks = [task_contract(it) for it in selected]

    out_plan = repo / cfg["output"]["taskPlanJsonl"]
    out_summary = repo / cfg["output"]["cycleSummary"]

    write_jsonl(out_plan, tasks)
    write_summary(out_summary, selected, git_status_short(repo), out_plan)

    print(f"Prepared {len(tasks)} task contracts -> {out_plan}")
    print(f"Summary -> {out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
