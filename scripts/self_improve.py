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
import csv
import json
import os
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
MEMORY_DIR = ROOT / "memory"
STATE_PATH = MEMORY_DIR / "self_improve_state.json"
NOTIFY_OUTBOX = MEMORY_DIR / "notification_outbox.md"
TODO_PATH = ROOT / "plans" / "todo.md"
CONFIG_PATH = ROOT / "config" / "automation.json"
ORCHESTRATOR_CONFIG_PATH = ROOT / "config" / "orchestrator.json"
AGENTS_PATH = ROOT / "AGENTS.md"
WORKFLOW_PATH = ROOT / "WORKFLOW.md"
ORCH_PLAN_PATH = ROOT / "memory" / "orchestrator_task_plan.jsonl"
ORCH_REQ_PATH = ROOT / "memory" / "orchestrator_spawn_requests.json"
ORCH_DISPATCH_LOG = ROOT / "memory" / "orchestrator_dispatch_log.jsonl"
ORCH_CYCLE_LOG = ROOT / "memory" / "orchestrator_cycle_events.jsonl"
DAILY_DIGEST_TEMPLATE = TEMPLATES / "daily_digest_notification.md"
WEEKLY_DIGEST_TEMPLATE = TEMPLATES / "weekly_digest_notification.md"
RESEARCH_DIR = MEMORY_DIR / "research"
DEFAULT_VALIDATION_COMMAND = "./venv/bin/python -m unittest discover -s tests -q"
DEFAULT_VALIDATION_POLICY = {
    "requireAtLeastOneCommand": True,
    "requireAllPass": True,
    "failOnZeroTests": True,
    "disallowCommandSubstrings": ["|| true"],
}
DEFAULT_PROMPT_TEMPLATE = (
    "You are executing one Sandy-Chaos automation contract.\n"
    "Lane: {lane}\n"
    "Section: {section}\n"
    "Goal: {goal}\n\n"
    "Global constraints:\n{global_constraints}\n\n"
    "Lane-specific instructions:\n{lane_instructions}\n\n"
    "Task constraints:\n{constraints}\n\n"
    "Definition of done:\n{definition_of_done}\n\n"
    "Output contract:\n{output_contract}\n\n"
    "Forbidden patterns:\n{forbidden}\n\n"
    "Validation command: {validation_command}\n"
    "Work in {workspace}. Make scoped changes and commit when done."
)
DEFAULT_PROMPTING = {
    "template": DEFAULT_PROMPT_TEMPLATE,
    "globalConstraints": [
        "Use openai-codex/gpt-5.3-codex.",
        "Keep strict causality; no retrocausal claims.",
    ],
    "byLane": {},
    "outputContract": [
        "List files changed.",
        "Report validation command + outcome.",
        "Give one concise completion note.",
    ],
    "forbidden": [
        "Do not bypass validation (no '|| true').",
        "Do not make unrelated broad refactors.",
    ],
}


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
        "promoted_policy_tweaks": {},
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
        base["promoted_policy_tweaks"].update(data.get("promoted_policy_tweaks", {}))
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
                "target": os.environ.get("OPENCLAW_TELEGRAM_TARGET", "<REDACTED_CHAT_ID>"),
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


def load_orchestrator_config() -> dict:
    if not ORCHESTRATOR_CONFIG_PATH.exists():
        return {}
    try:
        data = json.loads(ORCHESTRATOR_CONFIG_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _as_lines(raw: object) -> list[str]:
    if isinstance(raw, str):
        return [raw.strip()] if raw.strip() else []
    if isinstance(raw, list):
        out: list[str] = []
        for item in raw:
            text = str(item).strip()
            if text:
                out.append(text)
        return out
    return []


def _render_bullets(lines: list[str]) -> str:
    if not lines:
        return "- (none)"
    return "\n".join(f"- {line}" for line in lines)


def _normalize_prompting(raw: dict | None) -> dict:
    merged = dict(DEFAULT_PROMPTING)
    if isinstance(raw, dict):
        tmpl = raw.get("template")
        if isinstance(tmpl, str) and tmpl.strip():
            merged["template"] = tmpl
        for key in ["globalConstraints", "outputContract", "forbidden"]:
            merged[key] = _as_lines(raw.get(key, merged.get(key))) or _as_lines(merged.get(key))

        by_lane_raw = raw.get("byLane")
        by_lane: dict[str, list[str]] = {}
        if isinstance(by_lane_raw, dict):
            for lane, lane_value in by_lane_raw.items():
                lane_key = str(lane).strip()
                if not lane_key:
                    continue
                if isinstance(lane_value, dict):
                    lane_lines = _as_lines(lane_value.get("instructions"))
                else:
                    lane_lines = _as_lines(lane_value)
                by_lane[lane_key] = lane_lines
        merged["byLane"] = by_lane
    return merged


def resolve_prompting_runtime() -> dict:
    cfg = load_orchestrator_config()
    raw = cfg.get("prompting", {}) if isinstance(cfg, dict) else {}
    return _normalize_prompting(raw if isinstance(raw, dict) else None)


def render_contract_prompt(contract: dict, prompting: dict | None = None) -> str:
    cfg = _normalize_prompting(prompting)
    lane = str(contract.get("lane", "sandy-builder")).strip() or "sandy-builder"
    section = str(contract.get("section", "(unknown section)")).strip() or "(unknown section)"
    goal = str(contract.get("goal", "(missing goal)")).strip() or "(missing goal)"
    constraints = _as_lines(contract.get("constraints"))
    dod = _as_lines(contract.get("definition_of_done"))
    validation_command = str(contract.get("validation_command", DEFAULT_VALIDATION_COMMAND)).strip() or DEFAULT_VALIDATION_COMMAND

    by_lane = cfg.get("byLane", {}) if isinstance(cfg, dict) else {}
    lane_specific = _as_lines(by_lane.get(lane))

    fields = {
        "lane": lane,
        "section": section,
        "goal": goal,
        "global_constraints": _render_bullets(_as_lines(cfg.get("globalConstraints"))),
        "lane_instructions": _render_bullets(lane_specific),
        "constraints": _render_bullets(constraints),
        "definition_of_done": _render_bullets(dod),
        "output_contract": _render_bullets(_as_lines(cfg.get("outputContract"))),
        "forbidden": _render_bullets(_as_lines(cfg.get("forbidden"))),
        "validation_command": validation_command,
        "workspace": str(ROOT),
    }

    try:
        return str(cfg.get("template", DEFAULT_PROMPT_TEMPLATE)).format(**fields).strip()
    except Exception:
        return DEFAULT_PROMPT_TEMPLATE.format(**fields).strip()


def _normalize_validation_policy(raw: dict | None) -> dict:
    merged = dict(DEFAULT_VALIDATION_POLICY)
    if isinstance(raw, dict):
        for k in ["requireAtLeastOneCommand", "requireAllPass", "failOnZeroTests"]:
            if k in raw:
                merged[k] = bool(raw.get(k))
        disallow = raw.get("disallowCommandSubstrings")
        if isinstance(disallow, list):
            merged["disallowCommandSubstrings"] = [str(x).strip() for x in disallow if str(x).strip()]
    return merged


def resolve_validation_runtime(validation_commands_override: list[str] | None = None) -> dict:
    cfg = load_orchestrator_config()
    validation = cfg.get("validation", {}) if isinstance(cfg, dict) else {}
    commands_cfg = validation.get("commands", {}) if isinstance(validation, dict) else {}

    default_commands = commands_cfg.get("default") if isinstance(commands_cfg, dict) else None
    if isinstance(default_commands, list):
        default_commands_list = [str(c).strip() for c in default_commands if str(c).strip()]
    elif isinstance(default_commands, str) and default_commands.strip():
        default_commands_list = [default_commands.strip()]
    else:
        default_commands_list = [DEFAULT_VALIDATION_COMMAND]

    if validation_commands_override:
        commands = [str(c).strip() for c in validation_commands_override if str(c).strip()]
    else:
        commands = default_commands_list

    policy = _normalize_validation_policy(validation.get("policy") if isinstance(validation, dict) else None)
    return {
        "commands": commands,
        "policy": policy,
    }


def evaluate_validation_gate(outcomes: list[dict], policy: dict) -> bool:
    require_at_least_one = bool(policy.get("requireAtLeastOneCommand", True))
    require_all_pass = bool(policy.get("requireAllPass", True))

    if require_at_least_one and not outcomes:
        return False
    if not outcomes:
        return True
    if require_all_pass:
        return all(bool(row.get("ok", False)) for row in outcomes)
    return any(bool(row.get("ok", False)) for row in outcomes)


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
    promoted = promote_policy_tweaks(min_count=3, dry_run=False)
    promoted_count = len(promoted.get("promoted", []))
    if promoted_count:
        print(f"Appended post-task schema entry to {f} and promoted {promoted_count} tweak(s)")
    else:
        print(f"Appended post-task schema entry to {f}")


def classify_policy_tweak_target(policy_tweak: str) -> Path:
    workflow_keywords = {
        "workflow",
        "process",
        "checklist",
        "validate",
        "validation",
        "test",
        "tests",
        "commit",
        "git",
        "runbook",
        "cadence",
        "schedule",
        "orchestr",
        "dispatch",
        "automation",
    }
    text = policy_tweak.lower()
    if any(k in text for k in workflow_keywords):
        return WORKFLOW_PATH
    return AGENTS_PATH


def append_promoted_tweak(target_path: Path, policy_tweak: str) -> bool:
    heading = "## Promoted Policy Tweaks"
    bullet = f"- {policy_tweak.strip()}"
    if not target_path.exists():
        target_path.write_text(f"{heading}\n\n{bullet}\n", encoding="utf-8")
        return True

    text = target_path.read_text(encoding="utf-8")
    if bullet in text:
        return False

    if heading in text:
        lines = text.splitlines()
        idx = next(i for i, line in enumerate(lines) if line.strip() == heading)
        insert_at = idx + 1
        while insert_at < len(lines) and lines[insert_at].strip() == "":
            insert_at += 1
        lines.insert(insert_at, bullet)
        target_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        return True

    with target_path.open("a", encoding="utf-8") as out:
        if text and not text.endswith("\n"):
            out.write("\n")
        out.write(f"\n{heading}\n\n{bullet}\n")
    return True


def promote_policy_tweaks(min_count: int = 3, dry_run: bool = False) -> dict:
    state = load_state()
    tweaks = state.get("policy_tweak_counts", {})
    promoted = state.setdefault("promoted_policy_tweaks", {})
    promoted_now: list[dict] = []

    for tweak, count in tweaks.items():
        if int(count) < min_count:
            continue
        if tweak in promoted:
            continue

        target_path = classify_policy_tweak_target(tweak)
        changed = True
        if not dry_run:
            changed = append_promoted_tweak(target_path, tweak)

        promoted[tweak] = {
            "target": target_path.name,
            "promoted_at": now_dt().isoformat(timespec="seconds"),
            "count": int(count),
            "applied": bool(changed),
        }
        promoted_now.append({"policy_tweak": tweak, "target": target_path.name, "applied": bool(changed)})

    if promoted_now and not dry_run:
        save_state(state)

    return {
        "promoted": promoted_now,
        "min_count": min_count,
        "dry_run": dry_run,
    }


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




def append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def ensure_notification_outbox() -> None:
    NOTIFY_OUTBOX.parent.mkdir(parents=True, exist_ok=True)
    if NOTIFY_OUTBOX.exists():
        return

    NOTIFY_OUTBOX.write_text(
        "# Notification Outbox\n\n"
        "Append-only digest queue generated by `scripts/self_improve.py`.\n"
        "Each entry is timestamped and grouped by day.\n\n",
        encoding="utf-8",
    )


def queue_notification(text: str, dry_run: bool) -> None:
    now = now_dt()
    day_key = now.strftime("%Y-%m-%d")
    stamp = now.strftime("%Y-%m-%d %H:%M")
    payload = text.strip()

    block = (
        f"### [{stamp}]\n"
        f"{payload}\n\n"
        "---\n\n"
    )

    if dry_run:
        print(f"DRY RUN notification:\n## {day_key}\n\n{block}")
        return

    ensure_notification_outbox()
    existing = NOTIFY_OUTBOX.read_text(encoding="utf-8")
    day_header = f"## {day_key}\n\n"
    with NOTIFY_OUTBOX.open("a", encoding="utf-8") as out:
        if day_header not in existing:
            out.write(day_header)
        out.write(block)


def render_digest_template(template_path: Path, replacements: dict[str, str]) -> str:
    template = template_path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        template = template.replace(f"{{{{{key}}}}}", value)
    return template.strip()


def build_cadence_notification(created: list[str]) -> str:
    sections: list[str] = []
    created_names = [Path(p).name for p in created]

    daily_file = next((n for n in created_names if n.endswith("-meso-review.md")), "none")
    weekly_file = next((n for n in created_names if n.endswith("-slow-distill.md")), "none")

    if daily_file != "none":
        sections.append(
            render_digest_template(
                DAILY_DIGEST_TEMPLATE,
                {
                    "date": today_str(),
                    "artifact": daily_file,
                },
            )
        )

    if weekly_file != "none":
        year, week, _ = now_dt().isocalendar()
        sections.append(
            render_digest_template(
                WEEKLY_DIGEST_TEMPLATE,
                {
                    "week_label": f"{year}-W{week:02d}",
                    "artifact": weekly_file,
                },
            )
        )

    if not sections:
        return "Self-improve cadence check: no daily or weekly artifacts were due."

    return "\n\n".join(sections)


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
        queue_notification(build_cadence_notification(created), dry_run=dry_run)

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


def lane_for_path(path: str) -> str:
    p = path.strip()
    if p.startswith("docs/"):
        return "theory"
    if p.startswith("nfem_suite/"):
        return "simulation"
    if p.startswith("tests/"):
        return "validation"
    if p.startswith("scripts/") or p.startswith("ops/") or p.startswith("config/") or p.startswith("plans/"):
        return "ops"
    return "other"


def lanes_from_git_status(lines: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for ln in lines:
        raw = ln.strip()
        if not raw:
            continue
        path = raw[3:].strip() if len(raw) > 3 else raw
        if " -> " in path:
            path = path.split(" -> ")[-1].strip()
        lane = lane_for_path(path)
        out[lane] = int(out.get(lane, 0)) + 1
    return out


def productivity_gate(delta: dict, lane_hits: dict[str, int], orch: dict) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if delta.get("done", 0) > 0 or delta.get("open", 0) < 0:
        reasons.append("TODO state advanced")
    if lane_hits.get("validation", 0) > 0:
        reasons.append("validation lane touched")
    if lane_hits.get("theory", 0) > 0:
        reasons.append("theory/docs lane touched")
    pipeline = orch.get("pipeline", {})
    dispatch = orch.get("dispatch", {})
    if pipeline.get("orchestrator_ok") and pipeline.get("autospawn_ok"):
        reasons.append("orchestrator pipeline healthy")
    if dispatch.get("attempted", 0) > 0 and dispatch.get("errors") == []:
        reasons.append("dispatch completed without errors")
    return (len(reasons) > 0, reasons)


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


def _message_cadence_kind(text: str, cfg: dict) -> str | None:
    prefixes = (cfg.get("prefixes", {}) or {}) if isinstance(cfg, dict) else {}
    daily_prefix = str(prefixes.get("daily", "[SANDY-DAILY]")).strip()
    weekly_prefix = str(prefixes.get("weekly", "[SANDY-WEEKLY]")).strip()
    stripped = text.strip()
    if daily_prefix and stripped.startswith(daily_prefix):
        return "daily"
    if weekly_prefix and stripped.startswith(weekly_prefix):
        return "weekly"
    return None


def _is_quiet_hours_now(now: datetime, quiet_cfg: dict) -> bool:
    if not isinstance(quiet_cfg, dict):
        return False

    start_raw = str(quiet_cfg.get("start", "")).strip()
    end_raw = str(quiet_cfg.get("end", "")).strip()
    if not start_raw or not end_raw:
        return False

    try:
        start = datetime.strptime(start_raw, "%H:%M").time()
        end = datetime.strptime(end_raw, "%H:%M").time()
    except Exception:
        return False

    t = now.time()
    if start < end:
        return start <= t < end
    if start > end:
        return t >= start or t < end
    return True


def _get_rate_limit_max(kind: str, cfg: dict) -> int:
    rate = (cfg.get("rateLimits", {}) or {}) if isinstance(cfg, dict) else {}
    if kind == "daily":
        return int(rate.get("dailyMax", 1) or 0)
    if kind == "weekly":
        return int(rate.get("weeklyMax", 1) or 0)
    return 0


def _rate_limit_key(kind: str, now: datetime) -> str:
    if kind == "daily":
        return now.strftime("%Y-%m-%d")
    y, w, _ = now.isocalendar()
    return f"{y}-W{w:02d}"


def _can_send_now(text: str, state: dict, cfg: dict, now: datetime) -> tuple[bool, str | None, str | None]:
    if _is_quiet_hours_now(now, cfg.get("quietHours", {})):
        qh = cfg.get("quietHours", {}) or {}
        return False, f"Within quiet hours ({qh.get('start', '?')}–{qh.get('end', '?')}); send suppressed.", None

    kind = _message_cadence_kind(text, cfg)
    if kind not in {"daily", "weekly"}:
        return True, None, None

    max_allowed = _get_rate_limit_max(kind, cfg)
    if max_allowed <= 0:
        return False, f"Rate limit blocks all {kind} sends (max={max_allowed}).", kind

    sent = state.setdefault("sent", {})
    entry = sent.get(kind)
    if not isinstance(entry, dict):
        entry = {}
        sent[kind] = entry

    key = _rate_limit_key(kind, now)
    if entry.get("window") != key:
        return True, None, kind

    count = int(entry.get("count", 0) or 0)
    if count >= max_allowed:
        return False, f"{kind} send suppressed by rate limit ({count}/{max_allowed} in {key}).", kind
    return True, None, kind


def _record_send(state: dict, kind: str | None, now: datetime) -> None:
    if kind not in {"daily", "weekly"}:
        return
    sent = state.setdefault("sent", {})
    entry = sent.get(kind)
    if not isinstance(entry, dict):
        entry = {}
        sent[kind] = entry
    key = _rate_limit_key(kind, now)
    if entry.get("window") != key:
        entry["window"] = key
        entry["count"] = 0
    entry["count"] = int(entry.get("count", 0) or 0) + 1
    entry["last_at"] = now.isoformat(timespec="seconds")


def send_telegram_message(text: str, dry_run: bool) -> None:
    cfg = load_config().get("notifications", {})
    state = load_state()
    now = now_dt()

    allowed, reason, kind = _can_send_now(text=text, state=state, cfg=cfg, now=now)
    if not allowed:
        raise RuntimeError(reason or "Telegram send suppressed by runtime policy")

    target = str(cfg.get("target", "")).strip()
    token_env = cfg.get("botTokenEnv", "OPENCLAW_TELEGRAM_BOT_TOKEN")

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

    _record_send(state=state, kind=kind, now=now)
    save_state(state)



def load_orchestrator_snapshot() -> dict:
    plan_count = 0
    req_count = 0
    dispatched = 0
    latest_runs: list[str] = []
    capability_lanes: dict[str, int] = {}

    if ORCH_PLAN_PATH.exists():
        try:
            rows = [ln for ln in ORCH_PLAN_PATH.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip()]
            plan_count = len(rows)
            for ln in rows:
                try:
                    row = json.loads(ln)
                except Exception:
                    continue
                cap = str(row.get("capability_lane", "unspecified")).strip() or "unspecified"
                capability_lanes[cap] = int(capability_lanes.get(cap, 0)) + 1
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
        "capability_lanes": capability_lanes,
    }


def todo_delta(current: dict, previous: dict) -> dict:
    return {
        "done": int(current.get("done", 0)) - int(previous.get("done", 0)),
        "partial": int(current.get("partial", 0)) - int(previous.get("partial", 0)),
        "open": int(current.get("open", 0)) - int(previous.get("open", 0)),
    }

def format_validation_outcomes(outcomes: list[dict]) -> str:
    if not outcomes:
        return "- (no validation commands run)"

    lines: list[str] = []
    for row in outcomes:
        cmd = str(row.get("command", "")).strip() or "(unknown command)"
        ok = bool(row.get("ok", False))
        code = row.get("returncode")
        verdict = "PASS" if ok else "FAIL"
        suffix = ""
        if row.get("zero_tests"):
            suffix = " (0 tests discovered)"
        if row.get("policy_violation"):
            suffix = f" (policy violation: {row.get('policy_violation')})"
        if isinstance(code, int):
            lines.append(f"- {verdict} (exit {code}){suffix}: `{cmd}`")
        else:
            lines.append(f"- {verdict}{suffix}: `{cmd}`")
    return "\n".join(lines)


def _extract_unittest_ran_count(output_text: str) -> int | None:
    m = re.search(r"Ran\s+(\d+)\s+tests?", output_text)
    if not m:
        return None
    try:
        return int(m.group(1))
    except Exception:
        return None


def run_validation_commands(commands: list[str], dry_run: bool, policy: dict | None = None) -> list[dict]:
    policy = _normalize_validation_policy(policy)
    disallow = [str(x).strip() for x in policy.get("disallowCommandSubstrings", []) if str(x).strip()]
    fail_on_zero_tests = bool(policy.get("failOnZeroTests", True))

    outcomes: list[dict] = []
    for command in commands:
        cmd = str(command).strip()
        if not cmd:
            continue

        blocked = next((needle for needle in disallow if needle in cmd), None)
        if blocked:
            outcomes.append(
                {
                    "command": cmd,
                    "ok": False,
                    "returncode": None,
                    "policy_violation": f"command contains disallowed substring: {blocked}",
                }
            )
            continue

        if dry_run:
            outcomes.append({"command": cmd, "ok": True, "returncode": 0, "dry_run": True, "ran_tests": None})
            continue

        proc = subprocess.run(cmd, cwd=ROOT, shell=True, capture_output=True, text=True)
        combined = f"{proc.stdout or ''}\n{proc.stderr or ''}"
        ran_tests = _extract_unittest_ran_count(combined)
        zero_tests = bool(fail_on_zero_tests and ran_tests == 0)
        ok = proc.returncode == 0 and not zero_tests

        outcomes.append(
            {
                "command": cmd,
                "ok": ok,
                "returncode": proc.returncode,
                "ran_tests": ran_tests,
                "zero_tests": zero_tests,
                "stdout": (proc.stdout or "").strip()[:2000],
                "stderr": (proc.stderr or "").strip()[:2000],
            }
        )
    return outcomes


def _find_active_research_cycle(now: datetime, active_window_hours: int = 24) -> dict | None:
    if not RESEARCH_DIR.exists():
        return None

    date_prefix = now.strftime("%Y-%m-%d")
    candidates = sorted(RESEARCH_DIR.glob(f"{date_prefix}*-synthesis.md"))
    if not candidates:
        return None

    threshold = now - timedelta(hours=active_window_hours)
    for synthesis in reversed(candidates):
        base = synthesis.name[: -len("-synthesis.md")]
        bundle = {
            "query": RESEARCH_DIR / f"{base}-query.md",
            "evidence": RESEARCH_DIR / f"{base}-evidence.csv",
            "synthesis": synthesis,
            "falsification": RESEARCH_DIR / f"{base}-falsification.md",
        }
        if not all(p.exists() for p in bundle.values()):
            continue
        latest_mtime = max(datetime.fromtimestamp(p.stat().st_mtime) for p in bundle.values())
        if latest_mtime >= threshold:
            return {"base": base, "files": bundle, "latest_mtime": latest_mtime}

    return None


def maybe_write_research_cycle_summary(dry_run: bool, now: datetime | None = None) -> dict:
    now = now or now_dt()
    cycle = _find_active_research_cycle(now)
    if not cycle:
        return {"active": False, "generated": False, "path": None, "reason": "no active research cycle"}

    files = cycle["files"]
    evidence_rows = 0
    source_ids: set[str] = set()
    claims_count = 0

    try:
        with files["evidence"].open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                evidence_rows += 1
                sid = str((row or {}).get("source_id", "")).strip()
                if sid:
                    source_ids.add(sid)
    except Exception:
        evidence_rows = 0
        source_ids = set()

    try:
        in_claims = False
        for raw in files["synthesis"].read_text(encoding="utf-8", errors="ignore").splitlines():
            s = raw.strip()
            if s.startswith("## "):
                in_claims = s.lower().startswith("## claims")
                continue
            if in_claims and s.startswith("- "):
                claims_count += 1
    except Exception:
        claims_count = 0

    summary_path = RESEARCH_DIR / f"{cycle['base']}-cycle-summary.md"
    source_count = len(source_ids)
    lines = [
        f"# Research Cycle Summary ({cycle['base']})",
        "",
        f"Generated: {now.strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Activity status",
        "- active: yes (artifact updates within last 24h)",
        "",
        "## Evidence + claims snapshot",
        f"- evidence rows: {evidence_rows}",
        f"- unique source_ids: {source_count}",
        f"- synthesis claims bullets: {claims_count}",
        "",
        "## Artifact set",
        f"- query: `{files['query'].relative_to(ROOT)}`",
        f"- evidence: `{files['evidence'].relative_to(ROOT)}`",
        f"- synthesis: `{files['synthesis'].relative_to(ROOT)}`",
        f"- falsification: `{files['falsification'].relative_to(ROOT)}`",
        "",
        "## Causality guardrail",
        "- This summary is descriptive only and makes no retrocausal claim.",
        "",
    ]

    write_needed = True
    if summary_path.exists():
        summary_mtime = datetime.fromtimestamp(summary_path.stat().st_mtime)
        write_needed = summary_mtime < cycle["latest_mtime"]

    if dry_run:
        return {
            "active": True,
            "generated": write_needed,
            "path": str(summary_path),
            "reason": "dry-run",
            "claims": claims_count,
            "evidence_rows": evidence_rows,
            "source_ids": source_count,
        }

    if write_needed:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "active": True,
        "generated": write_needed,
        "path": str(summary_path),
        "reason": "updated" if write_needed else "up-to-date",
        "claims": claims_count,
        "evidence_rows": evidence_rows,
        "source_ids": source_count,
    }


def compose_fullpass_message(
    summary: dict,
    todo: dict,
    open_items: list[str],
    git_lines: list[str],
    orch: dict,
    delta: dict,
    lane_hits: dict[str, int],
    productive: bool,
    productivity_reasons: list[str],
    validation_outcomes: list[dict],
    research_summary: dict,
) -> str:
    cfg = load_config().get("notifications", {})
    prefix = cfg.get("prefixes", {}).get("fullpass", "[SANDY-FULLPASS]")

    created = summary.get("created", [])
    created_text = ", ".join([Path(c).name for c in created]) if created else "none"

    git_text = "\n".join([f"- {g}" for g in git_lines]) if git_lines else "- (no unstaged changes)"
    open_text = "\n".join([f"- {it}" for it in open_items]) if open_items else "- (no open checkbox items found)"
    run_text = ", ".join(orch.get("latest_run_ids", [])) if orch.get("latest_run_ids") else "none"
    plan_lanes = orch.get("capability_lanes", {}) or {}
    plan_lane_text = ", ".join([f"{k}={v}" for k, v in sorted(plan_lanes.items())]) if plan_lanes else "none"
    touch_lane_text = ", ".join([f"{k}={v}" for k, v in sorted(lane_hits.items())]) if lane_hits else "none"
    verdict = "productive" if productive else "maintenance/no-op"
    reason_text = "; ".join(productivity_reasons) if productivity_reasons else "no gate condition met"
    validation_text = format_validation_outcomes(validation_outcomes)
    research_path = research_summary.get("path") if isinstance(research_summary, dict) else None
    research_text = "inactive"
    if isinstance(research_summary, dict) and research_summary.get("active"):
        if research_path:
            p = Path(str(research_path))
            if p.is_absolute():
                try:
                    p = p.relative_to(ROOT)
                except Exception:
                    pass
            state = "updated" if research_summary.get("generated") else "up-to-date"
            research_text = f"{state}: `{p}`"
        else:
            research_text = "active (no summary path)"

    return (
        f"{prefix} automation cycle complete.\n\n"
        f"Execution workflow status:\n"
        f"- orchestrator tasks planned: {orch.get('plan_count', 0)}\n"
        f"- capability lanes in plan: {plan_lane_text}\n"
        f"- spawn requests prepared: {orch.get('request_count', 0)}\n"
        f"- recent dispatch events logged: {orch.get('dispatched_count', 0)}\n"
        f"- recent run ids: {run_text}\n"
        f"- pipeline orchestrator/autospawn: {orch.get('pipeline',{}).get('orchestrator_ok', False)}/{orch.get('pipeline',{}).get('autospawn_ok', False)}\n"
        f"- dispatch attempted/sent: {orch.get('dispatch',{}).get('attempted', 0)}/{orch.get('dispatch',{}).get('dispatched', 0)}\n"
        f"- dispatch session id: {orch.get('dispatch',{}).get('session_id', 'none')}\n\n"
        f"Cadence artifacts prepared: {created_text}.\n"
        f"Missed intervals detected: daily={summary.get('daily_missed', 0)}, weekly={summary.get('weekly_missed', 0)}.\n"
        f"Research cycle summary: {research_text}.\n\n"
        f"Project progress snapshot:\n"
        f"- done={todo['done']} (Δ {delta['done']:+d})\n"
        f"- partial={todo['partial']} (Δ {delta['partial']:+d})\n"
        f"- open={todo['open']} (Δ {delta['open']:+d})\n"
        f"- total={todo['total']}\n"
        f"- completion={todo['pct']:.1f}%\n"
        f"- touched lanes (from git): {touch_lane_text}\n"
        f"- cycle productivity verdict: {verdict}\n"
        f"- productivity reasons: {reason_text}\n\n"
        f"Validation outcomes (commands run):\n{validation_text}\n\n"
        f"Current repo changes:\n{git_text}\n\n"
        f"Top open/partial TODO items:\n{open_text}\n\n"
        f"Narrative summary: Sandy ran planning + execution bookkeeping, refreshed queue visibility, and emitted lane-aware productivity telemetry for the next autonomous cycle."
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


def resolve_dispatch_session_id(agent_id: str = "sandy") -> str | None:
    """Resolve latest UUID sessionId for an agent from OpenClaw session store."""
    candidates = [
        Path.home() / ".openclaw" / "agents" / agent_id / "sessions" / "sessions.json",
        Path.home() / ".openclaw" / "agents" / "main" / "sessions" / "sessions.json",
    ]
    best: tuple[int, str] | None = None
    for p in candidates:
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        for _, meta in data.items():
            if not isinstance(meta, dict):
                continue
            sid = str(meta.get("sessionId", "")).strip()
            updated = int(meta.get("updatedAt", 0) or 0)
            if sid and (best is None or updated > best[0]):
                best = (updated, sid)
    return best[1] if best else None


def resolve_openclaw_command() -> tuple[list[str], list[str]]:
    """Resolve openclaw executable with explicit-path preference + PATH fallback."""
    tried: list[str] = []

    candidates: list[Path] = []
    env_bin = os.environ.get("OPENCLAW_BIN", "").strip()
    if env_bin:
        candidates.append(Path(env_bin).expanduser())

    # Preferred explicit locations for this host/user setup.
    candidates.extend(
        [
            Path.home() / ".npm-global" / "bin" / "openclaw",
            Path("/usr/local/bin/openclaw"),
            Path("/usr/bin/openclaw"),
        ]
    )

    seen: set[str] = set()
    for c in candidates:
        raw = str(c)
        if raw in seen:
            continue
        seen.add(raw)
        tried.append(raw)
        try:
            if c.is_file() and os.access(c, os.X_OK):
                return [raw], tried
        except Exception:
            continue

    found = shutil.which("openclaw")
    if found:
        tried.append(f"PATH:{found}")
        return [found], tried

    return [], tried


def _resolve_request_message(request: dict) -> str:
    spawn = request.get("spawn", {}) if isinstance(request, dict) else {}
    direct = str(spawn.get("task", "")).strip() if isinstance(spawn, dict) else ""
    if direct:
        return direct

    prompt_context = request.get("prompt_context") if isinstance(request, dict) else None
    if isinstance(prompt_context, dict):
        return render_contract_prompt(prompt_context, prompting=resolve_prompting_runtime())

    return ""


def _build_dispatch_agent_payload(request: dict) -> dict:
    raw_id = str(request.get("id", "spawn")).strip() or "spawn"
    safe_id = "".join(ch.lower() if ch.isalnum() else "-" for ch in raw_id).strip("-") or "spawn"
    stamp = now_dt().strftime("%Y%m%dt%H%M%S")

    payload = {
        "agentId": "sandy",
        "sessionKey": f"agent:sandy:orchestrator-{safe_id}-{stamp}",
        "idempotencyKey": str(uuid.uuid4()),
        "message": _resolve_request_message(request),
    }

    lane = str(request.get("lane", "")).strip()
    if lane:
        payload["lane"] = lane
    return payload


def dispatch_spawn_requests(dry_run: bool, max_dispatch: int = 3) -> dict:
    """Dispatch orchestrator requests through Gateway `agent` calls."""
    out = {
        "dispatched": 0,
        "errors": [],
        "attempted": 0,
        "session_id": None,
        "openclaw_path": None,
        "openclaw_lookup": [],
    }
    if not ORCH_REQ_PATH.exists():
        return out

    try:
        req = json.loads(ORCH_REQ_PATH.read_text(encoding="utf-8"))
        requests = req.get("requests", [])[: max_dispatch]
    except Exception as exc:
        out["errors"].append(f"load requests failed: {exc}")
        return out

    openclaw_cmd, lookup = resolve_openclaw_command()
    out["openclaw_lookup"] = lookup
    out["openclaw_path"] = openclaw_cmd[0] if openclaw_cmd else None
    if not openclaw_cmd:
        out["errors"].append(
            "openclaw binary not found (checked explicit paths + PATH). "
            f"Tried: {', '.join(lookup) if lookup else '(none)'}"
        )
        return out

    # Kept for telemetry/debugging: most recent coordinator session observed locally.
    out["session_id"] = resolve_dispatch_session_id(agent_id="sandy")

    for r in requests:
        out["attempted"] += 1
        payload = _build_dispatch_agent_payload(r)
        if not payload["message"]:
            out["errors"].append(f"{r.get('id', 'unknown')}: empty spawn task message")
            continue

        cmd = openclaw_cmd + [
            "gateway",
            "call",
            "agent",
            "--json",
            "--timeout",
            "120000",
            "--params",
            json.dumps(payload, ensure_ascii=False),
        ]

        if dry_run:
            print("DRY RUN dispatch via agent for", r.get("id", "(unknown)"))
            out["dispatched"] += 1
            continue

        try:
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=130)
            ok = proc.returncode == 0
            if ok:
                try:
                    parsed = json.loads((proc.stdout or "").strip() or "{}")
                except Exception:
                    parsed = {}
                status = str(parsed.get("status", "")).strip().lower() if isinstance(parsed, dict) else ""
                run_id = parsed.get("runId") if isinstance(parsed, dict) else None
                ok = bool(run_id) or status in {"accepted", "ok", "in_flight"}

            if ok:
                out["dispatched"] += 1
            else:
                err = (proc.stderr or proc.stdout or "unknown error").strip()
                out["errors"].append(f"{r.get('id','unknown')}: {err}")
        except Exception as exc:
            out["errors"].append(f"{r.get('id','unknown')}: {exc}")

    return out


def full_pass(scheduler: str, send_telegram: bool, dry_run: bool, max_open_items: int, with_orchestration: bool = False, with_dispatch: bool = False, dispatch_limit: int = 3, validation_commands: list[str] | None = None) -> bool:
    started = now_dt()
    cycle_id = started.strftime("%Y%m%dT%H%M%S")
    summary = run_scheduler(scheduler=scheduler, dry_run=dry_run)

    orchestration = {"orchestrator_ok": False, "autospawn_ok": False, "errors": []}
    dispatch = {"dispatched": 0, "errors": [], "attempted": 0}
    if with_orchestration:
        orchestration = run_orchestrator_pipeline(limit=dispatch_limit, dry_run=dry_run)
    if with_dispatch:
        dispatch = dispatch_spawn_requests(dry_run=dry_run, max_dispatch=dispatch_limit)

    validation_runtime = resolve_validation_runtime(validation_commands_override=validation_commands)
    effective_validation_commands = validation_runtime.get("commands", [])
    validation_policy = validation_runtime.get("policy", {})
    validation_outcomes = run_validation_commands(effective_validation_commands, dry_run=dry_run, policy=validation_policy)
    validation_gate_ok = evaluate_validation_gate(validation_outcomes, validation_policy)
    research_summary = maybe_write_research_cycle_summary(dry_run=dry_run)

    todo_text = TODO_PATH.read_text(encoding="utf-8", errors="ignore") if TODO_PATH.exists() else ""
    todo = parse_todo_counts(todo_text)
    open_items = list_open_checkbox_items(limit=max_open_items)
    git_lines = git_status_short(limit=12)
    lane_hits = lanes_from_git_status(git_lines)
    orch = load_orchestrator_snapshot()
    orch["pipeline"] = orchestration
    orch["dispatch"] = dispatch

    state = load_state()
    prev_todo = state.get("last_todo_snapshot", {})
    delta = todo_delta(todo, prev_todo)
    productive, productivity_reasons = productivity_gate(delta=delta, lane_hits=lane_hits, orch=orch)
    if not validation_gate_ok:
        productive = False
        productivity_reasons.append("validation gate failed")
    state["last_run"]["full_pass"] = now_dt().isoformat(timespec="seconds")
    state["last_todo_snapshot"] = todo
    state["last_productivity"] = {
        "productive": productive,
        "reasons": productivity_reasons,
        "validation_gate_ok": validation_gate_ok,
        "validation_commands": effective_validation_commands,
        "at": now_dt().isoformat(timespec="seconds"),
    }
    save_state(state)

    message = compose_fullpass_message(
        summary,
        todo,
        open_items,
        git_lines,
        orch,
        delta,
        lane_hits,
        productive,
        productivity_reasons,
        validation_outcomes,
        research_summary,
    )

    queue_notification(message, dry_run=dry_run)
    telegram_sent = False
    telegram_error = None
    if send_telegram:
        try:
            send_telegram_message(message, dry_run=dry_run)
            telegram_sent = True
        except Exception as exc:
            telegram_error = str(exc)
            warn = f"[SANDY-ALERT] Telegram send skipped: {exc}"
            queue_notification(warn, dry_run=dry_run)
            print(warn)

    ended = now_dt()
    duration_ms = int((ended - started).total_seconds() * 1000)
    cycle_event = {
        "ts": ended.isoformat(timespec="seconds"),
        "event": "full_pass",
        "cycle_id": cycle_id,
        "scheduler": scheduler,
        "dry_run": dry_run,
        "with_orchestration": with_orchestration,
        "with_dispatch": with_dispatch,
        "dispatch_limit": dispatch_limit,
        "duration_ms": duration_ms,
        "todo": todo,
        "todo_delta": delta,
        "pipeline": orch.get("pipeline", {}),
        "dispatch": orch.get("dispatch", {}),
        "validation": validation_outcomes,
        "validation_gate_ok": validation_gate_ok,
        "validation_commands": effective_validation_commands,
        "validation_policy": validation_policy,
        "research_summary": research_summary,
        "telegram_sent": telegram_sent,
        "telegram_error": telegram_error,
    }
    append_jsonl(ORCH_CYCLE_LOG, cycle_event)

    print(f"Full pass complete. cycle_id={cycle_id} duration_ms={duration_ms}")
    return validation_gate_ok


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
    p_full.add_argument(
        "--validation-command",
        action="append",
        dest="validation_commands",
        default=None,
        help="Validation shell command to run and summarize (repeatable)",
    )

    p_add = sub.add_parser("todo-add", help="Add a checkbox item to plans/todo.md")
    p_add.add_argument("--text", required=True)
    p_add.add_argument("--section", required=False)

    p_set = sub.add_parser("todo-set", help="Mark first matching todo checkbox")
    p_set.add_argument("--match", required=True)
    p_set.add_argument("--state", choices=["done", "open", "partial"], required=True)

    p_remove = sub.add_parser("todo-remove", help="Remove first matching todo checkbox")
    p_remove.add_argument("--match", required=True)

    p_promote = sub.add_parser("promote-tweaks", help="Promote repeated policy tweaks into AGENTS/WORKFLOW")
    p_promote.add_argument("--min-count", type=int, default=3)
    p_promote.add_argument("--dry-run", action="store_true")

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
        validation_gate_ok = full_pass(
            scheduler=args.scheduler,
            send_telegram=args.send_telegram,
            dry_run=args.dry_run,
            max_open_items=args.max_open_items,
            with_orchestration=args.with_orchestration,
            with_dispatch=args.with_dispatch,
            dispatch_limit=args.dispatch_limit,
            validation_commands=args.validation_commands,
        )
        return 0 if validation_gate_ok else 1

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

    if args.cmd == "promote-tweaks":
        result = promote_policy_tweaks(min_count=args.min_count, dry_run=args.dry_run)
        promoted = result.get("promoted", [])
        if promoted:
            print(f"Promoted {len(promoted)} tweak(s).")
            for item in promoted:
                print(f"- {item['policy_tweak']} -> {item['target']}")
        else:
            print("No tweaks met promotion threshold.")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
