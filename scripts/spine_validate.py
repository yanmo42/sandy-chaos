#!/usr/bin/env python3
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any
import sys

try:
    from scripts import spine_common
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts import spine_common


def _loc(item: spine_common.LoadedItem) -> str:
    try:
        rel = item.path.relative_to(spine_common.ROOT)
    except ValueError:
        rel = item.path
    if item.line is not None:
        return f"{rel}:line {item.line}"
    return str(rel)


def _require_fields(item: spine_common.LoadedItem, required: set[str], errors: list[str]) -> None:
    missing = sorted(field for field in required if field not in item.data)
    if missing:
        errors.append(f"{_loc(item)}: missing required field(s): {', '.join(missing)}")


def _require_non_empty_string(item: spine_common.LoadedItem, field: str, errors: list[str]) -> None:
    value = item.data.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{_loc(item)}: field '{field}' must be a non-empty string")


def _require_list(item: spine_common.LoadedItem, field: str, errors: list[str], min_items: int = 0) -> None:
    value = item.data.get(field)
    if not isinstance(value, list):
        errors.append(f"{_loc(item)}: field '{field}' must be a list")
        return
    if len(value) < min_items:
        errors.append(f"{_loc(item)}: field '{field}' must contain at least {min_items} item(s)")


def _require_enum(item: spine_common.LoadedItem, field: str, allowed: set[str], errors: list[str]) -> None:
    value = item.data.get(field)
    if value not in allowed:
        errors.append(f"{_loc(item)}: invalid {field} '{value}'")


def _check_id(item: spine_common.LoadedItem, field: str, regex, errors: list[str]) -> str | None:
    value = item.data.get(field)
    if not isinstance(value, str) or not regex.match(value):
        errors.append(f"{_loc(item)}: invalid {field} '{value}'")
        return None
    return value


def _check_duplicate_ids(seen: dict[str, str], identifier: str, location: str, errors: list[str]) -> None:
    prior = seen.get(identifier)
    if prior:
        errors.append(f"{location}: duplicate id '{identifier}' (already seen at {prior})")
    else:
        seen[identifier] = location


def validate_concepts(concepts: list[spine_common.LoadedItem], errors: list[str], warnings: list[str]) -> set[str]:
    seen: dict[str, str] = {}
    concept_ids: set[str] = set()

    for item in concepts:
        _require_fields(item, spine_common.CONCEPT_REQUIRED, errors)
        identifier = _check_id(item, "id", spine_common.CONCEPT_ID_RE, errors)
        if identifier:
            _check_duplicate_ids(seen, identifier, _loc(item), errors)
            concept_ids.add(identifier)

        _require_non_empty_string(item, "name", errors)
        _require_non_empty_string(item, "summary", errors)
        _require_non_empty_string(item, "next_action", errors)
        _require_enum(item, "lane", spine_common.ALLOWED_LANES, errors)
        _require_enum(item, "claim_tier", spine_common.ALLOWED_TIERS, errors)
        _require_enum(item, "status", spine_common.ALLOWED_STATUS, errors)
        _require_enum(item, "promotion_target", spine_common.ALLOWED_PROMOTION_TARGETS, errors)
        _require_enum(item, "owner_surface", spine_common.ALLOWED_OWNER_SURFACES, errors)

        for field in ("depends_on", "documented_in", "implemented_in", "tested_by", "contradicts", "failure_conditions"):
            _require_list(item, field, errors, min_items=1 if field == "failure_conditions" else 0)

        if "missing_assumptions" in item.data:
            _require_list(item, "missing_assumptions", errors, min_items=0)

        if item.data.get("next_test") is not None:
            _require_non_empty_string(item, "next_test", errors)

        if item.data.get("status") == "canonical" and not item.data.get("documented_in"):
            warnings.append(f"{_loc(item)}: canonical concept has no documented_in links")
        if not item.data.get("tested_by"):
            warnings.append(f"{_loc(item)}: concept has no tested_by links")
        if item.data.get("status") in {"draft", "pressure-testing", "validated-partial"} and not item.data.get("next_test"):
            warnings.append(f"{_loc(item)}: active concept has no next_test field")
        if item.data.get("owner_surface") == "ygg-candidate" and not str(item.data.get("promotion_target", "")).startswith("ygg"):
            warnings.append(f"{_loc(item)}: ygg-candidate should usually target a Ygg promotion surface")

    return concept_ids


def validate_concept_references(concepts: list[spine_common.LoadedItem], concept_ids: set[str], errors: list[str]) -> None:
    for item in concepts:
        for field in ("depends_on", "contradicts"):
            for ref in item.data.get(field, []):
                if ref not in concept_ids:
                    errors.append(f"{_loc(item)}: {field} references missing concept '{ref}'")


def validate_pressure_events(events: list[spine_common.LoadedItem], concept_ids: set[str], errors: list[str], warnings: list[str]) -> set[str]:
    seen: dict[str, str] = {}
    event_ids: set[str] = set()

    for item in events:
        _require_fields(item, spine_common.PRESSURE_REQUIRED, errors)
        identifier = _check_id(item, "id", spine_common.PRESSURE_ID_RE, errors)
        if identifier:
            _check_duplicate_ids(seen, identifier, _loc(item), errors)
            event_ids.add(identifier)

        date = item.data.get("date")
        if not isinstance(date, str) or not spine_common.DATE_RE.match(date):
            errors.append(f"{_loc(item)}: invalid date '{date}'")

        _require_non_empty_string(item, "summary", errors)
        _require_non_empty_string(item, "next_action", errors)
        _require_enum(item, "kind", spine_common.ALLOWED_PRESSURE_KINDS, errors)
        _require_enum(item, "result", spine_common.ALLOWED_PRESSURE_RESULTS, errors)
        _require_enum(item, "disposition", spine_common.ALLOWED_PRESSURE_DISPOSITIONS, errors)
        _require_list(item, "concepts", errors, min_items=1)
        _require_list(item, "evidence", errors, min_items=1)

        for ref in item.data.get("concepts", []):
            if ref not in concept_ids:
                errors.append(f"{_loc(item)}: references missing concept '{ref}'")
        if item.data.get("result") == "support" and item.data.get("disposition") == "WAITING_ON_EVIDENCE":
            warnings.append(f"{_loc(item)}: support result paired with WAITING_ON_EVIDENCE looks inconsistent")

    return event_ids


def validate_promotion_events(events: list[spine_common.LoadedItem], concept_ids: set[str], errors: list[str], warnings: list[str]) -> set[str]:
    seen: dict[str, str] = {}
    event_ids: set[str] = set()

    for item in events:
        if "__parse_error__" in item.data:
            errors.append(f"{_loc(item)}: {item.data['__parse_error__']}")
            continue

        _require_fields(item, spine_common.PROMOTION_REQUIRED, errors)
        identifier = _check_id(item, "id", spine_common.PROMOTION_ID_RE, errors)
        if identifier:
            _check_duplicate_ids(seen, identifier, _loc(item), errors)
            event_ids.add(identifier)

        date = item.data.get("date")
        if not isinstance(date, str) or not spine_common.DATE_RE.match(date):
            errors.append(f"{_loc(item)}: invalid date '{date}'")

        _require_non_empty_string(item, "basis", errors)
        _require_enum(item, "from_status", spine_common.ALLOWED_STATUS, errors)
        _require_enum(item, "to_status", spine_common.ALLOWED_STATUS, errors)
        _require_enum(item, "promotion_target", spine_common.ALLOWED_PROMOTION_TARGETS, errors)
        _require_enum(item, "disposition", spine_common.ALLOWED_PROMOTION_DISPOSITIONS, errors)
        _require_list(item, "concepts", errors, min_items=1)

        for ref in item.data.get("concepts", []):
            if ref not in concept_ids:
                errors.append(f"{_loc(item)}: references missing concept '{ref}'")
        if item.data.get("from_status") == item.data.get("to_status"):
            warnings.append(f"{_loc(item)}: from_status and to_status are identical")

    return event_ids


def build_warning_index(events: list[spine_common.LoadedItem], field: str) -> dict[str, list[spine_common.LoadedItem]]:
    index: dict[str, list[spine_common.LoadedItem]] = defaultdict(list)
    for item in events:
        for ref in item.data.get(field, []):
            index[ref].append(item)
    return index


def _path_exists(path_text: str) -> bool:
    token = str(path_text).strip().split()[0]
    if not token:
        return False
    return (spine_common.ROOT / token).exists()


def validate_membranes(membranes: list[spine_common.LoadedItem], errors: list[str], warnings: list[str]) -> set[str]:
    seen: dict[str, str] = {}
    membrane_ids: set[str] = set()

    for item in membranes:
        _require_fields(item, spine_common.MEMBRANE_REQUIRED, errors)
        identifier = _check_id(item, "membrane_id", spine_common.MEMBRANE_ID_RE, errors)
        if identifier:
            _check_duplicate_ids(seen, identifier, _loc(item), errors)
            membrane_ids.add(identifier)

        _require_list(item, "between_layers", errors, min_items=2)
        for field in ("allowed_flows", "forbidden_flows", "required_evidence", "authority_limits", "artifacts_emitted", "governed_by"):
            _require_list(item, field, errors, min_items=1)

        for field in ("purpose", "failure_mode", "notes"):
            _require_non_empty_string(item, field, errors)

        for layer in item.data.get("between_layers", []):
            if layer not in spine_common.ALLOWED_HOST_LAYERS:
                errors.append(f"{_loc(item)}: invalid between_layers entry '{layer}'")

        if len(item.data.get("between_layers", [])) != len(set(item.data.get("between_layers", []))):
            errors.append(f"{_loc(item)}: between_layers contains duplicates")

        for ref in item.data.get("governed_by", []):
            ref_text = str(ref).strip()
            if "/" in ref_text and not _path_exists(ref_text):
                errors.append(f"{_loc(item)}: governed_by references missing file '{ref_text}'")

        if not item.data.get("notes"):
            warnings.append(f"{_loc(item)}: membrane has no notes")

    return membrane_ids


HOST_LAYER_TO_REPO_LANE = {
    "interpretive": "theory",
    "memory": "continuity",
    "circulatory": "ops",
    "experimental": "simulation",
    "governance": "validation",
}


def validate_subsystems(
    subsystems: list[spine_common.LoadedItem],
    membrane_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> set[str]:
    seen: dict[str, str] = {}
    subsystem_ids: set[str] = set()

    for item in subsystems:
        _require_fields(item, spine_common.SUBSYSTEM_REQUIRED, errors)
        identifier = _check_id(item, "subsystem_id", spine_common.SUBSYSTEM_ID_RE, errors)
        if identifier:
            _check_duplicate_ids(seen, identifier, _loc(item), errors)
            subsystem_ids.add(identifier)

        for field in (
            "name",
            "host_function",
            "purpose",
            "promotion_relevance",
            "failure_if_removed",
            "notes",
        ):
            _require_non_empty_string(item, field, errors)

        _require_enum(item, "status", spine_common.ALLOWED_SUBSYSTEM_STATUS, errors)
        _require_enum(item, "authority_class", spine_common.ALLOWED_AUTHORITY_CLASSES, errors)
        _require_enum(item, "host_layer", spine_common.ALLOWED_HOST_LAYERS, errors)
        _require_enum(item, "repo_lane", spine_common.ALLOWED_REPO_LANES, errors)
        _require_enum(item, "workflow_participation", spine_common.ALLOWED_WORKFLOW_PARTICIPATION, errors)
        _require_enum(item, "interface_clarity", spine_common.ALLOWED_INTERFACE_CLARITY, errors)
        _require_enum(item, "evidence_maturity", spine_common.ALLOWED_EVIDENCE_MATURITY, errors)
        _require_enum(item, "bounded_influence", spine_common.ALLOWED_BOUNDED_INFLUENCE, errors)
        _require_enum(item, "removal_impact", spine_common.ALLOWED_REMOVAL_IMPACT, errors)

        for field in (
            "non_goals",
            "inputs",
            "outputs",
            "upstream_dependencies",
            "downstream_consumers",
            "governed_by",
            "claim_classes_supported",
            "evidence_classes_produced",
            "main_risks",
            "membrane_contracts",
            "source_docs",
        ):
            _require_list(item, field, errors, min_items=1)

        for claim_class in item.data.get("claim_classes_supported", []):
            if claim_class not in spine_common.ALLOWED_CLAIM_CLASSES:
                errors.append(f"{_loc(item)}: invalid claim_classes_supported entry '{claim_class}'")

        for membrane_id in item.data.get("membrane_contracts", []):
            if membrane_id not in membrane_ids:
                errors.append(f"{_loc(item)}: references missing membrane '{membrane_id}'")

        for source_doc in item.data.get("source_docs", []):
            source_text = str(source_doc).strip()
            if source_text and not _path_exists(source_text):
                errors.append(f"{_loc(item)}: source_docs references missing file '{source_text}'")

        expected_lane = HOST_LAYER_TO_REPO_LANE.get(item.data.get("host_layer"))
        actual_lane = item.data.get("repo_lane")
        if expected_lane and actual_lane and expected_lane != actual_lane:
            errors.append(
                f"{_loc(item)}: repo_lane '{actual_lane}' is inconsistent with host_layer '{item.data.get('host_layer')}' "
                f"(expected '{expected_lane}')"
            )

        if item.data.get("status") == "canonical" and item.data.get("workflow_participation") != "standard":
            warnings.append(f"{_loc(item)}: canonical subsystem should usually have standard workflow participation")
        if item.data.get("bounded_influence") != "explicit":
            warnings.append(f"{_loc(item)}: subsystem influence is not yet explicit")

    return subsystem_ids


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    concepts = spine_common.load_concepts()
    pressure_events = spine_common.load_pressure_events()
    promotion_events = spine_common.load_promotion_events()
    membranes = spine_common.load_membranes()
    subsystems = spine_common.load_subsystems()

    concept_ids = validate_concepts(concepts, errors, warnings)
    validate_concept_references(concepts, concept_ids, errors)
    validate_pressure_events(pressure_events, concept_ids, errors, warnings)
    validate_promotion_events(promotion_events, concept_ids, errors, warnings)
    membrane_ids = validate_membranes(membranes, errors, warnings)
    validate_subsystems(subsystems, membrane_ids, errors, warnings)

    pressure_by_concept = build_warning_index(pressure_events, "concepts")
    for item in concepts:
        concept_id = item.data.get("id")
        if concept_id and concept_id not in pressure_by_concept:
            warnings.append(f"{_loc(item)}: concept has no linked pressure events")

    if errors:
        print("Spine validation failed.")
        print()
        print("ERRORS")
        for err in errors:
            print(f"- {err}")
        if warnings:
            print()
            print("WARNINGS")
            for warning in warnings:
                print(f"- {warning}")
        return 1

    print("Spine validation passed.")
    print(f"- {len(concepts)} concepts")
    print(f"- {len(pressure_events)} pressure events")
    print(f"- {len(promotion_events)} promotion events")
    print(f"- {len(membranes)} membranes")
    print(f"- {len(subsystems)} subsystems")
    print(f"- {len(errors)} errors")
    print(f"- {len(warnings)} warnings")
    if warnings:
        print()
        print("WARNINGS")
        for warning in warnings:
            print(f"- {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
