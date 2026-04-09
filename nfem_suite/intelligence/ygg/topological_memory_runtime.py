"""Runtime adoption surface for topological memory.

This module keeps topological retrieval bounded:
- retrieval outputs are advisory context only,
- provenance is explicit and inspectable,
- fallback stays available through flat retrieval.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from nfem_suite.intelligence.ygg.topological_memory import (
    GraphBundle,
    RankedResult,
    keyword_baseline,
    load_graph_bundle,
    recency_baseline,
    topology_aware_retrieval,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_GRAPH = ROOT / "memory" / "research" / "topological-memory-v0" / "graph_v0.json"
DEFAULT_TRACE_DIR = ROOT / "memory" / "research" / "topological-memory-v0" / "runtime_traces"

ALLOWED_MODES = {"auto", "topology", "flat"}


def _slug(text: str, *, fallback: str = "query") -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")
    return cleaned[:64] or fallback


def _relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


@dataclass(frozen=True)
class RuntimeRetrievalResult:
    query: str
    mode_requested: str
    mode_used: str
    baseline_mode: str
    authority_note: str
    provenance: dict[str, Any]
    ranked_results: list[dict[str, Any]]
    retrieval_trace_artifact: str | None = None
    fallback_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_mode(mode: str) -> str:
    normalized = str(mode or "auto").strip().lower()
    if normalized not in ALLOWED_MODES:
        raise ValueError(f"unsupported retrieval mode: {mode}")
    return normalized


def _graph_provenance(graph_path: Path, graph: GraphBundle) -> dict[str, Any]:
    return {
        "graph": _relative(graph_path),
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "trace_count": len(graph.traces),
    }


def _result_payload(rows: list[RankedResult]) -> list[dict[str, Any]]:
    return [row.to_dict() for row in rows]


def _flat_retrieval(graph: GraphBundle, query: str, *, top_k: int) -> tuple[str, list[RankedResult]]:
    keyword_rows = keyword_baseline(graph, query, top_k=top_k)
    if keyword_rows:
        return "keyword", keyword_rows
    return "recency", recency_baseline(graph, query, top_k=top_k)


def retrieve_continuity_context(
    query: str,
    *,
    mode: str = "auto",
    top_k: int = 3,
    graph_path: str | Path = DEFAULT_GRAPH,
) -> RuntimeRetrievalResult:
    normalized_mode = _normalize_mode(mode)
    graph_file = Path(graph_path)
    if not graph_file.exists():
        raise FileNotFoundError(f"graph not found: {graph_file}")

    graph = load_graph_bundle(graph_file)
    fallback_reason: str | None = None

    if normalized_mode == "flat":
        baseline_mode, rows = _flat_retrieval(graph, query, top_k=top_k)
        mode_used = "flat"
    else:
        try:
            rows = topology_aware_retrieval(graph, query, top_k=top_k)
            baseline_mode = "topology"
            mode_used = "topology"
            if not rows:
                baseline_mode, rows = _flat_retrieval(graph, query, top_k=top_k)
                mode_used = "flat"
                fallback_reason = "topology produced no ranked results"
        except Exception as exc:
            if normalized_mode == "topology":
                raise
            baseline_mode, rows = _flat_retrieval(graph, query, top_k=top_k)
            mode_used = "flat"
            fallback_reason = f"topology failed: {exc.__class__.__name__}"

    provenance = {
        "retrieved_at": datetime.now(UTC).isoformat(),
        "graph_bundle": _graph_provenance(graph_file, graph),
        "mode_requested": normalized_mode,
        "mode_used": mode_used,
        "baseline_mode": baseline_mode,
        "top_k": max(1, int(top_k)),
    }
    if fallback_reason:
        provenance["fallback_reason"] = fallback_reason

    return RuntimeRetrievalResult(
        query=query,
        mode_requested=normalized_mode,
        mode_used=mode_used,
        baseline_mode=baseline_mode,
        authority_note="Advisory continuity context only; retrieval outputs may not self-authorize planning, governance, or runtime policy changes.",
        provenance=provenance,
        ranked_results=_result_payload(rows),
        fallback_reason=fallback_reason,
    )


def write_retrieval_trace(
    query: str,
    *,
    mode: str = "auto",
    top_k: int = 3,
    trace_dir: str | Path = DEFAULT_TRACE_DIR,
    graph_path: str | Path = DEFAULT_GRAPH,
) -> RuntimeRetrievalResult:
    result = retrieve_continuity_context(query, mode=mode, top_k=top_k, graph_path=graph_path)

    out_dir = Path(trace_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out_path = out_dir / f"{stamp}_{_slug(query)}_{result.mode_used}.json"
    out_path.write_text(json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8")

    payload = result.to_dict()
    payload["retrieval_trace_artifact"] = _relative(out_path)
    return RuntimeRetrievalResult(**payload)
