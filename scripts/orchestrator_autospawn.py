#!/usr/bin/env python3
"""Auto-spawn plan executor (v1.5 bridge).

Consumes `memory/orchestrator_task_plan.jsonl` and emits concrete OpenClaw
sessions_spawn request payloads for each task contract.

Why bridge mode:
- Repository automation can run unattended on host timers.
- OpenClaw session spawning currently occurs in an active OpenClaw session.
- This script prepares deterministic spawn payloads + dispatch logs so an
  OpenClaw coordinator can execute them immediately.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "memory" / "orchestrator_task_plan.jsonl"
REQUESTS_OUT = ROOT / "memory" / "orchestrator_spawn_requests.json"
DISPATCH_LOG = ROOT / "memory" / "orchestrator_dispatch_log.jsonl"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_jsonl(path: Path) -> list[dict]:
    tasks: list[dict] = []
    if not path.exists():
        return tasks
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if not s:
            continue
        tasks.append(json.loads(s))
    return tasks


def to_spawn_request(task: dict, idx: int) -> dict:
    lane = task.get("lane", "sandy-builder")
    goal = task.get("goal", "(missing goal)")
    section = task.get("section", "(unknown section)")
    constraints = task.get("constraints", [])
    dod = task.get("definition_of_done", [])
    validation = task.get("validation_command", "./venv/bin/python -m unittest -q || true")

    prompt = (
        "You are executing one Sandy-Chaos automation contract.\n"
        f"Lane: {lane}\n"
        f"Section: {section}\n"
        f"Goal: {goal}\n\n"
        "Constraints:\n- " + "\n- ".join(constraints) + "\n\n"
        "Definition of done:\n- " + "\n- ".join(dod) + "\n\n"
        f"Validation command: {validation}\n"
        "Work in ${REPO_ROOT}. Make scoped changes and commit when done."
    )

    return {
        "id": f"spawn-{idx:02d}",
        "createdAt": now_iso(),
        "lane": lane,
        "spawn": {
            "runtime": "subagent",
            "mode": "run",
            "cleanup": "delete",
            "model": "openai-codex/gpt-5.3-codex",
            "cwd": "${REPO_ROOT}",
            "task": prompt,
        },
    }


def append_dispatch_log(entry: dict) -> None:
    DISPATCH_LOG.parent.mkdir(parents=True, exist_ok=True)
    with DISPATCH_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default=str(DEFAULT_PLAN))
    ap.add_argument("--out", default=str(REQUESTS_OUT))
    ap.add_argument("--limit", type=int, default=3)
    args = ap.parse_args()

    plan_path = Path(args.plan)
    out_path = Path(args.out)

    tasks = load_jsonl(plan_path)
    selected = tasks[: max(0, args.limit)]

    requests = [to_spawn_request(task, i + 1) for i, task in enumerate(selected)]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"generatedAt": now_iso(), "requests": requests}, indent=2), encoding="utf-8")

    append_dispatch_log(
        {
            "ts": now_iso(),
            "event": "spawn_requests_prepared",
            "plan": str(plan_path),
            "out": str(out_path),
            "count": len(requests),
        }
    )

    print(f"Prepared {len(requests)} spawn requests -> {out_path}")
    print("Next step: OpenClaw coordinator consumes this file and calls sessions_spawn for each request.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
