"""Small invariant checks for orchestrator dispatch-log entries."""

from __future__ import annotations


ALLOWED_CONTROL_MODES = {"control-affecting", "descriptive"}
GOVERNANCE_POLICY_REF = "spine/membranes/governance-runtime-v1.yaml"
MEMORY_POLICY_REF = "spine/membranes/memory-dispatch-v1.yaml"


def _is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_bool(value: object) -> bool:
    return isinstance(value, bool)


def validate_dispatch_log_entry(entry: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(entry, dict):
        return ["invalid dispatch-log payload"]

    control_mode = str(entry.get("control_mode", "")).strip().lower()
    if control_mode and control_mode not in ALLOWED_CONTROL_MODES:
        errors.append(f"invalid control_mode '{control_mode}'")
    if control_mode == "control-affecting" and not _is_nonempty_string(entry.get("governance_policy_ref")):
        errors.append("control-affecting events require governance_policy_ref")
    governance_policy_ref = entry.get("governance_policy_ref")
    if governance_policy_ref is not None:
        if not _is_nonempty_string(governance_policy_ref):
            errors.append("governance_policy_ref must be a non-empty string")
        elif str(governance_policy_ref).strip() != GOVERNANCE_POLICY_REF:
            errors.append(f"governance_policy_ref must equal {GOVERNANCE_POLICY_REF}")

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
                if len(set(artifact_ids)) != len(artifact_ids):
                    errors.append("memory_artifact_ids must not contain duplicates")

    if "continuity_relevant" in entry and not _is_bool(entry.get("continuity_relevant")):
        errors.append("continuity_relevant must be boolean")
    if "memory_consulted" in entry and not _is_bool(entry.get("memory_consulted")):
        errors.append("memory_consulted must be boolean")

    continuity_relevant = bool(entry.get("continuity_relevant", False))
    memory_consulted = bool(entry.get("memory_consulted", False))
    memory_policy_ref_present = _is_nonempty_string(entry.get("memory_policy_ref"))
    if entry.get("memory_policy_ref") is not None and not memory_policy_ref_present:
        errors.append("memory_policy_ref must be a non-empty string")
    if memory_policy_ref_present and str(entry.get("memory_policy_ref")).strip() != MEMORY_POLICY_REF:
        errors.append(f"memory_policy_ref must equal {MEMORY_POLICY_REF}")

    request_provenance_present = _is_nonempty_string(entry.get("memory_request_provenance"))
    if entry.get("memory_request_provenance") is not None and not request_provenance_present:
        errors.append("memory_request_provenance must be a non-empty string")

    memory_membrane_relevant = continuity_relevant or memory_consulted

    if not memory_consulted and artifact_ids:
        errors.append("memory_consulted=false requires empty memory_artifact_ids")
    if memory_consulted and not artifact_ids:
        errors.append("memory_consulted=true requires memory_artifact_ids")

    if memory_policy_ref_present and not memory_membrane_relevant:
        errors.append("memory_policy_ref may only appear when continuity/memory membrane is relevant")
    if memory_membrane_relevant and not memory_policy_ref_present:
        errors.append("continuity/memory membrane events require memory_policy_ref")
    if request_provenance_present and not memory_membrane_relevant:
        errors.append("memory_request_provenance may only appear when continuity/memory membrane is relevant")
    if memory_membrane_relevant and not request_provenance_present:
        errors.append("continuity/memory membrane events require memory_request_provenance")

    return errors
