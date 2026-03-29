"""Topological memory v0 helpers.

This module provides a small, inspectable retrieval surface for continuity tasks.
It intentionally stays lightweight:
- explicit node/edge/trace records,
- keyword + recency flat baselines,
- a simple topology-aware scorer with path evidence.

The goal is not to claim performance yet, only to make the benchmark loop runnable.
"""

from __future__ import annotations

import json
import math
import os
import re
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_/-]*")
_EMBEDDING_MODEL: Any | None = None
_EMBEDDING_MODEL_NAME: str | None = None


def _load_embedding_model() -> tuple[Any | None, str | None, str | None]:
    """Best-effort sentence-transformers backend.

    Returns: (model_or_none, model_name_or_none, reason_if_unavailable)
    """

    model_name = os.getenv("SC_TM_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        return None, model_name, f"sentence-transformers unavailable: {exc.__class__.__name__}"

    global _EMBEDDING_MODEL
    global _EMBEDDING_MODEL_NAME

    if _EMBEDDING_MODEL is not None and _EMBEDDING_MODEL_NAME == model_name:
        return _EMBEDDING_MODEL, model_name, None

    try:
        _EMBEDDING_MODEL = SentenceTransformer(model_name)
        _EMBEDDING_MODEL_NAME = model_name
    except Exception as exc:  # pragma: no cover - environment dependent
        return None, model_name, f"embedding model load failed: {exc.__class__.__name__}"

    return _EMBEDDING_MODEL, model_name, None


def embedding_backend_status() -> dict[str, Any]:
    model, model_name, reason = _load_embedding_model()
    return {
        "available": model is not None,
        "backend": "sentence-transformers",
        "model": model_name,
        **({"reason": reason} if reason else {}),
    }


@dataclass(frozen=True)
class TopologyNode:
    id: str
    kind: str
    title: str
    path: str
    summary: str
    tags: list[str]
    created_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TopologyNode":
        return cls(
            id=str(data["id"]),
            kind=str(data["kind"]),
            title=str(data["title"]),
            path=str(data.get("path", "")),
            summary=str(data.get("summary", "")),
            tags=[str(tag) for tag in data.get("tags", [])],
            created_at=str(data.get("created_at", "1970-01-01T00:00:00Z")),
            updated_at=str(data.get("updated_at", data.get("created_at", "1970-01-01T00:00:00Z"))),
        )


@dataclass(frozen=True)
class TopologyEdge:
    id: str
    source: str
    target: str
    relation: str
    weight: float = 1.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TopologyEdge":
        return cls(
            id=str(data["id"]),
            source=str(data["source"]),
            target=str(data["target"]),
            relation=str(data["relation"]),
            weight=float(data.get("weight", 1.0)),
        )


@dataclass(frozen=True)
class TopologyTrace:
    id: str
    subject_type: str
    subject_id: str
    event_type: str
    timestamp: str
    weight: float
    note: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TopologyTrace":
        return cls(
            id=str(data["id"]),
            subject_type=str(data["subject_type"]),
            subject_id=str(data["subject_id"]),
            event_type=str(data.get("event_type", "event")),
            timestamp=str(data.get("timestamp", "1970-01-01T00:00:00Z")),
            weight=float(data.get("weight", 1.0)),
            note=str(data.get("note", "")),
        )


@dataclass(frozen=True)
class BenchmarkQuery:
    id: str
    question: str
    category: str
    expected_nodes: list[str]
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BenchmarkQuery":
        return cls(
            id=str(data["id"]),
            question=str(data["question"]),
            category=str(data.get("category", "general")),
            expected_nodes=[str(node) for node in data.get("expected_nodes", [])],
            notes=str(data.get("notes", "")),
        )


@dataclass(frozen=True)
class RankedResult:
    node_id: str
    score: float
    reason: str
    path_nodes: list[str] = field(default_factory=list)
    path_edges: list[str] = field(default_factory=list)
    path_summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QueryEvalResult:
    query_id: str
    expected_nodes: list[str]
    top_nodes: list[str]
    hit: bool
    reciprocal_rank: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GraphBundle:
    nodes: dict[str, TopologyNode]
    edges: list[TopologyEdge]
    traces: list[TopologyTrace]
    reference_time: datetime | None = None

    def __post_init__(self) -> None:
        self._adjacency = self._build_adjacency()
        self._edge_by_id = {edge.id: edge for edge in self.edges}
        self._node_trace_weight = self._compute_node_trace_weight()

    def _build_adjacency(self) -> dict[str, list[tuple[str, TopologyEdge]]]:
        adjacency: dict[str, list[tuple[str, TopologyEdge]]] = defaultdict(list)
        for edge in self.edges:
            adjacency[edge.source].append((edge.target, edge))
            adjacency[edge.target].append((edge.source, edge))
        return dict(adjacency)

    def _compute_node_trace_weight(self) -> dict[str, float]:
        now = self.reference_time if self.reference_time is not None else datetime.now(UTC)
        out: dict[str, float] = defaultdict(float)

        for trace in self.traces:
            age_days = max(0.0, (now - _parse_dt(trace.timestamp)).total_seconds() / 86400.0)
            decay = math.exp(-age_days / 45.0)
            contribution = trace.weight * decay

            if trace.subject_type == "node" and trace.subject_id in self.nodes:
                out[trace.subject_id] += contribution
            elif trace.subject_type == "edge" and trace.subject_id in self._edge_by_id:
                edge = self._edge_by_id[trace.subject_id]
                out[edge.source] += 0.5 * contribution
                out[edge.target] += 0.5 * contribution

        return dict(out)

    def neighbors(self, node_id: str) -> list[tuple[str, TopologyEdge]]:
        return list(self._adjacency.get(node_id, []))

    def edge_by_id(self, edge_id: str) -> TopologyEdge | None:
        return self._edge_by_id.get(edge_id)

    def trace_boost(self, node_id: str) -> float:
        return float(self._node_trace_weight.get(node_id, 0.0))


def _parse_dt(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return datetime(1970, 1, 1, tzinfo=UTC)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall(text.lower()))


def _node_corpus(node: TopologyNode) -> str:
    return " ".join([
        node.id,
        node.kind,
        node.title,
        node.path,
        node.summary,
        " ".join(node.tags),
    ])


def _format_path_summary(
    graph: GraphBundle,
    *,
    path_nodes: list[str],
    path_edges: list[str],
) -> str:
    if not path_nodes:
        return ""
    if not path_edges:
        return path_nodes[0]

    segments: list[str] = [path_nodes[0]]
    for idx, edge_id in enumerate(path_edges):
        if idx + 1 >= len(path_nodes):
            break
        edge = graph.edge_by_id(edge_id)
        left = path_nodes[idx]
        right = path_nodes[idx + 1]

        if edge is None:
            segments.append(f" --[{edge_id}]--> {right}")
            continue

        if edge.source == left and edge.target == right:
            arrow = "-->"
        elif edge.source == right and edge.target == left:
            arrow = "<--"
        else:
            arrow = "<->"

        segments.append(f" --[{edge.relation}:{edge.id}] {arrow} {right}")

    return "".join(segments)


def load_graph_bundle(path: str | Path) -> GraphBundle:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("graph payload must be a JSON object")

    node_records = payload.get("nodes", [])
    edge_records = payload.get("edges", [])
    trace_records = payload.get("traces", [])
    reference_time_raw = payload.get("generated_at")

    if not isinstance(node_records, list) or not isinstance(edge_records, list) or not isinstance(trace_records, list):
        raise ValueError("graph payload must contain list fields: nodes, edges, traces")

    nodes = [TopologyNode.from_dict(item) for item in node_records]
    edges = [TopologyEdge.from_dict(item) for item in edge_records]
    traces = [TopologyTrace.from_dict(item) for item in trace_records]

    node_ids = [node.id for node in nodes]
    edge_ids = [edge.id for edge in edges]

    if len(set(node_ids)) != len(node_ids):
        raise ValueError("duplicate node id in graph payload")
    if len(set(edge_ids)) != len(edge_ids):
        raise ValueError("duplicate edge id in graph payload")

    node_map = {node.id: node for node in nodes}
    edge_map = {edge.id: edge for edge in edges}

    for edge in edges:
        if edge.source not in node_map or edge.target not in node_map:
            raise ValueError(f"edge {edge.id} references missing node")
        if edge.weight <= 0:
            raise ValueError(f"edge {edge.id} has non-positive weight")

    for trace in traces:
        if trace.subject_type not in {"node", "edge"}:
            raise ValueError(f"trace {trace.id} has invalid subject_type")
        if trace.subject_type == "node" and trace.subject_id not in node_map:
            raise ValueError(f"trace {trace.id} references missing node")
        if trace.subject_type == "edge" and trace.subject_id not in edge_map:
            raise ValueError(f"trace {trace.id} references missing edge")

    reference_time = _parse_dt(str(reference_time_raw)) if reference_time_raw else None
    return GraphBundle(nodes=node_map, edges=edges, traces=traces, reference_time=reference_time)


def load_benchmark_queries(path: str | Path) -> list[BenchmarkQuery]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))

    if isinstance(payload, dict):
        rows = payload.get("queries", [])
    elif isinstance(payload, list):
        rows = payload
    else:
        raise ValueError("query payload must be a JSON object or array")

    if not isinstance(rows, list):
        raise ValueError("queries must be a list")

    queries = [BenchmarkQuery.from_dict(item) for item in rows]
    query_ids = [query.id for query in queries]
    if len(set(query_ids)) != len(query_ids):
        raise ValueError("duplicate query id in benchmark")
    return queries


def keyword_baseline(graph: GraphBundle, question: str, *, top_k: int = 5) -> list[RankedResult]:
    q_tokens = _tokens(question)
    if not q_tokens:
        return []

    scored: list[RankedResult] = []
    for node in graph.nodes.values():
        node_tokens = _tokens(_node_corpus(node))
        overlap = q_tokens & node_tokens
        if not overlap:
            continue

        precision = len(overlap) / max(1, len(node_tokens))
        recall = len(overlap) / max(1, len(q_tokens))
        score = 0.75 * recall + 0.25 * precision

        scored.append(
            RankedResult(
                node_id=node.id,
                score=score,
                reason=f"keyword overlap={sorted(overlap)}",
            )
        )

    scored.sort(key=lambda item: (-item.score, item.node_id))
    return scored[:top_k]


def recency_baseline(graph: GraphBundle, question: str, *, top_k: int = 5) -> list[RankedResult]:
    q_tokens = _tokens(question)

    node_times = {node.id: _parse_dt(node.updated_at).timestamp() for node in graph.nodes.values()}
    if not node_times:
        return []

    t_min = min(node_times.values())
    t_max = max(node_times.values())
    span = max(1.0, t_max - t_min)

    scored: list[RankedResult] = []
    for node in graph.nodes.values():
        recency_score = (node_times[node.id] - t_min) / span
        overlap = q_tokens & _tokens(_node_corpus(node)) if q_tokens else set()
        lexical_bonus = 0.2 * (len(overlap) / max(1, len(q_tokens))) if q_tokens else 0.0
        score = 0.8 * recency_score + lexical_bonus

        scored.append(
            RankedResult(
                node_id=node.id,
                score=score,
                reason=(
                    f"recency={recency_score:.3f}"
                    + (f", lexical_overlap={sorted(overlap)}" if overlap else "")
                ),
            )
        )

    scored.sort(key=lambda item: (-item.score, item.node_id))
    return scored[:top_k]


def embedding_baseline(graph: GraphBundle, question: str, *, top_k: int = 5) -> list[RankedResult]:
    """Optional semantic baseline using sentence-transformers when available."""

    question = question.strip()
    if not question:
        return []

    model, model_name, _reason = _load_embedding_model()
    if model is None:
        return []

    nodes = list(graph.nodes.values())
    if not nodes:
        return []

    corpus = [_node_corpus(node) for node in nodes]

    vectors = model.encode(corpus + [question], normalize_embeddings=True)
    doc_vectors = vectors[:-1]
    q_vector = vectors[-1]

    scored: list[RankedResult] = []
    for node, vector in zip(nodes, doc_vectors):
        score = float(sum(float(a) * float(b) for a, b in zip(vector, q_vector)))
        scored.append(
            RankedResult(
                node_id=node.id,
                score=score,
                reason=f"embedding cosine via {model_name}",
            )
        )

    scored.sort(key=lambda item: (-item.score, item.node_id))
    return scored[:top_k]


def topology_aware_retrieval(
    graph: GraphBundle,
    question: str,
    *,
    top_k: int = 5,
    anchor_count: int = 3,
    max_hops: int = 3,
    hop_decay: float = 0.72,
) -> list[RankedResult]:
    if max_hops <= 0:
        raise ValueError("max_hops must be positive")

    anchors = keyword_baseline(graph, question, top_k=max(anchor_count, 1))
    if not anchors:
        anchors = recency_baseline(graph, question, top_k=max(anchor_count, 1))

    lexical = {row.node_id: row.score for row in keyword_baseline(graph, question, top_k=max(20, top_k * 3))}
    node_scores: dict[str, float] = defaultdict(float)
    best_paths: dict[str, tuple[float, list[str], list[str], str]] = {}

    for anchor in anchors:
        node_scores[anchor.node_id] += anchor.score
        best_paths.setdefault(anchor.node_id, (anchor.score, [anchor.node_id], [], anchor.node_id))

        queue: deque[tuple[str, int, float, list[str], list[str]]] = deque()
        queue.append((anchor.node_id, 0, anchor.score, [anchor.node_id], []))
        best_local: dict[str, float] = {anchor.node_id: anchor.score}

        while queue:
            curr, depth, strength, path_nodes, path_edges = queue.popleft()
            if depth >= max_hops:
                continue

            for neighbor, edge in graph.neighbors(curr):
                if neighbor in path_nodes:
                    continue
                propagated = strength * edge.weight * hop_decay
                if propagated < 1e-6:
                    continue
                if propagated <= best_local.get(neighbor, 0.0):
                    continue

                best_local[neighbor] = propagated
                candidate_nodes = path_nodes + [neighbor]
                candidate_edges = path_edges + [edge.id]

                node_scores[neighbor] += propagated
                prev = best_paths.get(neighbor)
                if prev is None or propagated > prev[0]:
                    best_paths[neighbor] = (propagated, candidate_nodes, candidate_edges, anchor.node_id)

                queue.append((neighbor, depth + 1, propagated, candidate_nodes, candidate_edges))

    ranked: list[RankedResult] = []
    for node_id, node in graph.nodes.items():
        topo_score = node_scores.get(node_id, 0.0)
        lexical_score = lexical.get(node_id, 0.0)
        trace_score = graph.trace_boost(node_id)

        final_score = 0.55 * topo_score + 0.30 * lexical_score + 0.15 * trace_score
        path_info = best_paths.get(node_id)

        path_nodes: list[str] = []
        path_edges: list[str] = []
        anchor_id = ""
        if path_info is not None:
            _, path_nodes, path_edges, anchor_id = path_info

        reason = (
            f"topology={topo_score:.3f}, lexical={lexical_score:.3f}, trace={trace_score:.3f}"
            + (f", anchor={anchor_id}" if anchor_id else "")
        )

        path_summary = _format_path_summary(graph, path_nodes=path_nodes, path_edges=path_edges)

        ranked.append(
            RankedResult(
                node_id=node_id,
                score=final_score,
                reason=reason,
                path_nodes=path_nodes,
                path_edges=path_edges,
                path_summary=path_summary,
            )
        )

    ranked.sort(key=lambda item: (-item.score, item.node_id))
    return ranked[:top_k]


def _reciprocal_rank(expected: list[str], ranked: list[RankedResult]) -> float:
    expected_set = set(expected)
    if not expected_set:
        return 0.0
    for index, row in enumerate(ranked, start=1):
        if row.node_id in expected_set:
            return 1.0 / index
    return 0.0


def evaluate_queries(
    graph: GraphBundle,
    queries: list[BenchmarkQuery],
    *,
    top_k: int = 3,
    include_topology: bool = True,
    include_embedding: bool = True,
) -> dict[str, Any]:
    embedding_status = embedding_backend_status() if include_embedding else {"available": False}

    scorers: dict[str, Any] = {
        "keyword": keyword_baseline,
        "recency": recency_baseline,
    }
    if include_topology:
        scorers["topology"] = topology_aware_retrieval
    if include_embedding and embedding_status.get("available"):
        scorers["embedding"] = embedding_baseline

    report: dict[str, Any] = {
        "query_count": len(queries),
        "top_k": top_k,
        "baselines": {},
        "embedding_backend": embedding_status,
    }

    if include_embedding and not embedding_status.get("available"):
        report["baselines"]["embedding"] = {
            "available": False,
            "reason": embedding_status.get("reason", "embedding backend unavailable"),
            "queries": [],
            "ranked_results": {},
        }

    for name, scorer in scorers.items():
        rows: list[QueryEvalResult] = []
        ranked_payload: dict[str, list[dict[str, Any]]] = {}

        for query in queries:
            ranked = scorer(graph, query.question, top_k=top_k)
            top_nodes = [row.node_id for row in ranked]
            hit = bool(set(query.expected_nodes) & set(top_nodes))
            rr = _reciprocal_rank(query.expected_nodes, ranked)

            rows.append(
                QueryEvalResult(
                    query_id=query.id,
                    expected_nodes=query.expected_nodes,
                    top_nodes=top_nodes,
                    hit=hit,
                    reciprocal_rank=rr,
                )
            )
            ranked_payload[query.id] = [item.to_dict() for item in ranked]

        denom = max(1, len(rows))
        hit_rate = sum(1 for row in rows if row.hit) / denom
        mean_rr = sum(row.reciprocal_rank for row in rows) / denom

        baseline_payload = {
            "hit_rate": hit_rate,
            "mrr": mean_rr,
            "queries": [row.to_dict() for row in rows],
            "ranked_results": ranked_payload,
        }
        if name == "embedding":
            baseline_payload["available"] = True
            baseline_payload["backend"] = embedding_status.get("backend")
            baseline_payload["model"] = embedding_status.get("model")

        report["baselines"][name] = baseline_payload

    return report


def write_report(report: dict[str, Any], out_path: str | Path) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
