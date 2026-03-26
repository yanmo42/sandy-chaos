"""Normalization helpers for Symbolic Maps records."""

from __future__ import annotations

from dataclasses import replace

from .symbolic_maps import SymbolicOperatorRecord

_OPERATOR_CANONICAL_MAP = {
    "boundary suprema": "boundary supremacy",
    "frame-escape": "frame escape",
    "capability absorbtion": "capability absorption",
    "benevolent sovereignity": "benevolent sovereignty",
}


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def _normalize_operator(value: str) -> str:
    normalized = _normalize_text(value).lower()
    return _OPERATOR_CANONICAL_MAP.get(normalized, normalized)


def normalize_record(record: SymbolicOperatorRecord) -> SymbolicOperatorRecord:
    signature_operators = sorted({_normalize_operator(op) for op in record.signature_operators})
    failure_modes = sorted({_normalize_text(mode) for mode in record.failure_modes})
    composable_with = sorted({_normalize_text(name) for name in record.composable_with})
    excluded_domains = sorted({_normalize_text(name) for name in record.excluded_domains})

    return replace(
        record,
        source_object=_normalize_text(record.source_object),
        source_domain=_normalize_text(record.source_domain),
        narrative_role=_normalize_text(record.narrative_role),
        core_fantasy=_normalize_text(record.core_fantasy),
        signature_operators=signature_operators,
        constraint_pattern=_normalize_text(record.constraint_pattern),
        failure_modes=failure_modes,
        composable_with=composable_with,
        excluded_domains=excluded_domains,
        confidence_tier=record.confidence_tier.strip().lower(),
        notes=_normalize_text(record.notes),
    )


def normalize_records(records: list[SymbolicOperatorRecord]) -> list[SymbolicOperatorRecord]:
    return [normalize_record(record) for record in records]
