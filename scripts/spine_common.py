from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPINE_DIR = ROOT / "spine"
CONCEPT_DIR = SPINE_DIR / "concepts"
PRESSURE_DIR = SPINE_DIR / "pressure"
PROMOTION_LEDGER = SPINE_DIR / "promotions" / "ledger.jsonl"

CONCEPT_ID_RE = re.compile(r"^SC-CONCEPT-[0-9]{4}$")
PRESSURE_ID_RE = re.compile(r"^SC-PRESSURE-[0-9]{8}-[0-9]{2}$")
PROMOTION_ID_RE = re.compile(r"^SC-PROMOTE-[0-9]{8}-[0-9]{2}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ALLOWED_LANES = {"theory", "simulation", "formalization", "automation", "continuity", "interface", "neuro"}
ALLOWED_TIERS = {"defensible", "plausible", "speculative"}
ALLOWED_STATUS = {"seed", "draft", "pressure-testing", "validated-partial", "canonical", "archived", "deprecated", "killed"}
ALLOWED_PROMOTION_TARGETS = {"docs/canonical", "docs/archive", "code/core", "code/experiment", "tests", "workflow", "config", "memory-only", "public-site", "ygg-bridge", "ygg-native-candidate"}
ALLOWED_OWNER_SURFACES = {"sandy-chaos", "shared-with-ygg", "ygg-candidate"}
ALLOWED_PRESSURE_KINDS = {"doc-critique", "toy-model-evaluation", "simulation-run", "test-review", "architecture-review", "promotion-review", "literature-pressure", "workflow-review"}
ALLOWED_PRESSURE_RESULTS = {"support", "partial-support", "contradiction", "insufficient-evidence", "refinement-needed"}
ALLOWED_PRESSURE_DISPOSITIONS = {"KEEP_EXPLORING", "REVISE", "ARCHIVE", "DOC_PROMOTE", "CODE_PROMOTE", "TEST_PROMOTE", "MERGE_INTO_EXISTING", "YGG_BRIDGE", "NEEDS_FALSIFICATION", "WAITING_ON_EVIDENCE", "KILL"}
ALLOWED_PROMOTION_DISPOSITIONS = {"DOC_PROMOTE", "CODE_PROMOTE", "TEST_PROMOTE", "ARCHIVE", "MERGE_INTO_EXISTING", "YGG_BRIDGE", "KILL"}

CONCEPT_REQUIRED = {"id", "name", "summary", "lane", "claim_tier", "status", "failure_conditions", "next_action", "promotion_target", "owner_surface"}
PRESSURE_REQUIRED = {"id", "date", "concepts", "kind", "summary", "result", "disposition", "evidence", "next_action"}
PROMOTION_REQUIRED = {"id", "date", "concepts", "from_status", "to_status", "promotion_target", "basis", "disposition"}

LIST_FIELDS = {
    "tags",
    "depends_on",
    "documented_in",
    "implemented_in",
    "tested_by",
    "contradicts",
    "failure_conditions",
    "missing_assumptions",
    "concepts",
    "evidence",
    "findings",
}


@dataclass
class LoadedItem:
    path: Path
    data: dict[str, Any]
    line: int | None = None


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "[]":
        return []
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        return value[1:-1]
    if value.startswith("'") and value.endswith("'") and len(value) >= 2:
        return value[1:-1]
    return value


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue

        if line.startswith("  - ") and current_key:
            existing = data.setdefault(current_key, [])
            if not isinstance(existing, list):
                existing = []
                data[current_key] = existing
            existing.append(_parse_scalar(line[4:]))
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key

        if value == "":
            data[key] = [] if key in LIST_FIELDS else ""
        else:
            data[key] = _parse_scalar(value)

    for key in LIST_FIELDS:
        if key in data and not isinstance(data[key], list):
            data[key] = [] if data[key] == "[]" else [data[key]]

    return data


def load_concepts(root: Path = ROOT) -> list[LoadedItem]:
    concept_dir = root / "spine" / "concepts"
    return [LoadedItem(path=p, data=parse_simple_yaml(p)) for p in sorted(concept_dir.glob("*.yaml"))]


def load_pressure_events(root: Path = ROOT) -> list[LoadedItem]:
    pressure_dir = root / "spine" / "pressure"
    return [LoadedItem(path=p, data=parse_simple_yaml(p)) for p in sorted(pressure_dir.glob("**/*.yaml"))]


def load_promotion_events(root: Path = ROOT) -> list[LoadedItem]:
    ledger = root / "spine" / "promotions" / "ledger.jsonl"
    items: list[LoadedItem] = []
    if not ledger.exists():
        return items
    for idx, line in enumerate(ledger.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError as exc:
            data = {"__parse_error__": f"invalid JSON: {exc.msg}"}
        items.append(LoadedItem(path=ledger, data=data, line=idx))
    return items
