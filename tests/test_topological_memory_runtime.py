import json
import tempfile
import unittest
from pathlib import Path

from nfem_suite.intelligence.ygg.topological_memory_runtime import (
    retrieve_continuity_context,
    write_retrieval_trace,
)


class TopologicalMemoryRuntimeTests(unittest.TestCase):
    def _write_fixture(self, root: Path) -> Path:
        graph = {
            "schema_version": "topological-memory-v0",
            "generated_at": "2026-03-29T00:00:00Z",
            "nodes": [
                {
                    "id": "N_DOC",
                    "kind": "doc",
                    "title": "Continuity Draft",
                    "path": "docs/draft.md",
                    "summary": "topological memory continuity draft",
                    "tags": ["topology", "continuity"],
                    "created_at": "2026-03-28T00:00:00Z",
                    "updated_at": "2026-03-29T00:00:00Z",
                },
                {
                    "id": "N_PLAN",
                    "kind": "plan",
                    "title": "Planner TODO",
                    "path": "plans/todo.md",
                    "summary": "execution queue for planner context",
                    "tags": ["todo", "planning"],
                    "created_at": "2026-03-28T00:00:00Z",
                    "updated_at": "2026-03-28T10:00:00Z",
                },
            ],
            "edges": [
                {
                    "id": "E1",
                    "source": "N_PLAN",
                    "target": "N_DOC",
                    "relation": "depends_on",
                    "weight": 0.8,
                }
            ],
            "traces": [
                {
                    "id": "T1",
                    "subject_type": "node",
                    "subject_id": "N_DOC",
                    "event_type": "review",
                    "timestamp": "2026-03-29T00:00:00Z",
                    "weight": 0.9,
                }
            ],
        }
        graph_path = root / "graph.json"
        graph_path.write_text(json.dumps(graph), encoding="utf-8")
        return graph_path

    def test_retrieve_continuity_context_uses_flat_mode_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            graph_path = self._write_fixture(Path(td))
            result = retrieve_continuity_context(
                "Where is planner context draft?",
                mode="flat",
                graph_path=graph_path,
                top_k=2,
            )

        self.assertEqual(result.mode_requested, "flat")
        self.assertEqual(result.mode_used, "flat")
        self.assertIn(result.baseline_mode, {"keyword", "recency"})
        self.assertTrue(result.ranked_results)
        self.assertIn("graph_bundle", result.provenance)
        self.assertIn("authority_note", result.to_dict())

    def test_write_retrieval_trace_persists_provenance_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            graph_path = self._write_fixture(root)
            trace_dir = root / "runtime_traces"

            result = write_retrieval_trace(
                "Where is the continuity draft?",
                mode="auto",
                graph_path=graph_path,
                trace_dir=trace_dir,
                top_k=2,
            )

            self.assertIsNotNone(result.retrieval_trace_artifact)
            trace_files = list(trace_dir.glob("*.json"))
            self.assertEqual(len(trace_files), 1)
            payload = json.loads(trace_files[0].read_text(encoding="utf-8"))
            self.assertEqual(payload["query"], "Where is the continuity draft?")
            self.assertIn("provenance", payload)
            self.assertIn("graph_bundle", payload["provenance"])
            self.assertEqual(str(trace_files[0].resolve()), result.retrieval_trace_artifact)
            self.assertEqual(payload["retrieval_trace_artifact"], None)


if __name__ == "__main__":
    unittest.main()
