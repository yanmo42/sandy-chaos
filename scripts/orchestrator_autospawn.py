#!/usr/bin/env python3
"""Auto-spawn plan executor (v2).

Consumes `memory/orchestrator_task_plan.jsonl`, emits concrete OpenClaw
`sessions_spawn` request payloads, and can optionally dispatch them through the
Gateway sessions API.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
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


def resolve_openclaw_command() -> list[str]:
    env_bin = os.environ.get("OPENCLAW_BIN", "").strip()
    candidates: list[Path] = []
    if env_bin:
        candidates.append(Path(env_bin).expanduser())

    candidates.extend(
        [
            Path.home() / ".npm-global" / "bin" / "openclaw",
            Path("/usr/local/bin/openclaw"),
            Path("/usr/bin/openclaw"),
        ]
    )

    for c in candidates:
        try:
            if c.is_file() and os.access(c, os.X_OK):
                return [str(c)]
        except Exception:
            continue

    found = shutil.which("openclaw")
    if found:
        return [found]

    return []


def dispatch_spawn_requests(requests: list[dict], dry_run: bool = False) -> dict:
    out = {"attempted": 0, "dispatched": 0, "errors": [], "results": []}

    openclaw_cmd = resolve_openclaw_command()
    if not openclaw_cmd:
        out["errors"].append("openclaw binary not found")
        return out

    for req in requests:
        out["attempted"] += 1
        spawn = req.get("spawn", {})
        cmd = openclaw_cmd + [
            "gateway",
            "call",
            "sessions_spawn",
            "--json",
            "--timeout",
            "120000",
            "--params",
            json.dumps(spawn, ensure_ascii=False),
        ]

        if dry_run:
            out["dispatched"] += 1
            out["results"].append({"id": req.get("id"), "ok": True, "dry_run": True})
            append_dispatch_log(
                {
                    "ts": now_iso(),
                    "event": "spawn_dispatched",
                    "id": req.get("id"),
                    "ok": True,
                    "dry_run": True,
                    "method": "sessions_spawn",
                }
            )
            continue

        try:
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=130)
            ok = proc.returncode == 0
            result = {
                "id": req.get("id"),
                "ok": ok,
                "stdout": (proc.stdout or "").strip()[:2000],
                "stderr": (proc.stderr or "").strip()[:2000],
            }
            out["results"].append(result)
            if ok:
                out["dispatched"] += 1
            else:
                out["errors"].append(f"{req.get('id', 'unknown')}: {(proc.stderr or proc.stdout or '').strip()}")

            append_dispatch_log(
                {
                    "ts": now_iso(),
                    "event": "spawn_dispatched",
                    "id": req.get("id"),
                    "ok": ok,
                    "dry_run": False,
                    "method": "sessions_spawn",
                    "stdout": result["stdout"],
                    "stderr": result["stderr"],
                }
            )
        except Exception as exc:
            out["errors"].append(f"{req.get('id', 'unknown')}: {exc}")
            append_dispatch_log(
                {
                    "ts": now_iso(),
                    "event": "spawn_dispatched",
                    "id": req.get("id"),
                    "ok": False,
                    "dry_run": False,
                    "method": "sessions_spawn",
                    "error": str(exc),
                }
            )

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default=str(DEFAULT_PLAN))
    ap.add_argument("--out", default=str(REQUESTS_OUT))
    ap.add_argument("--limit", type=int, default=3)
    ap.add_argument("--execute", action="store_true", help="Call OpenClaw sessions API (sessions_spawn) for each request")
    ap.add_argument("--dry-run", action="store_true", help="Prepare/dispatch without making API calls")
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

    if args.execute:
        result = dispatch_spawn_requests(requests=requests, dry_run=args.dry_run)
        print(
            f"Dispatch complete via sessions_spawn: dispatched={result['dispatched']} "
            f"attempted={result['attempted']} errors={len(result['errors'])}"
        )
        if result["errors"]:
            for e in result["errors"]:
                print(f"- {e}")
            return 1
    else:
        print("Next step: run with --execute to dispatch via OpenClaw sessions_spawn API.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
