"""Lux–Nyx Phase 2 pilot: next-action suggestion shaping.

This module provides:
  classify_next_action(text, section) → LuxNyxInteractionRecord
      Rules-based classifier. Infers input_type, salience, risk, ambiguity,
      evidence_tier, urgency from text + section keywords.

  ShadowArtifact
      Frozen dataclass for the emitted trace record.

  write_shadow_artifact(root, artifact) → Path
      Writes the shadow artifact to state/lux_nyx/shadow/.

  shape_next_action(text, section, root) → (EvaluatorRecommendation, Path)
      Full pipeline: classify → evaluate → emit shadow artifact → return both.

Pilot surface: next-action suggestion shaping.
Contract doc reference: docs/archive/lux_nyx_interaction_contract_v0.md §Candidate pilot surfaces
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from nfem_suite.intelligence.narrative_invariants.lux_nyx_contract import (
    EvaluatorRecommendation,
    LuxNyxInteractionRecord,
    evaluate,
)

# ---------------------------------------------------------------------------
# Classifier lookup tables
# ---------------------------------------------------------------------------

_INPUT_TYPE_KEYWORDS: dict[str, set[str]] = {
    "symbolic-input": {"symbolic", "mythic", "naming", "persona", "lux", "nyx", "shadow", "myth", "ritual"},
    "push":           {"publish", "release", "ship", "escalate", "push to prod", "push to main", "go live"},
    "claim":          {"claim", "canon", "canonize", "promote to canon", "prove", "falsif", "assert"},
    "signal":         {"alert", "notification", "event", "anomaly", "detected", "triggered", "webhook"},
    "route-request":  {"where should", "which lane", "route this", "belongs in", "assign to"},
    "spark":          {"explore", "what if", "consider", "maybe we", "idea:", "could we", "brainstorm"},
}

_SALIENCE_HIGH_KEYWORDS = {
    "continuity", "core", "sprint", "critical", "governance", "p0", "blocker",
    "convergence", "anchor", "retrodiction", "membrane",
}
_SALIENCE_MEDIUM_KEYWORDS = {
    "ops", "validation", "docs", "research", "maintenance", "cleanup",
}

_HIGH_RISK_KEYWORDS = {
    "canon", "canonical", "publish", "release", "merge main", "promote to docs",
    "promote to canon", "production", "public", "consequential",
}
_MEDIUM_RISK_KEYWORDS = {
    "test", "verify", "validate", "falsif", "config", "migration", "refactor",
    "rewrite", "rename",
}

_DEFENSIBLE_KEYWORDS = {
    "validated", "tested", "confirmed", "verified", "defensible", "proven",
}
_SPECULATIVE_KEYWORDS = {
    "speculative", "explore", "hypothesis", "maybe", "what if", "not sure",
    "rough idea", "brainstorm",
}

_URGENCY_HIGH_KEYWORDS = {
    "urgent", "asap", "blocker", "critical", "now", "immediately", "today",
}
_URGENCY_MEDIUM_KEYWORDS = {"soon", "next", "priority", "this week"}

_NYX_OPS_BY_INPUT_TYPE: dict[str, list[str]] = {
    "prompt":         ["compress", "trace"],
    "spark":          ["compress", "tier", "trace"],
    "push":           ["gate", "weight", "tier", "trace"],
    "claim":          ["gate", "weight", "tier", "trace"],
    "signal":         ["compress", "trace", "split"],
    "route-request":  ["compress", "trace", "split"],
    "symbolic-input": ["compress", "tier", "trace", "split"],
}

_SHADOW_TYPE_BY_INPUT_TYPE: dict[str, str] = {
    "prompt":         "glint",
    "spark":          "draft",
    "push":           "audit-trace",
    "claim":          "audit-trace",
    "signal":         "contour",
    "route-request":  "contour",
    "symbolic-input": "draft",
}


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

def classify_next_action(text: str, section: str = "") -> LuxNyxInteractionRecord:
    """Infer a LuxNyxInteractionRecord from raw next-action text + optional section.

    All rules are deterministic keyword lookups — no ML, no external calls.
    The record is validated before being returned.
    """
    combined = f"{section} {text}".lower()
    words = set(combined.split())

    # input_type — first keyword match wins; default to "prompt"
    input_type = "prompt"
    for itype, keywords in _INPUT_TYPE_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            input_type = itype
            break

    # salience — section-first, then text keywords
    salience = "medium"
    if any(kw in combined for kw in _SALIENCE_HIGH_KEYWORDS):
        salience = "high"
    elif any(kw in combined for kw in _SALIENCE_MEDIUM_KEYWORDS):
        salience = "medium"

    # risk — input_type drives primary assignment, text can escalate
    if input_type in {"push", "claim"} or any(kw in combined for kw in _HIGH_RISK_KEYWORDS):
        risk = "high"
    elif any(kw in combined for kw in _MEDIUM_RISK_KEYWORDS):
        risk = "medium"
    else:
        risk = "low"

    # ambiguity — short/vague text → high; specific/actionable → low
    word_count = len(text.split())
    vague = any(kw in combined for kw in {"?", "explore", "what if", "maybe", "not sure"})
    if word_count < 5 or vague:
        ambiguity = "high"
    elif word_count > 10 and input_type in {"prompt", "signal"} and not vague:
        ambiguity = "low"
    else:
        ambiguity = "medium"

    # evidence_tier
    if any(kw in combined for kw in _DEFENSIBLE_KEYWORDS):
        evidence_tier = "defensible"
    elif any(kw in combined for kw in _SPECULATIVE_KEYWORDS):
        evidence_tier = "speculative"
    else:
        evidence_tier = "plausible"

    # urgency
    if any(kw in combined for kw in _URGENCY_HIGH_KEYWORDS):
        urgency = "high"
    elif any(kw in combined for kw in _URGENCY_MEDIUM_KEYWORDS):
        urgency = "medium"
    else:
        urgency = "low"

    nyx_ops = _NYX_OPS_BY_INPUT_TYPE.get(input_type, ["compress", "trace"])
    shadow_type = _SHADOW_TYPE_BY_INPUT_TYPE.get(input_type, "glint")

    return LuxNyxInteractionRecord(
        input_type=input_type,
        input_description=text[:200].strip(),
        salience=salience,
        ambiguity=ambiguity,
        risk=risk,
        evidence_tier=evidence_tier,
        urgency=urgency,
        privacy_level="internal",
        allowed_nyx_ops=nyx_ops,
        shadow_artifact_type=shadow_type,
        shadow_artifact_summary=f"Shaped next-action: {text[:80].strip()}",
        promotion_condition="action accepted or lightly edited across repeated interactions",
        failure_condition="shaping increases correction burden or latency-to-useful-action",
        trace_requirements=["input_type classification", "chosen nyx ops", "evaluator action"],
    )


# ---------------------------------------------------------------------------
# Shadow artifact
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ShadowArtifact:
    """Emitted trace record from a Lux–Nyx shaping pass.

    Written to state/lux_nyx/shadow/ — durable record of every shaping decision.
    """

    timestamp: str
    source_text: str
    section: str
    input_type: str
    evaluator_action: str
    recommended_nyx_ops: tuple[str, ...]
    shadow_artifact_type: str
    rationale: str
    trace_note: str

    def to_dict(self) -> dict:
        d = asdict(self)
        d["recommended_nyx_ops"] = list(self.recommended_nyx_ops)
        return d


def write_shadow_artifact(root: str | Path, artifact: ShadowArtifact) -> Path:
    """Write a shadow artifact JSON file under state/lux_nyx/shadow/."""
    out_dir = Path(root) / "state" / "lux_nyx" / "shadow"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = artifact.timestamp.replace(":", "-")
    type_slug = re.sub(r"[^a-z0-9]+", "-", artifact.input_type.lower()).strip("-")
    path = out_dir / f"{stamp}_{type_slug}.json"
    path.write_text(json.dumps(artifact.to_dict(), indent=2) + "\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def shape_next_action(
    text: str,
    section: str = "",
    root: str | Path = Path(__file__).resolve().parents[4],
) -> tuple[EvaluatorRecommendation, Path]:
    """Classify, evaluate, and emit a shadow artifact for a next-action input.

    Returns (EvaluatorRecommendation, path_to_shadow_artifact).
    The shadow artifact is written to state/lux_nyx/shadow/.
    """
    record = classify_next_action(text, section)
    recommendation = evaluate(record)
    artifact = ShadowArtifact(
        timestamp=datetime.now(UTC).isoformat(),
        source_text=text,
        section=section,
        input_type=record.input_type,
        evaluator_action=recommendation.action,
        recommended_nyx_ops=recommendation.recommended_nyx_ops,
        shadow_artifact_type=recommendation.shadow_artifact_type,
        rationale=recommendation.rationale,
        trace_note=recommendation.trace_note,
    )
    path = write_shadow_artifact(root, artifact)
    return recommendation, path
