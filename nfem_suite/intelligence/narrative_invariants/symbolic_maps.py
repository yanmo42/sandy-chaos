"""Minimal scaffolding for symbolic operator extraction artifacts.

This module provides a small typed record format for early Symbolic Maps work.
The goal is not to automate full extraction yet, but to define a stable surface
for records that can later be produced by manual curation or model-assisted
pipelines.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SymbolicOperatorRecord:
    source_object: str
    source_domain: str
    narrative_role: str
    core_fantasy: str
    signature_operators: list[str]
    constraint_pattern: str
    failure_modes: list[str]
    composable_with: list[str]
    excluded_domains: list[str]
    confidence_tier: str
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SymbolicOperatorRecord":
        return cls(
            source_object=data["source_object"],
            source_domain=data["source_domain"],
            narrative_role=data["narrative_role"],
            core_fantasy=data["core_fantasy"],
            signature_operators=list(data["signature_operators"]),
            constraint_pattern=data["constraint_pattern"],
            failure_modes=list(data["failure_modes"]),
            composable_with=list(data["composable_with"]),
            excluded_domains=list(data["excluded_domains"]),
            confidence_tier=data["confidence_tier"],
            notes=data.get("notes", ""),
        )


def load_symbolic_records(path: str | Path) -> list[SymbolicOperatorRecord]:
    data = json.loads(Path(path).read_text())
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of symbolic operator records")
    return [SymbolicOperatorRecord.from_dict(item) for item in data]
