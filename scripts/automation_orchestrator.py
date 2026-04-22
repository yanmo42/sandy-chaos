#!/usr/bin/env python3
"""Sandy automation orchestrator (v1).

Purpose:
- Select high-priority TODO items
- Build explicit subagent task contracts
- Emit task plan JSONL for OpenClaw dispatch (Gateway `agent` bridge)
- Write cycle summary for human + reporter lane

This script is intentionally transport-agnostic: it prepares task contracts that
can be executed by OpenClaw subagents from chat or TUI.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

try:
    from nfem_suite.intelligence.ygg.continuity import (
        ALLOWED_BRANCH_OUTCOME_CLASSES,
        ALLOWED_DISPOSITIONS,
        ALLOWED_PROMOTION_TARGETS,
        ALLOWED_PROMOTION_REVIEW_REQUIREMENTS,
        ALLOWED_PROMOTION_REVIEW_STATUSES,
        load_latest_checkpoint,
        load_latest_resume_artifact,
    )
    from nfem_suite.intelligence.ygg.topological_memory_runtime import write_retrieval_trace
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from nfem_suite.intelligence.ygg.continuity import (
        ALLOWED_BRANCH_OUTCOME_CLASSES,
        ALLOWED_DISPOSITIONS,
        ALLOWED_PROMOTION_TARGETS,
        ALLOWED_PROMOTION_REVIEW_REQUIREMENTS,
        ALLOWED_PROMOTION_REVIEW_STATUSES,
        load_latest_checkpoint,
        load_latest_resume_artifact,
    )
    from nfem_suite.intelligence.ygg.topological_memory_runtime import write_retrieval_trace

ROOT = Path(__file__).resolve().parents[1]

CONTINUITY_CORE_ARTIFACTS = [
    "spine/subsystems/SC-SUBSYSTEM-0001-topological-memory-v0.yaml",
    "spine/membranes/memory-dispatch-v1.yaml",
]

TOPOLOGICAL_MEMORY_ARTIFACTS = [
    "docs/archive/topological_memory_continuity_retrieval_v0.md",
    "memory/research/topological-memory-v0/comparison_summary_v0.json",
    "memory/research/topological-memory-v0/comparison_report_v0.md",
    "docs/notes/topological_memory_v0_provisional_validation.md",
]


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
        out = subprocess.check_output(
            ["git", "status", "--short"],
            cwd=cwd,
            text=True,
            stderr=subprocess.DEVNULL,
        )
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


def capability_lane_for_item(item: TodoItem) -> str:
    text = f"{item.section} {item.text}".lower()
    if any(k in text for k in ["memory", "continuity", "retrieval", "recall", "topological"]):
        return "continuity"
    if any(k in text for k in ["test", "falsification", "verify", "validation"]):
        return "validation"
    if any(k in text for k in ["docs", "document", "claim tier", "math", "theory", "foundations"]):
        return "theory"
    if any(k in text for k in ["nfem", "simulation", "observer coupling", "temporal communication", "engine"]):
        return "simulation"
    return "ops"


def resolve_validation_command(cfg: dict, lane: str) -> str:
    validation = cfg.get("validation", {}) if isinstance(cfg, dict) else {}
    commands_cfg = validation.get("commands", {}) if isinstance(validation, dict) else {}
    by_lane = commands_cfg.get("byLane", {}) if isinstance(commands_cfg, dict) else {}

    lane_value = by_lane.get(lane)
    if isinstance(lane_value, list):
        lane_value = lane_value[0] if lane_value else None
    if isinstance(lane_value, str) and lane_value.strip():
        return lane_value.strip().replace(
            "./venv/bin/python",
            sys.executable or "python3",
            1,
        ) if lane_value.strip().startswith("./venv/bin/python") and not Path("./venv/bin/python").exists() else lane_value.strip()

    default_value = commands_cfg.get("default") if isinstance(commands_cfg, dict) else None
    if isinstance(default_value, list):
        default_value = default_value[0] if default_value else None
    if isinstance(default_value, str) and default_value.strip():
        return default_value.strip().replace(
            "./venv/bin/python",
            sys.executable or "python3",
            1,
        ) if default_value.strip().startswith("./venv/bin/python") and not Path("./venv/bin/python").exists() else default_value.strip()

    # Safe fallback if config is missing/malformed.
    return f"{sys.executable or 'python3'} -m unittest discover -s tests -q"


def resolve_promotion_review_policy(cfg: dict, promotion_target: str, outcome_class: str) -> dict[str, str]:
    review_cfg = cfg.get("promotionReview", {}) if isinstance(cfg, dict) else {}
    by_outcome = review_cfg.get("byOutcomeClass", {}) if isinstance(review_cfg, dict) else {}
    by_target = review_cfg.get("byTarget", {}) if isinstance(review_cfg, dict) else {}

    outcome_cfg = by_outcome.get(outcome_class, {}) if isinstance(by_outcome, dict) else {}

    # Target-specific policy takes precedence for granular overrides (e.g., todo).
    target_cfg = by_target.get(promotion_target) or outcome_cfg

    default_requirement = outcome_cfg.get(
        "requirement",
        "not-required" if outcome_class == "local" or promotion_target in {"todo", "log-only"} else "human-review",
    )
    requirement = str(target_cfg.get("requirement", review_cfg.get("defaultRequirement", default_requirement))).strip()
    if requirement not in ALLOWED_PROMOTION_REVIEW_REQUIREMENTS:
        requirement = str(default_requirement).strip()

    default_status = "not-required" if requirement == "not-required" else "pending"
    default_status = str(outcome_cfg.get("status", default_status)).strip() or default_status
    status = str(target_cfg.get("status", review_cfg.get("defaultStatus", default_status))).strip()
    if status not in ALLOWED_PROMOTION_REVIEW_STATUSES:
        status = default_status
    if requirement == "not-required":
        status = "not-required"
    elif status == "not-required":
        status = "pending"

    return {
        "requirement": requirement,
        "status": status,
    }


def load_topological_memory_signal(root: Path = ROOT) -> dict | None:
    summary_path = root / "memory" / "research" / "topological-memory-v0" / "comparison_summary_v0.json"
    if not summary_path.exists():
        return None

    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    metrics = summary.get("metrics", {}) if isinstance(summary, dict) else {}
    topology = metrics.get("topology", {}) if isinstance(metrics, dict) else {}
    keyword = metrics.get("keyword", {}) if isinstance(metrics, dict) else {}
    recency = metrics.get("recency", {}) if isinstance(metrics, dict) else {}

    if not topology.get("available"):
        return None

    topology_hit = float(topology.get("hit_rate", 0.0))
    topology_mrr = float(topology.get("mrr", 0.0))
    keyword_hit = float(keyword.get("hit_rate", 0.0)) if keyword.get("available") else None
    keyword_mrr = float(keyword.get("mrr", 0.0)) if keyword.get("available") else None
    recency_hit = float(recency.get("hit_rate", 0.0)) if recency.get("available") else None
    recency_mrr = float(recency.get("mrr", 0.0)) if recency.get("available") else None

    notes: list[str] = []
    if recency_hit is not None and recency_mrr is not None and topology_hit > recency_hit and topology_mrr > recency_mrr:
        notes.append("topology currently beats recency on hit-rate and MRR")
    if keyword_hit is not None and keyword_mrr is not None:
        if topology_hit > keyword_hit and topology_mrr < keyword_mrr:
            notes.append("topology beats keyword on hit-rate but still trails on MRR")
        elif topology_hit > keyword_hit and topology_mrr >= keyword_mrr:
            notes.append("topology currently beats keyword on both hit-rate and MRR")

    return {
        "source": str(summary_path.relative_to(root)),
        "query_count": int(summary.get("query_count", 0)),
        "top_k": int(summary.get("top_k", 0)),
        "topology_hit_rate": topology_hit,
        "topology_mrr": topology_mrr,
        "keyword_hit_rate": keyword_hit,
        "keyword_mrr": keyword_mrr,
        "recency_hit_rate": recency_hit,
        "recency_mrr": recency_mrr,
        "notes": notes,
        "advisory": "Inform continuity/planning context only; not sufficient by itself for promotion.",
    }


def load_session_resume_context(root: Path = ROOT) -> dict | None:
    """Load the latest resume artifact or checkpoint as inline session context.

    Tries resume artifacts first (richer); falls back to checkpoints.
    Returns None if no prior session artifacts exist.
    """
    artifact = load_latest_resume_artifact(root)
    if artifact is not None:
        return {
            "type": "resume",
            "timestamp": artifact.timestamp,
            "lane": artifact.lane,
            "branch_purpose": artifact.branch_purpose,
            "current_state": artifact.current_state,
            "next_action": artifact.next_action,
            "blocker": artifact.blocker,
            "summary": artifact.summary,
            "relevant_artifact_refs": list(artifact.relevant_artifact_refs),
        }
    checkpoint = load_latest_checkpoint(root)
    if checkpoint is not None:
        return {
            "type": "checkpoint",
            "timestamp": checkpoint.timestamp,
            "lane": checkpoint.lane,
            "summary": checkpoint.summary,
            "next_action": checkpoint.next_action,
        }
    return None


def continuity_artifact_ids_for_item(item: TodoItem, root: Path = ROOT) -> list[str]:
    text = f"{item.section} {item.text}".lower()
    refs: list[str] = []

    if capability_lane_for_item(item) != "continuity":
        return refs

    for rel in CONTINUITY_CORE_ARTIFACTS:
        if (root / rel).exists():
            refs.append(rel)

    if any(k in text for k in ["topological", "retrieval", "recall", "memory"]):
        for rel in TOPOLOGICAL_MEMORY_ARTIFACTS:
            if (root / rel).exists():
                refs.append(rel)

    # Include the latest durable session artifact so the dispatched agent sees where we left off
    for subdir in ("resume", "checkpoints"):
        artifact_dir = root / "state" / "ygg" / subdir
        if artifact_dir.exists():
            candidates = sorted(artifact_dir.glob("*.json"))
            if candidates:
                refs.append(str(candidates[-1].relative_to(root)))

    deduped: list[str] = []
    seen: set[str] = set()
    for ref in refs:
        if ref in seen:
            continue
        seen.add(ref)
        deduped.append(ref)
    return deduped


def infer_disposition_and_promotion_target(item: TodoItem) -> tuple[str, str]:
    text = f"{item.section} {item.text}".lower()

    if "workflow" in text:
        return "POLICY_PROMOTE", "workflow"
    if "foundations" in text:
        return "POLICY_PROMOTE", "foundations"
    if any(k in text for k in ["docs", "document", "claim tier"]):
        return "DOC_PROMOTE", "docs"
    if any(k in text for k in ["memory", "continuity", "retrieval", "topological"]):
        return "POLICY_PROMOTE", "tests/config"
    if any(k in text for k in ["test", "config", "validation", "orchestrator", "artifact", "summary", "automation"]):
        return "POLICY_PROMOTE", "tests/config"
    if any(k in text for k in ["todo", "next action", "backlog"]):
        return "TODO_PROMOTE", "todo"
    return "LOG_ONLY", "log-only"


def infer_branch_outcome_class(disposition: str) -> str:
    if disposition in {"DROP_LOCAL", "LOG_ONLY"}:
        return "local"
    if disposition in {"TODO_PROMOTE", "DOC_PROMOTE"}:
        return "promotable"
    if disposition == "POLICY_PROMOTE":
        return "policy-relevant"
    return "blocked"


def _infer_routed_target_from_text(text: str, disposition: str, current_target: str) -> str:
    if disposition == "LOG_ONLY":
        return "log-only"
    if disposition == "TODO_PROMOTE":
        return "todo"
    if disposition == "DOC_PROMOTE":
        return "docs"
    if disposition == "POLICY_PROMOTE":
        if "workflow" in text:
            return "workflow"
        if "foundations" in text:
            return "foundations"
        if any(k in text for k in ["test", "config", "validation", "orchestrator", "artifact", "summary", "automation", "dispatch"]):
            return "tests/config"
        if current_target in {"workflow", "foundations", "tests/config"}:
            return current_target
        return "tests/config"
    return current_target



def apply_lux_nyx_governance_routing(
    item: TodoItem,
    disposition: str,
    promotion_target: str,
    lux_nyx: dict | None,
) -> tuple[str, str]:
    if not isinstance(lux_nyx, dict):
        return disposition, promotion_target

    destination = str(lux_nyx.get("destination", "")).strip()
    routed_disposition = str(lux_nyx.get("routing_disposition", "")).strip()
    routed_target = str(lux_nyx.get("routing_promotion_target", "")).strip()
    text = f"{item.section} {item.text}".lower()

    if routed_disposition or routed_target:
        final_disposition = routed_disposition or disposition
        final_target = routed_target or _infer_routed_target_from_text(text, final_disposition, promotion_target)
        return final_disposition, final_target

    if destination in {"archive", "refusal-log"}:
        return "LOG_ONLY", "log-only"

    if destination == "hold-queue":
        return "TODO_PROMOTE", "todo"

    if destination == "promotion-queue" and promotion_target in {"log-only", "todo"}:
        if "workflow" in text:
            return "POLICY_PROMOTE", "workflow"
        if "foundations" in text or "admissibility" in text:
            return "POLICY_PROMOTE", "foundations"
        if any(k in text for k in ["test", "config", "validation", "orchestrator", "artifact", "summary", "automation", "dispatch"]):
            return "POLICY_PROMOTE", "tests/config"
        return "DOC_PROMOTE", "docs"

    return disposition, promotion_target


def validate_task_contracts(tasks: list[dict]) -> list[str]:
    errors: list[str] = []
    for idx, task in enumerate(tasks, start=1):
        disposition = task.get("disposition")
        promotion_target = task.get("promotion_target")
        outcome_class = task.get("branch_outcome_class")
        review_requirement = task.get("promotion_review_requirement")
        review_status = task.get("promotion_review_status")
        if disposition not in ALLOWED_DISPOSITIONS:
            errors.append(f"task {idx}: invalid or missing disposition '{disposition}'")
        if promotion_target not in ALLOWED_PROMOTION_TARGETS:
            errors.append(f"task {idx}: invalid or missing promotion_target '{promotion_target}'")
        if outcome_class not in ALLOWED_BRANCH_OUTCOME_CLASSES:
            errors.append(f"task {idx}: invalid or missing branch_outcome_class '{outcome_class}'")
        if review_requirement not in ALLOWED_PROMOTION_REVIEW_REQUIREMENTS:
            errors.append(f"task {idx}: invalid or missing promotion_review_requirement '{review_requirement}'")
        if review_status not in ALLOWED_PROMOTION_REVIEW_STATUSES:
            errors.append(f"task {idx}: invalid or missing promotion_review_status '{review_status}'")
        if review_requirement == "not-required" and review_status != "not-required":
            errors.append(f"task {idx}: promotion_review_status must be 'not-required' when review is not required")
        if review_requirement == "human-review" and review_status == "not-required":
            errors.append(f"task {idx}: human-review targets may not use review_status 'not-required'")
    return errors



def _lux_nyx_shape(text: str, section: str, root: Path = ROOT) -> dict | None:
    """Run the Lux–Nyx Phase 3 combined shaping and routing pipeline.

    Lazy import so the orchestrator degrades gracefully if nfem_suite is absent.
    Returns a serialisable dict of the combined shaping and routing fields,
    or None on any error.
    """
    try:
        from nfem_suite.intelligence.narrative_invariants.lux_nyx_pilot import (
            shape_and_route,
        )
        outcome = shape_and_route(text, section, root)

        return {
            "action": outcome.recommendation.action,
            "destination": outcome.governance.destination,
            "rationale": outcome.governance.rationale,
            "recommended_nyx_ops": list(outcome.recommendation.recommended_nyx_ops),
            "shadow_artifact_type": outcome.recommendation.shadow_artifact_type,
            "trace_note": outcome.governance.trace_note,
            "shadow_artifact_path": str(outcome.shadow_path.relative_to(root)),
            "governance_artifact_path": str(outcome.governance.artifact_path.relative_to(root)),
        }
    except Exception:
        return None


def task_contract(item: TodoItem, cfg: dict) -> dict:
    lane = "sandy-builder"
    if "document" in item.text.lower() or "claim tier" in item.text.lower():
        lane = "sandy-planner"
    if "test" in item.text.lower() or "falsification" in item.text.lower() or "verify" in item.text.lower():
        lane = "sandy-verifier"

    capability_lane = capability_lane_for_item(item)
    disposition, promotion_target = infer_disposition_and_promotion_target(item)
    lux_nyx = _lux_nyx_shape(item.text, item.section)
    disposition, promotion_target = apply_lux_nyx_governance_routing(item, disposition, promotion_target, lux_nyx)
    outcome_class = infer_branch_outcome_class(disposition)
    promotion_review = resolve_promotion_review_policy(cfg, promotion_target, outcome_class)

    validation = resolve_validation_command(cfg, lane=lane)

    contract = {
        "lane": lane,
        "capability_lane": capability_lane,
        "goal": item.text,
        "section": item.section,
        "disposition": disposition,
        "promotion_target": promotion_target,
        "branch_outcome_class": outcome_class,
        "promotion_review_requirement": promotion_review["requirement"],
        "promotion_review_status": promotion_review["status"],
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
        "validation_policy_ref": {
            "config": "config/orchestrator.json",
            "lane": lane,
        },
    }

    continuity_refs = continuity_artifact_ids_for_item(item)
    if continuity_refs:
        contract["memory_artifact_ids"] = continuity_refs

    continuity_ctx: dict = {}
    if capability_lane == "continuity":
        try:
            retrieval_trace = write_retrieval_trace(item.text, mode="auto", top_k=3)
        except Exception as exc:
            continuity_ctx["topological_retrieval"] = {
                "available": False,
                "mode_requested": "auto",
                "mode_used": "flat-unavailable",
                "fallback_behavior": "Workflow continues without runtime retrieval; static artifact refs remain available.",
                "error": exc.__class__.__name__,
                "authority_note": "Retrieval remains advisory only and may not self-authorize planning or governance changes.",
            }
        else:
            continuity_ctx["topological_retrieval"] = {
                "available": True,
                "mode_requested": retrieval_trace.mode_requested,
                "mode_used": retrieval_trace.mode_used,
                "baseline_mode": retrieval_trace.baseline_mode,
                "fallback_reason": retrieval_trace.fallback_reason,
                "authority_note": retrieval_trace.authority_note,
                "retrieval_trace_artifact": retrieval_trace.retrieval_trace_artifact,
                "top_results": retrieval_trace.ranked_results[:3],
            }
            if retrieval_trace.retrieval_trace_artifact:
                existing = contract.get("memory_artifact_ids", [])
                contract["memory_artifact_ids"] = existing + [retrieval_trace.retrieval_trace_artifact]

    if lux_nyx:
        contract["lux_nyx_shaping"] = {
            **{
                k: v for k, v in lux_nyx.items()
                if k not in {"shadow_artifact_path", "governance_artifact_path"}
            },
            "routing_disposition": disposition,
            "routing_promotion_target": promotion_target,
        }
        shadow_path = lux_nyx.get("shadow_artifact_path")
        if shadow_path:
            existing = contract.get("memory_artifact_ids", [])
            contract["memory_artifact_ids"] = existing + [shadow_path]

        gov_path = lux_nyx.get("governance_artifact_path")
        if gov_path:
            existing = contract.get("memory_artifact_ids", [])
            contract["memory_artifact_ids"] = existing + [gov_path]

    topological_signal = load_topological_memory_signal()
    if topological_signal:
        continuity_ctx["topological_memory_signal"] = topological_signal
    session_resume = load_session_resume_context()
    if session_resume:
        continuity_ctx["session_resume"] = session_resume
    if continuity_ctx:
        contract["continuity_context"] = continuity_ctx
    if contract.get("memory_artifact_ids"):
        deduped: list[str] = []
        seen: set[str] = set()
        for ref in contract["memory_artifact_ids"]:
            if ref in seen:
                continue
            seen.add(ref)
            deduped.append(ref)
        contract["memory_artifact_ids"] = deduped

    return contract


def write_jsonl(path: Path, tasks: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for t in tasks:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")


def write_summary(
    path: Path,
    selected: List[TodoItem],
    git_lines: list[str],
    plan_path: Path,
    cfg: dict,
    *,
    task_contracts: List[dict] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    topological_signal = load_topological_memory_signal()
    lines = [
        f"# Orchestrator Cycle Summary ({now()})",
        "",
        "## Selected tasks",
    ]
    if selected:
        for i, it in enumerate(selected, 1):
            cap = capability_lane_for_item(it)
            contract = None
            if task_contracts and i - 1 < len(task_contracts):
                candidate = task_contracts[i - 1]
                if isinstance(candidate, dict):
                    contract = candidate

            if contract:
                disposition = str(contract.get("disposition", "")).strip()
                promotion_target = str(contract.get("promotion_target", "")).strip()
                outcome_class = str(contract.get("branch_outcome_class", "")).strip()
                if not disposition or not promotion_target:
                    disposition, promotion_target = infer_disposition_and_promotion_target(it)
                if not outcome_class:
                    outcome_class = infer_branch_outcome_class(disposition)
                promotion_review = {
                    "requirement": str(contract.get("promotion_review_requirement", "")).strip(),
                    "status": str(contract.get("promotion_review_status", "")).strip(),
                }
                if not promotion_review["requirement"] or not promotion_review["status"]:
                    promotion_review = resolve_promotion_review_policy(cfg, promotion_target, outcome_class)
            else:
                disposition, promotion_target = infer_disposition_and_promotion_target(it)
                outcome_class = infer_branch_outcome_class(disposition)
                promotion_review = resolve_promotion_review_policy(cfg, promotion_target, outcome_class)

            review_text = f"review={promotion_review['requirement']}/{promotion_review['status']}"
            continuity_text = ""
            if cap == "continuity" and topological_signal:
                continuity_text = (
                    f" · topology_hit={topological_signal['topology_hit_rate']:.3f}"
                    f" · topology_mrr={topological_signal['topology_mrr']:.3f}"
                )
            lines.append(
                f"{i}. [{it.state}] {it.text} ({it.section}) · lane={cap} · disposition={disposition} · target={promotion_target} · outcome={outcome_class} · {review_text}{continuity_text}"
            )
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
    tasks = [task_contract(it, cfg=cfg) for it in selected]
    task_errors = validate_task_contracts(tasks)
    if task_errors:
        print("Invalid orchestrator task contracts:")
        for err in task_errors:
            print(f"- {err}")
        return 1

    out_plan = repo / cfg["output"]["taskPlanJsonl"]
    out_summary = repo / cfg["output"]["cycleSummary"]

    write_jsonl(out_plan, tasks)
    write_summary(
        out_summary,
        selected,
        git_status_short(repo),
        out_plan,
        cfg,
        task_contracts=tasks,
    )

    print(f"Prepared {len(tasks)} task contracts -> {out_plan}")
    print(f"Summary -> {out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
