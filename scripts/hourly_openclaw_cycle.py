#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
import shlex
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import orchestrator_autospawn, self_improve
RECEIPT_PATH = ROOT / "memory" / "hourly_cycle_receipts.md"
TASK_PLAN_PATH = ROOT / "memory" / "orchestrator_task_plan.jsonl"
DEFAULT_REMOTE = "origin"
DEFAULT_BRANCH = "main"
DEFAULT_AGENT = "claude"
DEFAULT_AGENT_TIMEOUT_SEC = 300


def default_validation_command() -> list[str]:
    return [self_improve.resolve_validation_python(), "-m", "unittest", "discover", "-s", "tests", "-q"]


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def run_live(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)


def git_status() -> list[str]:
    proc = run(["git", "status", "--short"], check=True)
    return [line for line in proc.stdout.splitlines() if line.strip()]


def git_head() -> str:
    return run(["git", "rev-parse", "HEAD"], check=True).stdout.strip()


def remote_branch_exists(remote: str, branch: str) -> bool:
    proc = run_live(["git", "ls-remote", "--heads", remote, branch])
    return proc.returncode == 0 and bool(proc.stdout.strip())


def branch_is_behind(remote: str, branch: str) -> bool:
    run_live(["git", "fetch", remote, branch])
    local = run(["git", "rev-parse", branch], check=True).stdout.strip()
    remote_ref = f"{remote}/{branch}"
    remote_head = run(["git", "rev-parse", remote_ref], check=True).stdout.strip()
    base = run(["git", "merge-base", branch, remote_ref], check=True).stdout.strip()
    return base == local and local != remote_head


def tracked_changes_only(lines: list[str]) -> list[str]:
    kept: list[str] = []
    for line in lines:
        status = line[:2]
        if status == "??":
            continue
        kept.append(line)
    return kept


def changed_paths(lines: list[str]) -> list[str]:
    paths: list[str] = []
    for line in lines:
        item = line[3:].strip()
        if not item:
            continue
        if " -> " in item:
            item = item.split(" -> ", 1)[1].strip()
        paths.append(item)
    return paths


def run_full_pass(limit: int, dry_run: bool) -> subprocess.CompletedProcess[str]:
    out = io.StringIO()
    err = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        ok = self_improve.full_pass(
            scheduler="host-cron",
            send_telegram=False,
            dry_run=dry_run,
            max_open_items=5,
            with_orchestration=True,
            with_dispatch=False,
            dispatch_limit=limit,
            validation_commands=None,
            foundations_evidence_paths=None,
        )
    return subprocess.CompletedProcess(
        args=["self_improve.full_pass"],
        returncode=0 if ok else 1,
        stdout=out.getvalue(),
        stderr=err.getvalue(),
    )


def load_selected_task() -> dict | None:
    if not TASK_PLAN_PATH.exists():
        return None
    for raw in TASK_PLAN_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line:
            continue
        return json.loads(line)
    return None


def resolve_agent_command(agent: str) -> list[str]:
    if agent == "claude":
        binary = shutil.which("claude") or str(Path.home() / ".local" / "bin" / "claude")
        return [binary, "--permission-mode", "bypassPermissions", "--print"]
    raise ValueError(f"unsupported agent: {agent}")


def build_agent_prompt(task: dict) -> str:
    prompt = orchestrator_autospawn.render_contract_prompt(
        task,
        prompting=orchestrator_autospawn.resolve_prompting_runtime(),
    )
    prompt += (
        "\n\nHourly execution wrapper rules:\n"
        "- This is the single bounded execution slice for the current hourly loop.\n"
        "- Pull directly from the plan goal above and make the smallest real implementation move that advances it.\n"
        "- Prefer code, tests, or concrete spec artifacts over bookkeeping-only edits.\n"
        "- Do not commit or push; leave file changes for the outer wrapper.\n"
        "- If the full goal is too large, do one honest, inspectable sub-slice and say what remains.\n"
        "- If blocked, make the blocker explicit and leave the repo in a validated state if possible."
    )
    return prompt


def run_agent_task(task: dict, *, agent: str, dry_run: bool, timeout_sec: int) -> subprocess.CompletedProcess[str]:
    prompt = build_agent_prompt(task)
    if dry_run:
        return subprocess.CompletedProcess(
            args=[agent],
            returncode=0,
            stdout=prompt,
            stderr="",
        )
    cmd = resolve_agent_command(agent)
    try:
        return subprocess.run(
            cmd + [prompt],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=124,
            stdout=(exc.stdout or ""),
            stderr=((exc.stderr or "") + f"\nagent timed out after {timeout_sec}s").strip(),
        )


def resolve_task_validation_command(task: dict | None) -> list[str]:
    if isinstance(task, dict):
        raw = str(task.get("validation_command", "")).strip()
        if raw:
            return shlex.split(self_improve.normalize_validation_command(raw))
    return default_validation_command()


def run_validation(task: dict | None) -> subprocess.CompletedProcess[str]:
    return run_live(resolve_task_validation_command(task))


def latest_cycle_event() -> dict | None:
    path = self_improve.ORCH_CYCLE_LOG
    if not path.exists():
        return None
    for raw in reversed(path.read_text(encoding="utf-8", errors="ignore").splitlines()):
        line = raw.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    return None


def append_receipt(*, start_head: str, dispatch_limit: int, task: dict | None, agent: str, dry_run: bool) -> None:
    if dry_run:
        return
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not RECEIPT_PATH.exists():
        RECEIPT_PATH.write_text("# Hourly Cycle Receipts\n\n", encoding="utf-8")
    goal = "none"
    section = "none"
    if task:
        goal = str(task.get("goal", "none")).replace("\n", " ").strip()
        section = str(task.get("section", "none")).replace("\n", " ").strip()
    with RECEIPT_PATH.open("a", encoding="utf-8") as fh:
        fh.write(
            f"- {stamp} | start_head={start_head} | dispatch_limit={dispatch_limit} | agent={agent} | section={section} | goal={goal}\n"
        )


def maybe_commit(changed: list[str], *, dry_run: bool) -> tuple[bool, str | None]:
    if not changed:
        return False, None
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"chore: hourly automation cycle {stamp}"
    if dry_run:
        return True, msg
    subprocess.run(["git", "add", "--", *changed], cwd=ROOT, check=True)
    commit = subprocess.run(
        ["git", "commit", "-m", msg], cwd=ROOT, text=True, capture_output=True
    )
    if commit.returncode != 0:
        combined = f"{commit.stdout}\n{commit.stderr}".lower()
        if "nothing to commit" in combined:
            return False, None
        raise RuntimeError((commit.stderr or commit.stdout).strip() or "git commit failed")
    return True, msg


def maybe_push(remote: str, branch: str, *, dry_run: bool) -> tuple[bool, str | None]:
    if not remote_branch_exists(remote, branch):
        return False, f"remote branch missing: {remote}/{branch}"
    if branch_is_behind(remote, branch):
        return False, f"local branch is behind {remote}/{branch}"
    if dry_run:
        return True, None
    proc = subprocess.run(["git", "push", remote, branch], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout).strip() or "git push failed"
    return True, None


def main() -> int:
    ap = argparse.ArgumentParser(description="Run one Sandy Chaos hourly automation cycle with guarded commit/push.")
    ap.add_argument("--dispatch-limit", type=int, default=1)
    ap.add_argument("--remote", default=DEFAULT_REMOTE)
    ap.add_argument("--branch", default=DEFAULT_BRANCH)
    ap.add_argument("--agent", default=DEFAULT_AGENT)
    ap.add_argument("--agent-timeout-sec", type=int, default=DEFAULT_AGENT_TIMEOUT_SEC)
    ap.add_argument("--allow-untracked", action="store_true", help="Include untracked files in the commit set")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    start_head = git_head()
    full_pass = run_full_pass(limit=args.dispatch_limit, dry_run=args.dry_run)
    if full_pass.returncode != 0:
        cycle_event = latest_cycle_event()
        print(json.dumps({
            "ok": False,
            "stage": "full-pass",
            "stdout": full_pass.stdout[-4000:],
            "stderr": full_pass.stderr[-4000:],
            "validation_gate_ok": None if not cycle_event else cycle_event.get("validation_gate_ok"),
            "validation": [] if not cycle_event else cycle_event.get("validation", []),
            "pipeline": {} if not cycle_event else cycle_event.get("pipeline", {}),
        }, indent=2))
        return 1

    selected_task = load_selected_task()
    if not selected_task:
        print(json.dumps({
            "ok": False,
            "stage": "task-selection",
            "stdout": full_pass.stdout[-4000:],
            "stderr": "No task contract produced by orchestrator",
        }, indent=2))
        return 1

    agent_run = run_agent_task(
        selected_task,
        agent=args.agent,
        dry_run=args.dry_run,
        timeout_sec=max(1, args.agent_timeout_sec),
    )
    if agent_run.returncode != 0:
        print(json.dumps({
            "ok": False,
            "stage": "agent-run",
            "task_goal": selected_task.get("goal"),
            "stdout": agent_run.stdout[-4000:],
            "stderr": agent_run.stderr[-4000:],
        }, indent=2))
        return 1

    append_receipt(
        start_head=start_head,
        dispatch_limit=args.dispatch_limit,
        task=selected_task,
        agent=args.agent,
        dry_run=args.dry_run,
    )
    status_lines = git_status()
    candidate_lines = status_lines if args.allow_untracked else tracked_changes_only(status_lines)
    commit_candidates = changed_paths(candidate_lines)

    validation = None
    if commit_candidates and not args.dry_run:
        validation = run_validation(selected_task)
        if validation.returncode != 0:
            print(json.dumps({
                "ok": False,
                "stage": "validation",
                "task_goal": selected_task.get("goal"),
                "changed": commit_candidates,
                "stdout": validation.stdout[-4000:],
                "stderr": validation.stderr[-4000:],
            }, indent=2))
            return 1

    committed, commit_message = maybe_commit(commit_candidates, dry_run=args.dry_run)

    pushed = False
    push_error = None
    if committed:
        pushed, push_error = maybe_push(args.remote, args.branch, dry_run=args.dry_run)

    end_head = git_head()
    result = {
        "ok": push_error is None and agent_run.returncode == 0,
        "repo": str(ROOT),
        "start_head": start_head,
        "end_head": end_head,
        "dispatch_limit": args.dispatch_limit,
        "dry_run": args.dry_run,
        "agent": args.agent,
        "selected_task_goal": selected_task.get("goal"),
        "selected_task_section": selected_task.get("section"),
        "full_pass_tail": full_pass.stdout.splitlines()[-20:],
        "agent_tail": (agent_run.stdout + "\n" + agent_run.stderr).splitlines()[-20:],
        "changed": changed_paths(status_lines),
        "commit_candidates": commit_candidates,
        "validation_ran": bool(validation is not None),
        "validation_ok": None if validation is None else validation.returncode == 0,
        "validation_tail": [] if validation is None else (validation.stdout + "\n" + validation.stderr).splitlines()[-20:],
        "committed": committed,
        "commit_message": commit_message,
        "pushed": pushed,
        "push_error": push_error,
        "cycle_summary": "memory/orchestrator_cycle_summary.md",
    }
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
