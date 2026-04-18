import unittest

from scripts.dispatch_log_validator import validate_dispatch_log_entry


class DispatchLogValidatorTests(unittest.TestCase):
    def test_accepts_valid_memory_membrane_evidence(self):
        errors = validate_dispatch_log_entry(
            {
                "ts": "2026-04-18T08:12:20",
                "event": "spawn_dispatched",
                "id": "spawn-01",
                "ok": True,
                "control_mode": "control-affecting",
                "governance_policy_ref": "spine/membranes/governance-runtime-v1.yaml",
                "continuity_relevant": True,
                "memory_consulted": True,
                "memory_artifact_ids": [
                    "memory/research/topological-memory-v0/comparison_summary_v0.json",
                    "state/lux_nyx/shadow/2026-04-18T08-12-20.270195+00-00_prompt.json",
                ],
                "memory_policy_ref": "spine/membranes/memory-dispatch-v1.yaml",
                "memory_request_provenance": "spawn-01:prompt_context.memory_artifact_ids",
            }
        )

        self.assertEqual(errors, [])

    def test_rejects_non_inspectable_artifact_refs(self):
        errors = validate_dispatch_log_entry(
            {
                "ts": "2026-04-18T08:12:20",
                "event": "spawn_dispatched",
                "id": "spawn-01",
                "ok": True,
                "control_mode": "control-affecting",
                "governance_policy_ref": "spine/membranes/governance-runtime-v1.yaml",
                "continuity_relevant": False,
                "memory_consulted": True,
                "memory_artifact_ids": ["artifact-without-slash"],
                "memory_policy_ref": "spine/membranes/memory-dispatch-v1.yaml",
                "memory_request_provenance": "spawn-01:request.memory_artifact_ids",
            }
        )

        self.assertIn("memory_artifact_ids must contain inspectable repo-relative artifact refs", errors)

    def test_rejects_malformed_memory_request_provenance(self):
        errors = validate_dispatch_log_entry(
            {
                "ts": "2026-04-18T08:12:20",
                "event": "spawn_dispatched",
                "id": "spawn-01",
                "ok": True,
                "control_mode": "descriptive",
                "governance_policy_ref": "spine/membranes/governance-runtime-v1.yaml",
                "continuity_relevant": True,
                "memory_consulted": False,
                "memory_artifact_ids": [],
                "memory_policy_ref": "spine/membranes/memory-dispatch-v1.yaml",
                "memory_request_provenance": "spawn-01",
            }
        )

        self.assertIn("memory_request_provenance must be formatted as <request-id>:<source>", errors)

    def test_rejects_memory_consulted_with_capability_lane_provenance(self):
        errors = validate_dispatch_log_entry(
            {
                "ts": "2026-04-18T08:12:20",
                "event": "spawn_dispatched",
                "id": "spawn-01",
                "ok": True,
                "control_mode": "descriptive",
                "governance_policy_ref": "spine/membranes/governance-runtime-v1.yaml",
                "continuity_relevant": True,
                "memory_consulted": True,
                "memory_artifact_ids": ["memory/2026-04-18.md#L1-L4"],
                "memory_policy_ref": "spine/membranes/memory-dispatch-v1.yaml",
                "memory_request_provenance": "spawn-01:prompt_context.capability_lane",
            }
        )

        self.assertIn(
            "memory_consulted=true requires memory_request_provenance to cite artifact-bearing evidence",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
