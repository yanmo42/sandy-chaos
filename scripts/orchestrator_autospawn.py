#!/usr/bin/env python3
"""Auto-spawn plan executor (v2).

Consumes `memory/orchestrator_task_plan.jsonl`, emits concrete task-dispatch
payloads, and can optionally dispatch them through the Gateway `agent` API.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path

try:
    from nfem_suite.intelligence.ygg.continuity import (
        ALLOWED_BRANCH_OUTCOME_CLASSES,
        ALLOWED_DISPOSITIONS,
        ALLOWED_PROMOTION_TARGETS,
        ALLOWED_PROMOTION_REVIEW_REQUIREMENTS,
        ALLOWED_PROMOTION_REVIEW_STATUSES,
    )
    from scripts.dispatch_log_validator import validate_dispatch_log_entry
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from nfem_suite.intelligence.ygg.continuity import (
        ALLOWED_BRANCH_OUTCOME_CLASSES,
        ALLOWED_DISPOSITIONS,
        ALLOWED_PROMOTION_TARGETS,
        ALLOWED_PROMOTION_REVIEW_REQUIREMENTS,
        ALLOWED_PROMOTION_REVIEW_STATUSES,
    )
    from scripts.dispatch_log_validator import validate_dispatch_log_entry

ROOT = Path(__file__).resolve().parents[1]
ORCH_CONFIG = ROOT / "config" / "orchestrator.json"
DEFAULT_PLAN = ROOT / "memory" / "orchestrator_task_plan.jsonl"
REQUESTS_OUT = ROOT / "memory" / "orchestrator_spawn_requests.json"
DISPATCH_LOG = ROOT / "memory" / "orchestrator_dispatch_log.jsonl"

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
DEFAULT_DISPATCH_AGENT_ID = ROOT.name
GOVERNANCE_POLICY_REF = "spine/membranes/governance-runtime-v1.yaml"
MEMORY_POLICY_REF = "spine/membranes/memory-dispatch-v1.yaml"


def _as_string_list(raw: object) -> list[str]:
    if isinstance(raw, str):
        text = raw.strip()
        return [text] if text else []
    if isinstance(raw, list):
        out: list[str] = []
        for item in raw:
            text = str(item).strip()
            if text:
                out.append(text)
        return out
    return []


def _extract_dispatch_membrane_evidence(req: dict) -> dict:
    """Build membrane evidence fields for dispatch logs.

    This keeps governance/runtime and memory/dispatch membrane traces explicit
    without changing dispatch semantics.
    """
    prompt_context = req.get("prompt_context", {}) if isinstance(req, dict) else {}
    capability_lane = str(prompt_context.get("capability_lane", req.get("capability_lane", ""))).strip().lower()

    request_id = str(req.get("id", "unknown-request")).strip() or "unknown-request"

    memory_artifact_ids = []
    continuity_artifact_ids: list[str] = []
    memory_request_source = "request"
    for source, candidate in (
        ("request.memory_artifact_ids", req.get("memory_artifact_ids")),
        ("prompt_context.memory_artifact_ids", prompt_context.get("memory_artifact_ids")),
        ("prompt_context.continuity_artifact_ids", prompt_context.get("continuity_artifact_ids")),
    ):
        refs = _as_string_list(candidate)
        if refs and memory_request_source == "request":
            memory_request_source = source
        if source == "prompt_context.continuity_artifact_ids":
            continuity_artifact_ids.extend(refs)
        memory_artifact_ids.extend(refs)

    deduped_ids: list[str] = []
    seen: set[str] = set()
    for artifact_id in memory_artifact_ids:
        if artifact_id in seen:
            continue
        seen.add(artifact_id)
        deduped_ids.append(artifact_id)

    continuity_relevant = capability_lane == "continuity" or bool(continuity_artifact_ids)
    memory_consulted = bool(deduped_ids)

    if memory_request_source == "request" and continuity_relevant:
        memory_request_source = "prompt_context.capability_lane"

    evidence = {
        "continuity_relevant": continuity_relevant,
        "memory_consulted": memory_consulted,
        "memory_artifact_ids": deduped_ids,
        "governance_policy_ref": GOVERNANCE_POLICY_REF,
    }
    if continuity_relevant or memory_consulted:
        evidence["memory_policy_ref"] = MEMORY_POLICY_REF
        evidence["memory_request_provenance"] = f"{request_id}:{memory_request_source}"
    return evidence


def validate_continuity_contract(contract: dict) -> list[str]:
    errors: list[str] = []
    disposition = contract.get("disposition")
    promotion_target = contract.get("promotion_target")
    outcome_class = contract.get("branch_outcome_class")
    review_requirement = contract.get("promotion_review_requirement")
    review_status = contract.get("promotion_review_status")
    if disposition not in ALLOWED_DISPOSITIONS:
        errors.append(f"invalid or missing disposition '{disposition}'")
    if promotion_target not in ALLOWED_PROMOTION_TARGETS:
        errors.append(f"invalid or missing promotion_target '{promotion_target}'")
    if outcome_class not in ALLOWED_BRANCH_OUTCOME_CLASSES:
        errors.append(f"invalid or missing branch_outcome_class '{outcome_class}'")
    if review_requirement not in ALLOWED_PROMOTION_REVIEW_REQUIREMENTS:
        errors.append(f"invalid or missing promotion_review_requirement '{review_requirement}'")
    if review_status not in ALLOWED_PROMOTION_REVIEW_STATUSES:
        errors.append(f"invalid or missing promotion_review_status '{review_status}'")
    if review_requirement == "not-required" and review_status != "not-required":
        errors.append("promotion_review_status must be 'not-required' when review is not required")
    if review_requirement == "human-review" and review_status == "not-required":
        errors.append("human-review targets may not use review_status 'not-required'")
    return errors


def promotion_review_gate_error(contract: dict) -> str | None:
    requirement = str(contract.get("promotion_review_requirement", "")).strip()
    status = str(contract.get("promotion_review_status", "")).strip()
    target = str(contract.get("promotion_target", "")).strip() or "(missing target)"
    if requirement == "human-review" and status != "approved":
        return f"promotion_target '{target}' requires human review before dispatch (status={status or 'missing'})"
    return None


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
    try:
        if ORCH_CONFIG.exists():
            cfg = json.loads(ORCH_CONFIG.read_text(encoding="utf-8"))
            raw = cfg.get("prompting", {}) if isinstance(cfg, dict) else {}
            return _normalize_prompting(raw if isinstance(raw, dict) else None)
    except Exception:
        pass
    return _normalize_prompting(None)


def render_contract_prompt(task: dict, prompting: dict | None = None) -> str:
    cfg = _normalize_prompting(prompting)
    lane = str(task.get("lane", "sandy-builder")).strip() or "sandy-builder"
    section = str(task.get("section", "(unknown section)")).strip() or "(unknown section)"
    goal = str(task.get("goal", "(missing goal)")).strip() or "(missing goal)"
    constraints = _as_lines(task.get("constraints"))
    dod = _as_lines(task.get("definition_of_done"))
    validation_command = str(task.get("validation_command", resolve_default_validation_command())).strip() or resolve_default_validation_command()

    lane_map = cfg.get("byLane", {}) if isinstance(cfg, dict) else {}
    lane_specific = _as_lines(lane_map.get(lane))

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
        rendered = str(cfg.get("template", DEFAULT_PROMPT_TEMPLATE)).format(**fields).strip()
    except Exception:
        rendered = DEFAULT_PROMPT_TEMPLATE.format(**fields).strip()

    continuity_artifacts = _as_string_list(task.get("memory_artifact_ids"))
    continuity_context = task.get("continuity_context", {}) if isinstance(task.get("continuity_context"), dict) else {}
    disposition = str(task.get("disposition", "")).strip()
    promotion_target = str(task.get("promotion_target", "")).strip()
    outcome_class = str(task.get("branch_outcome_class", "")).strip()
    review_requirement = str(task.get("promotion_review_requirement", "")).strip()
    review_status = str(task.get("promotion_review_status", "")).strip()
    rendered += (
        "\n\nContinuity contract:\n"
        f"- Branch outcome class: {outcome_class or '(missing)'}\n"
        f"- Disposition: {disposition or '(missing)'}\n"
        f"- Promotion target: {promotion_target or '(missing)'}\n"
        f"- Promotion review: {review_requirement or '(missing)'} / {review_status or '(missing)'}\n"
        "- End your completion note by restating all four fields explicitly."
    )
    if continuity_artifacts:
        rendered += "\n\nContinuity evidence artifacts:\n" + _render_bullets(continuity_artifacts)
    topological_signal = continuity_context.get("topological_memory_signal", {}) if isinstance(continuity_context, dict) else {}
    if topological_signal:
        notes = _as_lines(topological_signal.get("notes"))
        rendered += (
            "\n\nContinuity retrieval context:\n"
            f"- Source: {topological_signal.get('source', '(missing)')}\n"
            f"- Query count: {topological_signal.get('query_count', 0)}\n"
            f"- Topology hit-rate: {float(topological_signal.get('topology_hit_rate', 0.0)):.3f}\n"
            f"- Topology MRR: {float(topological_signal.get('topology_mrr', 0.0)):.3f}\n"
            f"- Advisory: {topological_signal.get('advisory', '(none)')}"
        )
        if notes:
            rendered += "\n- Retrieval notes:\n" + _render_bullets(notes)
    session_resume = continuity_context.get("session_resume") if isinstance(continuity_context, dict) else None
    if session_resume:
        resume_type = str(session_resume.get("type", "prior"))
        ts = str(session_resume.get("timestamp", ""))[:10]
        rendered += f"\n\nPrior session context ({resume_type}, {ts}):"
        rendered += f"\n- Lane: {session_resume.get('lane', '(unknown)')}"
        if session_resume.get("branch_purpose"):
            rendered += f"\n- Purpose: {session_resume['branch_purpose']}"
        if session_resume.get("current_state"):
            rendered += f"\n- State at close: {session_resume['current_state']}"
        if session_resume.get("summary"):
            rendered += f"\n- Summary: {session_resume['summary']}"
        if session_resume.get("next_action"):
            rendered += f"\n- Next action: {session_resume['next_action']}"
        if session_resume.get("blocker"):
            rendered += f"\n- Blocker: {session_resume['blocker']}"
        prior_refs = _as_lines(session_resume.get("relevant_artifact_refs"))
        if prior_refs:
            rendered += "\n- Prior refs:\n" + _render_bullets(prior_refs)
    return rendered


def resolve_default_validation_command() -> str:
    try:
        if ORCH_CONFIG.exists():
            cfg = json.loads(ORCH_CONFIG.read_text(encoding="utf-8"))
            validation = cfg.get("validation", {}) if isinstance(cfg, dict) else {}
            commands_cfg = validation.get("commands", {}) if isinstance(validation, dict) else {}
            default_value = commands_cfg.get("default") if isinstance(commands_cfg, dict) else None
            if isinstance(default_value, list):
                default_value = default_value[0] if default_value else None
            if isinstance(default_value, str) and default_value.strip():
                text = default_value.strip()
                if text.startswith("./venv/bin/python") and not (ROOT / "venv" / "bin" / "python").exists():
                    return text.replace("./venv/bin/python", sys.executable or "python3", 1)
                return text
    except Exception:
        pass
    return f"{sys.executable or 'python3'} -m unittest discover -s tests -q"


def to_spawn_request(task: dict, idx: int, prompting: dict | None = None) -> dict:
    contract_errors = validate_continuity_contract(task)
    if contract_errors:
        raise ValueError("; ".join(contract_errors))

    lane = str(task.get("lane", "sandy-builder")).strip() or "sandy-builder"
    contract = {
        "lane": lane,
        "capability_lane": task.get("capability_lane", "unspecified"),
        "goal": task.get("goal", "(missing goal)"),
        "section": task.get("section", "(unknown section)"),
        "branch_outcome_class": task.get("branch_outcome_class", ""),
        "disposition": task.get("disposition", ""),
        "promotion_target": task.get("promotion_target", ""),
        "promotion_review_requirement": task.get("promotion_review_requirement", ""),
        "promotion_review_status": task.get("promotion_review_status", ""),
        "constraints": task.get("constraints", []),
        "definition_of_done": task.get("definition_of_done", []),
        "memory_artifact_ids": task.get("memory_artifact_ids", []),
        "continuity_context": task.get("continuity_context", {}),
        "validation_command": task.get("validation_command", resolve_default_validation_command()),
    }
    prompt = render_contract_prompt(contract, prompting=prompting)

    return {
        "id": f"spawn-{idx:02d}",
        "createdAt": now_iso(),
        "lane": lane,
        "prompt_context": contract,
        "prompt_schema_version": "v1",
        "spawn": {
            "runtime": "subagent",
            "mode": "run",
            "cleanup": "delete",
            "model": "openai-codex/gpt-5.3-codex",
            "cwd": str(ROOT),
            "task": prompt,
        },
    }


def append_dispatch_log(entry: dict) -> None:
    errors = validate_dispatch_log_entry(entry)
    if errors:
        raise ValueError("; ".join(errors))
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


def resolve_dispatch_agent_id() -> str:
    try:
        if ORCH_CONFIG.exists():
            cfg = json.loads(ORCH_CONFIG.read_text(encoding="utf-8"))
            dispatch = cfg.get("dispatch", {}) if isinstance(cfg, dict) else {}
            configured = str(dispatch.get("agentId", "")).strip() if isinstance(dispatch, dict) else ""
            if configured:
                return configured
    except Exception:
        pass

    env_value = os.environ.get("OPENCLAW_AGENT_ID", "").strip()
    if env_value:
        return env_value

    return DEFAULT_DISPATCH_AGENT_ID


def _build_dispatch_agent_call(req: dict) -> dict:
    """Build a Gateway `agent` call payload from a spawn request."""
    spawn = req.get("spawn", {}) if isinstance(req, dict) else {}
    raw_id = str(req.get("id", "spawn")).strip() or "spawn"
    safe_id = "".join(ch.lower() if ch.isalnum() else "-" for ch in raw_id).strip("-") or "spawn"
    stamp = datetime.now().strftime("%Y%m%dt%H%M%S")
    agent_id = resolve_dispatch_agent_id()

    payload = {
        "agentId": agent_id,
        "sessionKey": f"agent:{agent_id}:orchestrator-{safe_id}-{stamp}",
        "idempotencyKey": str(uuid.uuid4()),
        "message": str(spawn.get("task", "")).strip(),
    }

    lane = str(req.get("lane", "")).strip()
    if lane:
        payload["lane"] = lane
    return payload


def dispatch_spawn_requests(requests: list[dict], dry_run: bool = False) -> dict:
    out = {"attempted": 0, "dispatched": 0, "errors": [], "results": []}

    openclaw_cmd = resolve_openclaw_command()
    if not openclaw_cmd:
        out["errors"].append("openclaw binary not found")
        return out

    for req in requests:
        out["attempted"] += 1
        contract_errors = validate_continuity_contract(req.get("prompt_context", {}))
        if contract_errors:
            out["errors"].append(f"{req.get('id', 'unknown')}: {'; '.join(contract_errors)}")
            continue
        review_gate_error = promotion_review_gate_error(req.get("prompt_context", {}))
        if review_gate_error:
            out["errors"].append(f"{req.get('id', 'unknown')}: {review_gate_error}")
            continue

        payload = _build_dispatch_agent_call(req)
        membrane_evidence = _extract_dispatch_membrane_evidence(req)

        if not payload["message"]:
            out["errors"].append(f"{req.get('id', 'unknown')}: empty spawn task message")
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
            out["dispatched"] += 1
            out["results"].append(
                {
                    "id": req.get("id"),
                    "ok": True,
                    "dry_run": True,
                    "control_mode": "control-affecting",
                    **membrane_evidence,
                }
            )
            append_dispatch_log(
                {
                    "ts": now_iso(),
                    "event": "spawn_dispatched",
                    "id": req.get("id"),
                    "ok": True,
                    "dry_run": True,
                    "method": "agent",
                    "sessionKey": payload["sessionKey"],
                    "control_mode": "control-affecting",
                    **membrane_evidence,
                }
            )
            continue

        try:
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=130)
            ok = proc.returncode == 0
            run_id = None
            status = None
            if ok:
                try:
                    parsed = json.loads((proc.stdout or "").strip() or "{}")
                except Exception:
                    parsed = {}
                if isinstance(parsed, dict):
                    run_id = parsed.get("runId")
                    status = str(parsed.get("status", "")).strip().lower()
                ok = bool(run_id) or status in {"accepted", "ok", "in_flight"}

            result = {
                "id": req.get("id"),
                "ok": ok,
                "runId": run_id,
                "status": status,
                "control_mode": "control-affecting",
                **membrane_evidence,
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
                    "method": "agent",
                    "sessionKey": payload["sessionKey"],
                    "runId": run_id,
                    "status": status,
                    "control_mode": "control-affecting",
                    **membrane_evidence,
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
                    "method": "agent",
                    "sessionKey": payload["sessionKey"],
                    "control_mode": "control-affecting",
                    **membrane_evidence,
                    "error": str(exc),
                }
            )

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default=str(DEFAULT_PLAN))
    ap.add_argument("--out", default=str(REQUESTS_OUT))
    ap.add_argument("--limit", type=int, default=3)
    ap.add_argument("--execute", action="store_true", help="Dispatch each request via OpenClaw Gateway `agent` method")
    ap.add_argument("--dry-run", action="store_true", help="Prepare/dispatch without making API calls")
    args = ap.parse_args()

    plan_path = Path(args.plan)
    out_path = Path(args.out)

    tasks = load_jsonl(plan_path)
    selected = tasks[: max(0, args.limit)]

    contract_errors: list[str] = []
    for idx, task in enumerate(selected, start=1):
        for err in validate_continuity_contract(task):
            contract_errors.append(f"task {idx}: {err}")
    if contract_errors:
        print("Invalid orchestrator task contracts:")
        for err in contract_errors:
            print(f"- {err}")
        return 1

    prompting = resolve_prompting_runtime()
    requests = [to_spawn_request(task, i + 1, prompting=prompting) for i, task in enumerate(selected)]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"generatedAt": now_iso(), "requests": requests}, indent=2), encoding="utf-8")

    append_dispatch_log(
        {
            "ts": now_iso(),
            "event": "spawn_requests_prepared",
            "plan": str(plan_path),
            "out": str(out_path),
            "count": len(requests),
            "control_mode": "descriptive",
            "governance_policy_ref": GOVERNANCE_POLICY_REF,
        }
    )

    print(f"Prepared {len(requests)} spawn requests -> {out_path}")

    if args.execute:
        result = dispatch_spawn_requests(requests=requests, dry_run=args.dry_run)
        print(
            f"Dispatch complete via agent bridge: dispatched={result['dispatched']} "
            f"attempted={result['attempted']} errors={len(result['errors'])}"
        )
        if result["errors"]:
            for e in result["errors"]:
                print(f"- {e}")
            return 1
    else:
        print("Next step: run with --execute to dispatch via OpenClaw Gateway `agent` API.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
