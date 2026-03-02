#!/usr/bin/env python3
"""Automation helpers for assistant self-improvement loops.

Examples:
  python3 scripts/self_improve.py fast "miss=too verbose; fix=shorter bullets"
  python3 scripts/self_improve.py post-task \
    --context "User asked for quick recap" \
    --decision "Used bullets + one recommendation" \
    --outcome "Accepted without follow-up" \
    --policy-tweak "Default to 4 bullets max for recaps"
  python3 scripts/self_improve.py daily
  python3 scripts/self_improve.py weekly
  python3 scripts/self_improve.py run --scheduler heartbeat --dry-run
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
MEMORY_DIR = ROOT / "memory"
STATE_PATH = MEMORY_DIR / "self_improve_state.json"
NOTIFY_OUTBOX = MEMORY_DIR / "notification_outbox.md"


def now_dt() -> datetime:
    return datetime.now()


def today_str() -> str:
    return now_dt().strftime("%Y-%m-%d")


def ensure_memory_file() -> Path:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    f = MEMORY_DIR / f"{today_str()}.md"
    if not f.exists():
        f.write_text(f"# {today_str()}\n\n", encoding="utf-8")
    return f


def load_state() -> dict:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_PATH.exists():
        return {
            "scheduler_source": "heartbeat",
            "last_run": {"daily": None, "weekly": None},
            "missed_runs": {"daily": 0, "weekly": 0},
            "policy_tweak_counts": {},
        }

    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {
            "scheduler_source": "heartbeat",
            "last_run": {"daily": None, "weekly": None},
            "missed_runs": {"daily": 0, "weekly": 0},
            "policy_tweak_counts": {},
        }


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fast(note: str) -> None:
    f = ensure_memory_file()
    with f.open("a", encoding="utf-8") as out:
        out.write(f"- FAST_LOOP: {note.strip()}\n")
    print(f"Appended fast-loop note to {f}")


def post_task(context: str, decision: str, outcome: str, policy_tweak: str) -> None:
    """Enforce a structured post-task log schema."""
    f = ensure_memory_file()
    stamp = now_dt().strftime("%Y-%m-%d %H:%M")

    with f.open("a", encoding="utf-8") as out:
        out.write(
            "\n"
            f"## POST_TASK_LOG ({stamp})\n"
            f"- context: {context.strip()}\n"
            f"- decision: {decision.strip()}\n"
            f"- outcome: {outcome.strip()}\n"
            f"- policy_tweak: {policy_tweak.strip()}\n"
        )

    state = load_state()
    tweaks = state.setdefault("policy_tweak_counts", {})
    key = policy_tweak.strip()
    tweaks[key] = int(tweaks.get(key, 0)) + 1
    save_state(state)

    print(f"Appended post-task schema entry to {f}")


def scaffold(kind: str) -> Path:
    if kind == "daily":
        src = TEMPLATES / "daily_meso_review.md"
        dst = MEMORY_DIR / f"{today_str()}-meso-review.md"
    elif kind == "weekly":
        src = TEMPLATES / "weekly_slow_distill.md"
        year, week, _ = now_dt().isocalendar()
        dst = MEMORY_DIR / f"{year}-W{week:02d}-slow-distill.md"
    else:
        raise ValueError("kind must be 'daily' or 'weekly'")

    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        print(f"Already exists: {dst}")
        return dst

    shutil.copyfile(src, dst)
    print(f"Created: {dst}")
    return dst


def queue_notification(text: str, dry_run: bool) -> None:
    stamp = now_dt().strftime("%Y-%m-%d %H:%M")
    payload = f"[{stamp}] {text}"
    if dry_run:
        print(f"DRY RUN notification:\n{payload}")
        return

    with NOTIFY_OUTBOX.open("a", encoding="utf-8") as out:
        out.write(payload + "\n")
    print(f"Queued notification in {NOTIFY_OUTBOX}")


def cadence_due(state: dict, cadence: str) -> tuple[bool, int]:
    """Return (is_due, missed_intervals)."""
    now = now_dt()
    last_raw = state.get("last_run", {}).get(cadence)
    if not last_raw:
        return True, 0

    try:
        last = datetime.fromisoformat(last_raw)
    except Exception:
        return True, 0

    if cadence == "daily":
        delta_days = (now.date() - last.date()).days
        if delta_days <= 0:
            return False, 0
        return True, max(0, delta_days - 1)

    curr_y, curr_w, _ = now.isocalendar()
    last_y, last_w, _ = last.isocalendar()
    curr_index = curr_y * 53 + curr_w
    last_index = last_y * 53 + last_w
    gap = curr_index - last_index
    if gap <= 0:
        return False, 0
    return True, max(0, gap - 1)


def run_scheduler(scheduler: str, dry_run: bool = False) -> None:
    state = load_state()
    state["scheduler_source"] = scheduler

    daily_due, daily_missed = cadence_due(state, "daily")
    weekly_due, weekly_missed = cadence_due(state, "weekly")

    if daily_missed:
        state["missed_runs"]["daily"] = int(state["missed_runs"].get("daily", 0)) + daily_missed
    if weekly_missed:
        state["missed_runs"]["weekly"] = int(state["missed_runs"].get("weekly", 0)) + weekly_missed

    created: list[str] = []

    if daily_due:
        created.append(str(scaffold("daily")))
        state["last_run"]["daily"] = now_dt().isoformat(timespec="seconds")

    if weekly_due:
        created.append(str(scaffold("weekly")))
        state["last_run"]["weekly"] = now_dt().isoformat(timespec="seconds")

    save_state(state)

    if created:
        queue_notification(
            "Self-improve loop update: "
            + "; ".join([f"created {Path(c).name}" for c in created]),
            dry_run=dry_run,
        )
    else:
        queue_notification("Self-improve loop check: nothing due.", dry_run=dry_run)

    top_tweaks = sorted(
        state.get("policy_tweak_counts", {}).items(), key=lambda kv: kv[1], reverse=True
    )[:3]
    if top_tweaks:
        preview = ", ".join([f"{k} ({v}x)" for k, v in top_tweaks])
        print(f"Promotion candidates (top recurring tweaks): {preview}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Self-improvement loop automation helpers")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_fast = sub.add_parser("fast", help="Append a FAST_LOOP note")
    p_fast.add_argument("note", nargs="+", help="Note text")

    p_post = sub.add_parser("post-task", help="Append structured post-task log")
    p_post.add_argument("--context", required=True)
    p_post.add_argument("--decision", required=True)
    p_post.add_argument("--outcome", required=True)
    p_post.add_argument("--policy-tweak", required=True)

    sub.add_parser("daily", help="Create daily meso review scaffold")
    sub.add_parser("weekly", help="Create weekly slow distill scaffold")

    p_run = sub.add_parser("run", help="Run cadence checks + missed-run detection")
    p_run.add_argument(
        "--scheduler",
        choices=["heartbeat", "host-cron"],
        default="heartbeat",
        help="Source of periodic triggering",
    )
    p_run.add_argument("--dry-run", action="store_true", help="Preview notification text only")

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "fast":
        fast(" ".join(args.note).strip())
        return 0

    if args.cmd == "post-task":
        post_task(args.context, args.decision, args.outcome, args.policy_tweak)
        return 0

    if args.cmd == "daily":
        scaffold("daily")
        return 0

    if args.cmd == "weekly":
        scaffold("weekly")
        return 0

    if args.cmd == "run":
        run_scheduler(scheduler=args.scheduler, dry_run=args.dry_run)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
