"""Small invariant checks for orchestrator dispatch-log entries."""

from __future__ import annotations


ALLOWED_CONTROL_MODES = {"control-affecting", "descriptive"}
ALLOWED_MEMORY_PROVENANCE_SOURCES = {
    "request.memory_artifact_ids",
    "prompt_context.memory_artifact_ids",
    "prompt_context.continuity_artifact_ids",
    "prompt_context.capability_lane",
}
GOVERNANCE_POLICY_REF = "spine/membranes/governance-runtime-v1.yaml"
MEMORY_POLICY_REF = "spine/membranes/memory-dispatch-v1.yaml"


def _is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_bool(value: object) -> bool:
    return isinstance(value, bool)


def _is_inspectable_artifact_ref(value: object) -> bool:
    if not _is_nonempty_string(value):
        return False
    text = str(value).strip()
    if text.startswith("/") or text.startswith("../") or "/../" in text:
        return False
    base, _, _fragment = text.partition("#")
    return bool(base) and "/" in base


def _parse_memory_request_provenance(value: object) -> tuple[str, str] | None:
    if not _is_nonempty_string(value):
        return None
    request_id, sep, source = str(value).strip().partition(":")
    if not sep or not request_id or not source:
        return None
    return request_id, source


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
                invalid_refs = [item for item in artifact_ids if not _is_inspectable_artifact_ref(item)]
                if invalid_refs:
                    errors.append("memory_artifact_ids must contain inspectable repo-relative artifact refs")

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

    request_provenance = _parse_memory_request_provenance(entry.get("memory_request_provenance"))
    request_provenance_present = request_provenance is not None
    if entry.get("memory_request_provenance") is not None and not request_provenance_present:
        errors.append("memory_request_provenance must be formatted as <request-id>:<source>")
    if request_provenance_present:
        _, request_source = request_provenance
        if request_source not in ALLOWED_MEMORY_PROVENANCE_SOURCES:
            errors.append("memory_request_provenance source is not allowed")

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
    if memory_consulted and request_provenance_present and request_provenance[1] == "prompt_context.capability_lane":
        errors.append("memory_consulted=true requires memory_request_provenance to cite artifact-bearing evidence")

    return errors
