import unittest
from pathlib import Path

from nfem_suite.intelligence.ygg.topological_memory import (
    evaluate_queries,
    load_benchmark_queries,
    load_graph_bundle,
)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "memory" / "research" / "topological-memory-v0"


class TopologicalMemoryArtifactTests(unittest.TestCase):
    def test_frozen_v0_artifacts_support_provisional_gate(self):
        graph = load_graph_bundle(ARTIFACT_ROOT / "graph_v0.json")
        queries = load_benchmark_queries(ARTIFACT_ROOT / "benchmark_queries_v0.json")
        report = evaluate_queries(graph, queries, top_k=3, include_topology=True, include_embedding=False)

        self.assertEqual(len(graph.nodes), 12)
        self.assertEqual(len(queries), 30)

        keyword = report["baselines"]["keyword"]
        recency = report["baselines"]["recency"]
        topology = report["baselines"]["topology"]

        self.assertGreater(topology["hit_rate"], keyword["hit_rate"])
        self.assertGreater(topology["hit_rate"], recency["hit_rate"])
        self.assertGreater(topology["mrr"], keyword["mrr"])
        self.assertGreater(topology["mrr"], recency["mrr"])

        first_rows = topology["ranked_results"]["Q-001"]
        self.assertTrue(first_rows)
        self.assertIn("path_summary", first_rows[0])
        self.assertIn("path_nodes", first_rows[0])
        self.assertIn("path_edges", first_rows[0])


if __name__ == "__main__":
    unittest.main()
