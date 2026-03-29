import json
import tempfile
import unittest
from pathlib import Path

from nfem_suite.intelligence.ygg.topological_memory import (
    evaluate_queries,
    load_benchmark_queries,
    load_graph_bundle,
)


class TestTopologicalMemory(unittest.TestCase):
    def _write_fixture(self, root: Path) -> tuple[Path, Path]:
        graph = {
            "schema_version": "topological-memory-v0",
            "generated_at": "2026-03-29T00:00:00Z",
            "nodes": [
                {
                    "id": "N_DOC",
                    "kind": "doc",
                    "title": "Draft",
                    "path": "docs/draft.md",
                    "summary": "topological memory continuity draft",
                    "tags": ["topology", "continuity"],
                    "created_at": "2026-03-28T00:00:00Z",
                    "updated_at": "2026-03-29T00:00:00Z",
                },
                {
                    "id": "N_PLAN",
                    "kind": "plan",
                    "title": "Todo",
                    "path": "plans/todo.md",
                    "summary": "execution queue",
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

        queries = {
            "schema_version": "topological-memory-queries-v0",
            "generated_at": "2026-03-29T00:00:00Z",
            "queries": [
                {
                    "id": "Q1",
                    "question": "Where is topological memory draft?",
                    "category": "origin_trace",
                    "expected_nodes": ["N_DOC"],
                },
                {
                    "id": "Q2",
                    "question": "What todo tracks execution queue?",
                    "category": "resume_next",
                    "expected_nodes": ["N_PLAN"],
                },
            ],
        }

        graph_path = root / "graph.json"
        query_path = root / "queries.json"
        graph_path.write_text(json.dumps(graph), encoding="utf-8")
        query_path.write_text(json.dumps(queries), encoding="utf-8")
        return graph_path, query_path

    def test_evaluate_queries_with_baselines(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            graph_path, query_path = self._write_fixture(Path(td))

            graph = load_graph_bundle(graph_path)
            queries = load_benchmark_queries(query_path)
            report = evaluate_queries(graph, queries, top_k=2, include_topology=True, include_embedding=True)
            report_repeat = evaluate_queries(graph, queries, top_k=2, include_topology=True, include_embedding=True)

            self.assertIn("keyword", report["baselines"])
            self.assertIn("recency", report["baselines"])
            self.assertIn("topology", report["baselines"])
            self.assertIn("embedding", report["baselines"])

            keyword = report["baselines"]["keyword"]
            self.assertGreaterEqual(keyword["hit_rate"], 0.0)
            self.assertLessEqual(keyword["hit_rate"], 1.0)

            topology_rows = report["baselines"]["topology"]["ranked_results"]["Q1"]
            self.assertTrue(topology_rows)
            self.assertIn("path_summary", topology_rows[0])
            self.assertIn("path_nodes", topology_rows[0])
            self.assertIn("path_edges", topology_rows[0])

            topology_rows_repeat = report_repeat["baselines"]["topology"]["ranked_results"]["Q1"]
            self.assertEqual(topology_rows[0]["node_id"], topology_rows_repeat[0]["node_id"])
            self.assertAlmostEqual(topology_rows[0]["score"], topology_rows_repeat[0]["score"], places=12)

            embedding = report["baselines"]["embedding"]
            if embedding.get("available") is False:
                self.assertIn("reason", embedding)
            else:
                self.assertIn("hit_rate", embedding)
                self.assertIn("mrr", embedding)


if __name__ == "__main__":
    unittest.main()
