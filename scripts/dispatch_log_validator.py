"""Small invariant checks for orchestrator dispatch-log entries."""

from __future__ import annotations


def _is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_dispatch_log_entry(entry: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(entry, dict):
        return ["invalid dispatch-log payload"]

    control_mode = str(entry.get("control_mode", "")).strip().lower()
    if control_mode == "control-affecting" and not _is_nonempty_string(entry.get("governance_policy_ref")):
        errors.append("control-affecting events require governance_policy_ref")

    raw_artifact_ids = entry.get("memory_artifact_ids")
    artifact_ids: list[str] = []
    if raw_artifact_ids is not None:
        if not isinstance(raw_artifact_ids, list):
            errors.append("memory_artifact_ids must be a list of strings")
        else:
            invalid_items = [item for item in raw_artifact_ids if not _is_nonempty_string(item)]
            if invalid_items:
                errors.append("memory_artifact_ids must be a list of strings")
            else:
                artifact_ids = [item.strip() for item in raw_artifact_ids]

    continuity_relevant = bool(entry.get("continuity_relevant", False))
    memory_consulted = bool(entry.get("memory_consulted", False))
    memory_policy_ref_present = _is_nonempty_string(entry.get("memory_policy_ref"))
    memory_membrane_relevant = continuity_relevant or memory_consulted

    if not memory_consulted and artifact_ids:
        errors.append("memory_consulted=false requires empty memory_artifact_ids")
    if memory_consulted and not artifact_ids:
        errors.append("memory_consulted=true requires memory_artifact_ids")

    if memory_policy_ref_present and not memory_membrane_relevant:
        errors.append("memory_policy_ref may only appear when continuity/memory membrane is relevant")
    if memory_membrane_relevant and not memory_policy_ref_present:
        errors.append("continuity/memory membrane events require memory_policy_ref")

    return errors
