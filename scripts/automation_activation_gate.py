#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STAGE = "off"
ALLOWED_STAGES = {"off", "preflight", "dry-run", "local", "live"}
DEFAULT_AGENT = "claude"
DEFAULT_DISPATCH_LIMIT = 1
DEFAULT_AGENT_TIMEOUT_SEC = 600


def read_env_int(name: str, default: int) -> int:
    raw = str(os.environ.get(name, default)).strip()
    try:
        value = int(raw)
    except ValueError:
        return default
    return value


def read_env_bool(name: str, default: bool = False) -> bool:
    raw = str(os.environ.get(name, "1" if default else "0")).strip().lower()
    return raw in {"1", "true", "yes", "on"}


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)


def tracked_worktree_clean() -> tuple[bool, str]:
    proc = run(["git", "status", "--short", "--untracked-files=no"])
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout).strip() or "git status failed"
    dirty = [line for line in proc.stdout.splitlines() if line.strip()]
    if dirty:
        return False, "tracked working tree is dirty"
    return True, "tracked working tree clean"


def required_binary(name: str) -> tuple[bool, str]:
    path = shutil.which(name)
    if path:
        return True, path
    return False, f"{name} not found on PATH"


def preflight(stage: str, agent: str) -> dict:
    checks: list[dict] = []

    def record(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    record("repo_root", ROOT.is_dir(), str(ROOT))
    record("git_dir", (ROOT / ".git").is_dir(), str(ROOT / ".git"))
    ok, detail = required_binary("python3")
    record("python3", ok, detail)
    ok, detail = required_binary("git")
    record("git", ok, detail)

    if stage in {"local", "live"}:
        ok, detail = required_binary(agent)
        record(f"agent:{agent}", ok, detail)

    ok, detail = tracked_worktree_clean()
    if stage in {"local", "live"}:
        record("tracked_worktree_clean", ok, detail)
    else:
        record("tracked_worktree_clean", True, f"advisory: {detail}")

    return {
        "ok": all(item["ok"] for item in checks),
        "checks": checks,
    }


def build_hourly_command(
    *,
    stage: str,
    agent: str,
    dispatch_limit: int,
    agent_timeout_sec: int,
    send_telegram: bool,
) -> list[str]:
    cmd = [
        sys.executable or "python3",
        str(ROOT / "scripts" / "hourly_openclaw_cycle.py"),
        "--dispatch-limit",
        str(dispatch_limit),
        "--agent",
        agent,
        "--agent-timeout-sec",
        str(agent_timeout_sec),
    ]
    if stage == "dry-run":
        cmd.append("--dry-run")
    if stage == "live":
        cmd.extend(["--allow-commit", "--allow-push"])
    if send_telegram:
        cmd.append("--send-telegram")
    return cmd


def main() -> int:
    stage = str(os.environ.get("SANDY_AUTOMATION_STAGE", DEFAULT_STAGE)).strip().lower()
    agent = str(os.environ.get("SANDY_AUTOMATION_AGENT", DEFAULT_AGENT)).strip() or DEFAULT_AGENT
    dispatch_limit = max(1, read_env_int("SANDY_AUTOMATION_DISPATCH_LIMIT", DEFAULT_DISPATCH_LIMIT))
    agent_timeout_sec = max(1, read_env_int("SANDY_AUTOMATION_AGENT_TIMEOUT_SEC", DEFAULT_AGENT_TIMEOUT_SEC))
    send_telegram = read_env_bool("SANDY_AUTOMATION_SEND_TELEGRAM", default=False)

    if stage not in ALLOWED_STAGES:
        print(
            json.dumps(
                {
                    "ok": False,
                    "stage": stage,
                    "error": f"invalid stage: {stage}",
                    "allowed_stages": sorted(ALLOWED_STAGES),
                },
                indent=2,
            )
        )
        return 2

    if stage == "off":
        print(
            json.dumps(
                {
                    "ok": True,
                    "stage": stage,
                    "skipped": True,
                    "reason": "automation stage is off",
                },
                indent=2,
            )
        )
        return 0

    pf = preflight(stage, agent)
    summary = {
        "ok": pf["ok"],
        "stage": stage,
        "agent": agent,
        "dispatch_limit": dispatch_limit,
        "agent_timeout_sec": agent_timeout_sec,
        "send_telegram": send_telegram,
        "preflight": pf["checks"],
    }

    if not pf["ok"] or stage == "preflight":
        print(json.dumps(summary, indent=2))
        return 0 if pf["ok"] else 1

    cmd = build_hourly_command(
        stage=stage,
        agent=agent,
        dispatch_limit=dispatch_limit,
        agent_timeout_sec=agent_timeout_sec,
        send_telegram=send_telegram,
    )
    proc = run(cmd)
    summary["command"] = cmd
    summary["command_ok"] = proc.returncode == 0
    summary["stdout_tail"] = proc.stdout.splitlines()[-40:]
    summary["stderr_tail"] = proc.stderr.splitlines()[-40:]
    summary["ok"] = summary["ok"] and summary["command_ok"]
    print(json.dumps(summary, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
