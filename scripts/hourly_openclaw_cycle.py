#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = ROOT / "memory" / "hourly_cycle_receipts.jsonl"
DEFAULT_VALIDATION = ["./venv/bin/python", "-m", "unittest", "discover", "-s", "tests", "-q"]
DEFAULT_REMOTE = "origin"
DEFAULT_BRANCH = "main"


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
    cmd = [
        "python3",
        "scripts/self_improve.py",
        "full-pass",
        "--scheduler",
        "host-cron",
        "--with-orchestration",
        "--with-dispatch",
        "--dispatch-limit",
        str(limit),
    ]
    if dry_run:
        cmd.append("--dry-run")
    return run_live(cmd)


def run_validation() -> subprocess.CompletedProcess[str]:
    return run_live(DEFAULT_VALIDATION)


def append_receipt(*, start_head: str, dispatch_limit: int, dry_run: bool) -> None:
    if dry_run:
        return
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "start_head": start_head,
        "dispatch_limit": dispatch_limit,
    }
    with RECEIPT_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def maybe_commit(changed: list[str], *, dry_run: bool) -> tuple[bool, str | None]:
    if not changed:
        return False, None
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"chore: hourly automation cycle {stamp}"
    if dry_run:
        return True, msg
    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
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
    ap.add_argument("--allow-untracked", action="store_true", help="Include untracked files in the commit set")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    start_head = git_head()
    full_pass = run_full_pass(limit=args.dispatch_limit, dry_run=args.dry_run)
    if full_pass.returncode != 0:
        print(json.dumps({
            "ok": False,
            "stage": "full-pass",
            "stdout": full_pass.stdout[-4000:],
            "stderr": full_pass.stderr[-4000:],
        }, indent=2))
        return 1

    append_receipt(start_head=start_head, dispatch_limit=args.dispatch_limit, dry_run=args.dry_run)
    status_lines = git_status()
    commit_candidates = status_lines if args.allow_untracked else tracked_changes_only(status_lines)

    validation = None
    if commit_candidates and not args.dry_run:
        validation = run_validation()
        if validation.returncode != 0:
            print(json.dumps({
                "ok": False,
                "stage": "validation",
                "changed": changed_paths(commit_candidates),
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
        "ok": push_error is None,
        "repo": str(ROOT),
        "start_head": start_head,
        "end_head": end_head,
        "dispatch_limit": args.dispatch_limit,
        "dry_run": args.dry_run,
        "full_pass_tail": full_pass.stdout.splitlines()[-20:],
        "changed": changed_paths(status_lines),
        "commit_candidates": changed_paths(commit_candidates),
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
