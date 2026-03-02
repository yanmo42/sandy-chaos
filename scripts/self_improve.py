#!/usr/bin/env python3
"""Automation helpers for assistant self-improvement loops.

Examples:
  python3 scripts/self_improve.py fast "miss=too verbose; fix=shorter bullets"
  python3 scripts/self_improve.py post-task \
    --context "User asked for quick recap" \
    --decision "Used bullets + one recommendation" \
    --outcome "Accepted without follow-up" \
    --policy-tweak "Default to 4 bullets max for recaps"
  python3 scripts/self_improve.py full-pass --scheduler host-cron --send-telegram
  python3 scripts/self_improve.py todo-add --text "Implement digest sender" --section "Closed automation loop"
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
MEMORY_DIR = ROOT / "memory"
STATE_PATH = MEMORY_DIR / "self_improve_state.json"
NOTIFY_OUTBOX = MEMORY_DIR / "notification_outbox.md"
TODO_PATH = ROOT / "plans" / "todo.md"
CONFIG_PATH = ROOT / "config" / "automation.json"
ORCH_PLAN_PATH = ROOT / "memory" / "orchestrator_task_plan.jsonl"
ORCH_REQ_PATH = ROOT / "memory" / "orchestrator_spawn_requests.json"
ORCH_DISPATCH_LOG = ROOT / "memory" / "orchestrator_dispatch_log.jsonl"


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


def default_state() -> dict:
    return {
        "scheduler_source": "heartbeat",
        "last_run": {"daily": None, "weekly": None, "full_pass": None},
        "missed_runs": {"daily": 0, "weekly": 0},
        "policy_tweak_counts": {},
        "last_todo_snapshot": {"done": 0, "partial": 0, "open": 0, "total": 0},
        "sent": {"daily": None, "weekly": None},
    }


def load_state() -> dict:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_PATH.exists():
        return default_state()

    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        base = default_state()
        base.update(data)
        base["last_run"].update(data.get("last_run", {}))
        base["missed_runs"].update(data.get("missed_runs", {}))
        base["sent"].update(data.get("sent", {}))
        return base
    except Exception:
        return default_state()


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {
            "notifications": {
                "channel": "telegram",
                "target": "<REDACTED_CHAT_ID>",
                "prefixes": {
                    "daily": "[SANDY-DAILY]",
                    "weekly": "[SANDY-WEEKLY]",
                    "alert": "[SANDY-ALERT]",
                    "fullpass": "[SANDY-FULLPASS]",
                },
                "rateLimits": {"dailyMax": 1, "weeklyMax": 1},
                "botTokenEnv": "OPENCLAW_TELEGRAM_BOT_TOKEN",
            }
        }
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return load_config.__defaults__[0] if load_config.__defaults__ else {}


def fast(note: str) -> None:
    f = ensure_memory_file()
    with f.open("a", encoding="utf-8") as out:
        out.write(f"- FAST_LOOP: {note.strip()}\n")
    print(f"Appended fast-loop note to {f}")


def post_task(context: str, decision: str, outcome: str, policy_tweak: str) -> None:
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
        return dst

    shutil.copyfile(src, dst)
    return dst


def queue_notification(text: str, dry_run: bool) -> None:
    stamp = now_dt().strftime("%Y-%m-%d %H:%M")
    payload = f"[{stamp}] {text}"
    if dry_run:
        print(f"DRY RUN notification:\n{payload}")
        return

    with NOTIFY_OUTBOX.open("a", encoding="utf-8") as out:
        out.write(payload + "\n")


def cadence_due(state: dict, cadence: str) -> tuple[bool, int]:
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


def run_scheduler(scheduler: str, dry_run: bool = False) -> dict:
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
            + "; ".join([f"prepared {Path(c).name}" for c in created]),
            dry_run=dry_run,
        )

    return {
        "daily_due": daily_due,
        "weekly_due": weekly_due,
        "created": created,
        "daily_missed": daily_missed,
        "weekly_missed": weekly_missed,
    }


def parse_todo_counts(todo_text: str) -> dict:
    done = partial = open_ = 0
    for line in todo_text.splitlines():
        s = line.strip()
        if s.startswith("- [x]") or s.startswith("- [X]"):
            done += 1
        elif s.startswith("- [ ]"):
            open_ += 1
        elif s.startswith("- [🟡]"):
            partial += 1
        elif "|" in s and "✅" in s:
            done += 1
        elif "|" in s and "🟡" in s:
            partial += 1
        elif "|" in s and "⬜" in s:
            open_ += 1
    total = done + partial + open_
    pct = (done / total * 100.0) if total else 0.0
    return {"done": done, "partial": partial, "open": open_, "total": total, "pct": pct}


def list_open_checkbox_items(limit: int = 5) -> list[str]:
    if not TODO_PATH.exists():
        return []
    items: list[str] = []
    for line in TODO_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if s.startswith("- [ ]") or s.startswith("- [🟡]"):
            items.append(s)
        if len(items) >= limit:
            break
    return items


def git_status_short(limit: int = 12) -> list[str]:
    try:
        out = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True)
    except Exception:
        return []
    lines = [ln for ln in out.splitlines() if ln.strip()]
    return lines[:limit]


def todo_add(text: str, section: str | None = None) -> bool:
    if not TODO_PATH.exists():
        return False
    lines = TODO_PATH.read_text(encoding="utf-8").splitlines()

    insert_idx = len(lines)
    if section:
        header = f"## {section.strip()}"
        for i, ln in enumerate(lines):
            if ln.strip() == header:
                insert_idx = i + 1
                while insert_idx < len(lines) and lines[insert_idx].strip() == "":
                    insert_idx += 1
                break

    lines.insert(insert_idx, f"- [ ] {text.strip()}")
    TODO_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def todo_set(match: str, state_name: str) -> bool:
    if not TODO_PATH.exists():
        return False
    marker = {"done": "[x]", "open": "[ ]", "partial": "[🟡]"}.get(state_name)
    if not marker:
        return False

    lines = TODO_PATH.read_text(encoding="utf-8").splitlines()
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("- [") and match.lower() in s.lower():
            prefix_len = ln.find("[")
            end = ln.find("]", prefix_len)
            if prefix_len >= 0 and end > prefix_len:
                lines[i] = ln[:prefix_len] + marker + ln[end + 1 :]
                TODO_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
                return True
    return False


def todo_remove(match: str) -> bool:
    if not TODO_PATH.exists():
        return False
    lines = TODO_PATH.read_text(encoding="utf-8").splitlines()
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("- [") and match.lower() in s.lower():
            del lines[i]
            TODO_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return True
    return False


def send_telegram_message(text: str, dry_run: bool) -> None:
    cfg = load_config().get("notifications", {})
    target = str(cfg.get("target", "")).strip()
    token_env = cfg.get("botTokenEnv", "OPENCLAW_TELEGRAM_BOT_TOKEN")

    import os

    token = os.environ.get(token_env, "").strip()
    if not target:
        raise RuntimeError("Telegram target missing in config/automation.json")
    if not token:
        raise RuntimeError(
            f"Telegram bot token missing. Export {token_env}=<bot_token> for automation service."
        )

    if dry_run:
        print("DRY RUN telegram send:\n" + text)
        return

    payload = urllib.parse.urlencode({"chat_id": target, "text": text}).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage", data=payload, method="POST"
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        _ = resp.read()



def load_orchestrator_snapshot() -> dict:
    plan_count = 0
    req_count = 0
    dispatched = 0
    latest_runs: list[str] = []

    if ORCH_PLAN_PATH.exists():
        try:
            plan_count = len([ln for ln in ORCH_PLAN_PATH.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip()])
        except Exception:
            plan_count = 0

    if ORCH_REQ_PATH.exists():
        try:
            data = json.loads(ORCH_REQ_PATH.read_text(encoding="utf-8"))
            req_count = len(data.get("requests", []))
        except Exception:
            req_count = 0

    if ORCH_DISPATCH_LOG.exists():
        try:
            lines = [ln for ln in ORCH_DISPATCH_LOG.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip()]
            events = []
            for ln in lines[-80:]:
                try:
                    events.append(json.loads(ln))
                except Exception:
                    continue
            disp = [e for e in events if e.get("event") == "spawn_dispatched"]
            dispatched = len(disp)
            latest_runs = [str(e.get("runId", "")) for e in disp[-5:] if e.get("runId")]
        except Exception:
            pass

    return {
        "plan_count": plan_count,
        "request_count": req_count,
        "dispatched_count": dispatched,
        "latest_run_ids": latest_runs,
    }


def todo_delta(current: dict, previous: dict) -> dict:
    return {
        "done": int(current.get("done", 0)) - int(previous.get("done", 0)),
        "partial": int(current.get("partial", 0)) - int(previous.get("partial", 0)),
        "open": int(current.get("open", 0)) - int(previous.get("open", 0)),
    }

def compose_fullpass_message(summary: dict, todo: dict, open_items: list[str], git_lines: list[str], orch: dict, delta: dict) -> str:
    cfg = load_config().get("notifications", {})
    prefix = cfg.get("prefixes", {}).get("fullpass", "[SANDY-FULLPASS]")

    created = summary.get("created", [])
    created_text = ", ".join([Path(c).name for c in created]) if created else "none"

    git_text = "\n".join([f"- {g}" for g in git_lines]) if git_lines else "- (no unstaged changes)"
    open_text = "\n".join([f"- {it}" for it in open_items]) if open_items else "- (no open checkbox items found)"
    run_text = ", ".join(orch.get("latest_run_ids", [])) if orch.get("latest_run_ids") else "none"

    return (
        f"{prefix} automation cycle complete.\n\n"
        f"Execution workflow status:\n"
        f"- orchestrator tasks planned: {orch.get('plan_count', 0)}\n"
        f"- spawn requests prepared: {orch.get('request_count', 0)}\n"
        f"- recent dispatch events logged: {orch.get('dispatched_count', 0)}\n"
        f"- recent run ids: {run_text}\n"
        f"- pipeline orchestrator/autospawn: {orch.get('pipeline',{}).get('orchestrator_ok', False)}/{orch.get('pipeline',{}).get('autospawn_ok', False)}\n"
        f"- dispatch attempted/sent: {orch.get('dispatch',{}).get('attempted', 0)}/{orch.get('dispatch',{}).get('dispatched', 0)}\n\n"
        f"Cadence artifacts prepared: {created_text}.\n"
        f"Missed intervals detected: daily={summary.get('daily_missed', 0)}, weekly={summary.get('weekly_missed', 0)}.\n\n"
        f"Project progress snapshot:\n"
        f"- done={todo['done']} (Δ {delta['done']:+d})\n"
        f"- partial={todo['partial']} (Δ {delta['partial']:+d})\n"
        f"- open={todo['open']} (Δ {delta['open']:+d})\n"
        f"- total={todo['total']}\n"
        f"- completion={todo['pct']:.1f}%\n\n"
        f"Current repo changes:\n{git_text}\n\n"
        f"Top open/partial TODO items:\n{open_text}\n\n"
        f"Narrative summary: Sandy ran planning + execution bookkeeping, refreshed queue visibility, and produced dispatch-aware telemetry for the next autonomous cycle."
    )


def run_orchestrator_pipeline(limit: int, dry_run: bool) -> dict:
    """Run orchestrator + autospawn preparation pipeline."""
    results = {"orchestrator_ok": False, "autospawn_ok": False, "errors": []}

    cmds = [
        ["python3", "scripts/automation_orchestrator.py"],
        ["python3", "scripts/orchestrator_autospawn.py", "--limit", str(limit)],
    ]

    for i, cmd in enumerate(cmds):
        if dry_run:
            print("DRY RUN pipeline cmd:", " ".join(cmd))
            if i == 0:
                results["orchestrator_ok"] = True
            else:
                results["autospawn_ok"] = True
            continue
        try:
            subprocess.check_call(cmd, cwd=ROOT)
            if i == 0:
                results["orchestrator_ok"] = True
            else:
                results["autospawn_ok"] = True
        except Exception as exc:
            results["errors"].append(str(exc))

    return results


def dispatch_spawn_requests(dry_run: bool, max_dispatch: int = 3) -> dict:
    """Dispatch spawn requests by asking the active OpenClaw session to run them.

    This uses `openclaw agent` to feed the request contracts back into the main
    agent session, where tool-level `sessions_spawn` can execute.
    """
    out = {"dispatched": 0, "errors": [], "attempted": 0}
    if not ORCH_REQ_PATH.exists():
        return out

    try:
        req = json.loads(ORCH_REQ_PATH.read_text(encoding="utf-8"))
        requests = req.get("requests", [])[: max_dispatch]
    except Exception as exc:
        out["errors"].append(f"load requests failed: {exc}")
        return out

    for r in requests:
        spawn = r.get("spawn", {})
        msg = (
            "Dispatch this spawn contract now using sessions_spawn with exact JSON params: "
            + json.dumps(spawn, ensure_ascii=False)
        )
        out["attempted"] += 1

        if dry_run:
            print("DRY RUN dispatch via openclaw agent for", r.get("id", "(unknown)"))
            out["dispatched"] += 1
            continue

        try:
            subprocess.check_call(
                ["openclaw", "agent", "--session-id", "agent:main:main", "--message", msg],
                cwd=ROOT,
            )
            out["dispatched"] += 1
        except Exception as exc:
            out["errors"].append(f"{r.get('id','unknown')}: {exc}")

    return out


def full_pass(scheduler: str, send_telegram: bool, dry_run: bool, max_open_items: int, with_orchestration: bool = False, with_dispatch: bool = False, dispatch_limit: int = 3) -> None:
    summary = run_scheduler(scheduler=scheduler, dry_run=dry_run)

    orchestration = {"orchestrator_ok": False, "autospawn_ok": False, "errors": []}
    dispatch = {"dispatched": 0, "errors": [], "attempted": 0}
    if with_orchestration:
        orchestration = run_orchestrator_pipeline(limit=dispatch_limit, dry_run=dry_run)
    if with_dispatch:
        dispatch = dispatch_spawn_requests(dry_run=dry_run, max_dispatch=dispatch_limit)

    todo_text = TODO_PATH.read_text(encoding="utf-8", errors="ignore") if TODO_PATH.exists() else ""
    todo = parse_todo_counts(todo_text)
    open_items = list_open_checkbox_items(limit=max_open_items)
    git_lines = git_status_short(limit=12)
    orch = load_orchestrator_snapshot()
    orch["pipeline"] = orchestration
    orch["dispatch"] = dispatch

    state = load_state()
    prev_todo = state.get("last_todo_snapshot", {})
    delta = todo_delta(todo, prev_todo)
    state["last_run"]["full_pass"] = now_dt().isoformat(timespec="seconds")
    state["last_todo_snapshot"] = todo
    save_state(state)

    message = compose_fullpass_message(summary, todo, open_items, git_lines, orch, delta)

    queue_notification(message, dry_run=dry_run)
    if send_telegram:
        try:
            send_telegram_message(message, dry_run=dry_run)
        except Exception as exc:
            warn = f"[SANDY-ALERT] Telegram send skipped: {exc}"
            queue_notification(warn, dry_run=dry_run)
            print(warn)

    print("Full pass complete.")


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
    p_run.add_argument("--scheduler", choices=["heartbeat", "host-cron"], default="heartbeat")
    p_run.add_argument("--dry-run", action="store_true", help="Preview notification text only")

    p_full = sub.add_parser("full-pass", help="Run full cycle and build rich digest")
    p_full.add_argument("--scheduler", choices=["heartbeat", "host-cron"], default="host-cron")
    p_full.add_argument("--send-telegram", action="store_true", help="Send full digest to Telegram")
    p_full.add_argument("--dry-run", action="store_true", help="Preview output only")
    p_full.add_argument("--max-open-items", type=int, default=5)
    p_full.add_argument("--with-orchestration", action="store_true", help="Run orchestrator + autospawn before digest")
    p_full.add_argument("--with-dispatch", action="store_true", help="Dispatch spawn requests via openclaw agent bridge")
    p_full.add_argument("--dispatch-limit", type=int, default=3, help="Max requests to prepare/dispatch")

    p_add = sub.add_parser("todo-add", help="Add a checkbox item to plans/todo.md")
    p_add.add_argument("--text", required=True)
    p_add.add_argument("--section", required=False)

    p_set = sub.add_parser("todo-set", help="Mark first matching todo checkbox")
    p_set.add_argument("--match", required=True)
    p_set.add_argument("--state", choices=["done", "open", "partial"], required=True)

    p_remove = sub.add_parser("todo-remove", help="Remove first matching todo checkbox")
    p_remove.add_argument("--match", required=True)

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
        p = scaffold("daily")
        print(p)
        return 0

    if args.cmd == "weekly":
        p = scaffold("weekly")
        print(p)
        return 0

    if args.cmd == "run":
        run_scheduler(scheduler=args.scheduler, dry_run=args.dry_run)
        print("Cadence check complete.")
        return 0

    if args.cmd == "full-pass":
        full_pass(
            scheduler=args.scheduler,
            send_telegram=args.send_telegram,
            dry_run=args.dry_run,
            max_open_items=args.max_open_items,
            with_orchestration=args.with_orchestration,
            with_dispatch=args.with_dispatch,
            dispatch_limit=args.dispatch_limit,
        )
        return 0

    if args.cmd == "todo-add":
        ok = todo_add(text=args.text, section=args.section)
        print("Added." if ok else "Failed.")
        return 0 if ok else 1

    if args.cmd == "todo-set":
        ok = todo_set(match=args.match, state_name=args.state)
        print("Updated." if ok else "No matching checkbox found.")
        return 0 if ok else 1

    if args.cmd == "todo-remove":
        ok = todo_remove(match=args.match)
        print("Removed." if ok else "No matching checkbox found.")
        return 0 if ok else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
