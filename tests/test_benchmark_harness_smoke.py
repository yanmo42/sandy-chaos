import unittest

from nfem_suite.benchmarks.temporal_predictive_processing import (
    _ALLOWED_ABLATION_IDS,
    BenchmarkCase,
    BenchmarkFrame,
    BenchmarkHarness,
    ScaffoldVariant,
    make_default_harness,
)


class BenchmarkHarnessSmokeTests(unittest.TestCase):
    def test_scaffold_exposes_three_variant_interfaces(self):
        harness = make_default_harness()

        interfaces = harness.variant_interfaces()
        smoke_results = harness.run_smoke_case()

        self.assertEqual(
            list(interfaces.keys()),
            [
                "single-scale-baseline",
                "multiframe-unconstrained-baseline",
                "neighbor-only-contract-model",
            ],
        )
        self.assertEqual(len(smoke_results), 3)

        for variant_id, interface_contract in interfaces.items():
            self.assertTrue(interface_contract, msg=f"missing interface for {variant_id}")

        for result in smoke_results:
            self.assertEqual(result.status, "scaffold-only")
            self.assertIsNone(result.placeholder_metrics["prediction_error"])
            self.assertTrue(
                result.causal_guards,
                msg=f"missing causal guards for {result.variant_id}",
            )
            self.assertTrue(
                result.failure_modes,
                msg=f"missing failure modes for {result.variant_id}",
            )

    def test_smoke_results_match_canonical_variant_order(self):
        # Falsification guard: ``run_smoke_case()`` must emit results in the
        # canonical variant order. Without this, a shuffled result list would
        # still pass the generic shape checks above, letting outsiders read
        # the wrong ``variant_id`` against the wrong interface contract. The
        # scaffold's inspectability depends on this pairing being pinned.
        harness = make_default_harness()

        smoke_results = harness.run_smoke_case()

        self.assertEqual(
            [result.variant_id for result in smoke_results],
            [
                "single-scale-baseline",
                "multiframe-unconstrained-baseline",
                "neighbor-only-contract-model",
            ],
        )
        self.assertEqual(
            [result.variant_id for result in smoke_results],
            [variant.variant_id for variant in harness.variants],
        )


class BenchmarkHarnessDescribeContractTests(unittest.TestCase):
    """Falsification guard: ``describe()`` must keep advertising scaffold-only.

    The harness and each variant report ``status="scaffold-only"`` and the
    harness notes explicitly deny empirical-result claims. Those declarations
    are the only outsider-legible signal that no promotion is implied yet. If
    they silently disappear or change wording, the scaffold could be read as
    producing real scores. This test pins the canonical shape so any drift has
    to happen deliberately, not by accident.
    """

    _REQUIRED_NOTE_FRAGMENTS = (
        "inspectable scaffolding only",
        "No empirical results",
        "Strict causality",
    )

    def test_harness_describe_declares_scaffold_only_posture(self):
        harness = make_default_harness()

        description = harness.describe()

        self.assertEqual(description["status"], "scaffold-only")
        variant_ids = [entry["variant_id"] for entry in description["variants"]]
        self.assertEqual(
            variant_ids,
            [
                "single-scale-baseline",
                "multiframe-unconstrained-baseline",
                "neighbor-only-contract-model",
            ],
        )
        for entry in description["variants"]:
            self.assertEqual(
                entry["status"],
                "scaffold-only",
                msg=f"variant {entry['variant_id']!r} must advertise scaffold-only status",
            )
        joined_notes = " ".join(description["notes"])
        for fragment in self._REQUIRED_NOTE_FRAGMENTS:
            self.assertIn(
                fragment,
                joined_notes,
                msg=(
                    f"harness describe notes dropped required fragment {fragment!r}; "
                    "scaffold-only posture must remain explicit"
                ),
            )


class BenchmarkHarnessNoEmpiricalScoresTests(unittest.TestCase):
    """Falsification guard: the smoke scaffold must not emit numeric scores.

    The scaffold declares `status="scaffold-only"` and `"No empirical results"`
    in its describe notes. If any of the canonical numeric placeholder metrics
    silently turns into a real number, the harness has drifted out of the
    inspectable-only posture. Checking only `prediction_error` would let the
    other three slots drift unnoticed, so this test asserts the full set.
    """

    _NUMERIC_PLACEHOLDER_KEYS = (
        "prediction_error",
        "contract_violation_rate",
        "coherence_gain",
        "latency_adjusted_utility",
    )

    def test_smoke_run_emits_no_numeric_scores_across_variants(self):
        harness = make_default_harness()

        smoke_results = harness.run_smoke_case()

        self.assertEqual(len(smoke_results), 3)
        for result in smoke_results:
            self.assertEqual(result.status, "scaffold-only")
            for key in self._NUMERIC_PLACEHOLDER_KEYS:
                self.assertIn(
                    key,
                    result.placeholder_metrics,
                    msg=f"variant {result.variant_id} missing placeholder metric {key!r}",
                )
                self.assertIsNone(
                    result.placeholder_metrics[key],
                    msg=(
                        f"variant {result.variant_id} emitted a non-None value for "
                        f"{key!r}; scaffold must not report empirical scores yet"
                    ),
                )


class BenchmarkHarnessAblationsContractTests(unittest.TestCase):
    """Falsification guard: the declared ablation list must not drift silently.

    ``BenchmarkHarness.ablations`` is part of the outsider-legible describe
    output. Consumers (spec notes, falsification reviewers) read it as the
    scaffold's canonical claim about *which* ablations the benchmark intends to
    cover once scoring exists. If a name is silently added, renamed, or dropped
    here, the ablation-table contract has drifted from the spec without a human
    review. Pinning the exact ordered tuple forces any change to be deliberate.
    """

    _CANONICAL_ABLATIONS = (
        "no-contract-projection",
        "no-shared-latent-space",
        "no-cross-frame-coupling",
        "all-to-all-coupling",
        "latency-distortion-removed",
    )

    def test_default_harness_exposes_canonical_ablation_list(self):
        harness = make_default_harness()

        self.assertEqual(harness.ablations, self._CANONICAL_ABLATIONS)

    def test_describe_reports_canonical_ablation_list(self):
        harness = make_default_harness()

        description = harness.describe()

        self.assertEqual(
            tuple(description["ablations"]),
            self._CANONICAL_ABLATIONS,
            msg=(
                "harness.describe() ablation list drifted from the canonical "
                "scaffold contract; silent reorder/rename would desync the "
                "ablation table spec from code"
            ),
        )


class BenchmarkVariantRequiredMetadataContractTests(unittest.TestCase):
    """Falsification guard: per-variant metadata-key requirements are pinned.

    Only ``neighbor-only-contract-model`` is supposed to declare a metadata
    precondition (``neighbor_topology``). The two baselines must stay
    minimal-contract: no declared required metadata keys. Silent drift either
    way would misrepresent the scaffold's falsification posture — a baseline
    could quietly start refusing cases, or the contract model could quietly
    lose its precondition and accept under-specified cases as scaffold-only
    passes. Pinning the mapping prevents both failure modes.
    """

    _EXPECTED_REQUIRED_METADATA = {
        "single-scale-baseline": (),
        "multiframe-unconstrained-baseline": (),
        "neighbor-only-contract-model": ("neighbor_topology",),
    }

    def test_each_variant_declares_expected_required_metadata_keys(self):
        harness = make_default_harness()

        actual = {
            variant.variant_id: tuple(variant.required_metadata_keys)
            for variant in harness.variants
        }

        self.assertEqual(actual, self._EXPECTED_REQUIRED_METADATA)

    def test_describe_reports_required_metadata_per_variant(self):
        harness = make_default_harness()

        description = harness.describe()

        actual = {
            entry["variant_id"]: tuple(entry["required_metadata_keys"])
            for entry in description["variants"]
        }
        self.assertEqual(
            actual,
            self._EXPECTED_REQUIRED_METADATA,
            msg=(
                "describe() required_metadata_keys drifted from the canonical "
                "scaffold contract; baselines must remain minimal-contract and "
                "the neighbor-only variant must keep its precondition visible"
            ),
        )


class BenchmarkHarnessFailureModeTests(unittest.TestCase):
    """Falsification-oriented checks: the scaffold must refuse malformed inputs.

    These tests protect the inspectable-only contract by proving that invalid
    states fail loudly instead of silently accepting ill-formed wiring.
    """

    def test_unknown_variant_id_is_rejected(self):
        with self.assertRaises(ValueError):
            ScaffoldVariant(
                variant_id="not-a-real-variant",
                label="bogus",
                interface_contract=("x",),
                causal_guards=("y",),
                failure_modes=("z",),
            )

    def test_harness_rejects_non_canonical_variant_order(self):
        default = make_default_harness()
        shuffled = (default.variants[2], default.variants[0], default.variants[1])
        with self.assertRaises(ValueError):
            BenchmarkHarness(variants=shuffled)

    def test_harness_rejects_unknown_ablation_id(self):
        # Falsification symmetry: variant ids are canonical-only and ablation
        # ids must be too. A silent typo/rename at construction time would
        # otherwise drift past the scaffold contract without failing loudly.
        default = make_default_harness()
        with self.assertRaises(ValueError) as ctx:
            BenchmarkHarness(
                variants=default.variants,
                ablations=("no-contract-projection", "totally-made-up-ablation"),
            )
        self.assertIn("unknown ablation ids", str(ctx.exception))
        self.assertIn("totally-made-up-ablation", str(ctx.exception))

    def test_harness_rejects_duplicate_ablation_ids(self):
        default = make_default_harness()
        duplicated = _ALLOWED_ABLATION_IDS + ("no-contract-projection",)
        with self.assertRaises(ValueError) as ctx:
            BenchmarkHarness(variants=default.variants, ablations=duplicated)
        self.assertIn("duplicate ablation ids", str(ctx.exception))

    def test_harness_rejects_missing_canonical_ablation(self):
        default = make_default_harness()
        dropped = tuple(a for a in _ALLOWED_ABLATION_IDS if a != "all-to-all-coupling")
        with self.assertRaises(ValueError) as ctx:
            BenchmarkHarness(variants=default.variants, ablations=dropped)
        self.assertIn("missing canonical ablation ids", str(ctx.exception))
        self.assertIn("all-to-all-coupling", str(ctx.exception))

    def test_benchmark_case_rejects_empty_frames(self):
        with self.assertRaises(ValueError):
            BenchmarkCase(
                case_id="empty",
                description="no frames",
                frames=(),
                target_state={"signal": 0.0},
            )

    def test_benchmark_case_rejects_duplicate_frame_ids(self):
        frame = BenchmarkFrame(
            frame_id="dup",
            timestep=0,
            observed_state={"signal": 0.0},
        )
        with self.assertRaises(ValueError):
            BenchmarkCase(
                case_id="dup-case",
                description="duplicate frame ids",
                frames=(frame, frame),
                target_state={"signal": 0.0},
            )

    def test_benchmark_frame_rejects_negative_latency(self):
        bad_frame = BenchmarkFrame(
            frame_id="f",
            timestep=0,
            observed_state={"signal": 0.0},
            latency=-0.1,
        )
        with self.assertRaises(ValueError):
            BenchmarkCase(
                case_id="neg-latency",
                description="negative latency must fail",
                frames=(bad_frame,),
                target_state={"signal": 0.0},
            )

    def test_benchmark_case_rejects_retrocausal_frame_order(self):
        # Frames must be supplied in non-decreasing timestep order. A later
        # frame_id carrying an earlier timestep would let a variant index a
        # "future" observation while pretending it was a past one.
        earlier = BenchmarkFrame(
            frame_id="past",
            timestep=2,
            observed_state={"signal": 0.0},
        )
        later = BenchmarkFrame(
            frame_id="before-past",
            timestep=1,
            observed_state={"signal": 0.0},
        )
        with self.assertRaises(ValueError):
            BenchmarkCase(
                case_id="retrocausal",
                description="non-monotonic timesteps must fail loudly",
                frames=(earlier, later),
                target_state={"signal": 0.0},
            )

    def test_neighbor_only_variant_refuses_backward_edge_in_topology(self):
        # A declared neighbor edge that runs backward in time would let the
        # contract variant read a later frame as if it were informed by an
        # earlier one. Strict causality requires refusal, not a quiet pass.
        from nfem_suite.benchmarks.temporal_predictive_processing import (
            make_default_harness,
            make_smoke_case,
        )

        harness = make_default_harness()
        neighbor_variant = next(
            v for v in harness.variants if v.variant_id == "neighbor-only-contract-model"
        )

        base_case = make_smoke_case()
        bad_metadata = dict(base_case.metadata)
        bad_metadata["neighbor_topology"] = (("slow", "fast"),)
        bad_case = BenchmarkCase(
            case_id=base_case.case_id,
            description=base_case.description,
            frames=base_case.frames,
            target_state=base_case.target_state,
            metadata=bad_metadata,
        )

        result = neighbor_variant.run(bad_case)

        self.assertEqual(result.status, "scaffold-only-contract-unmet")
        self.assertIn("backward in time", result.summary)
        self.assertIn("backward in time", result.placeholder_metrics["invariant_violation"])
        self.assertIsNone(result.placeholder_metrics["prediction_error"])

    def test_neighbor_only_variant_refuses_unknown_frame_reference(self):
        from nfem_suite.benchmarks.temporal_predictive_processing import (
            make_default_harness,
            make_smoke_case,
        )

        harness = make_default_harness()
        neighbor_variant = next(
            v for v in harness.variants if v.variant_id == "neighbor-only-contract-model"
        )

        base_case = make_smoke_case()
        bad_metadata = dict(base_case.metadata)
        bad_metadata["neighbor_topology"] = (("fast", "ghost"),)
        bad_case = BenchmarkCase(
            case_id=base_case.case_id,
            description=base_case.description,
            frames=base_case.frames,
            target_state=base_case.target_state,
            metadata=bad_metadata,
        )

        result = neighbor_variant.run(bad_case)

        self.assertEqual(result.status, "scaffold-only-contract-unmet")
        self.assertIn("unknown frame_id", result.summary)
        self.assertIn("ghost", result.summary)

    def test_neighbor_only_variant_refuses_empty_topology(self):
        from nfem_suite.benchmarks.temporal_predictive_processing import (
            make_default_harness,
            make_smoke_case,
        )

        harness = make_default_harness()
        neighbor_variant = next(
            v for v in harness.variants if v.variant_id == "neighbor-only-contract-model"
        )

        base_case = make_smoke_case()
        bad_metadata = dict(base_case.metadata)
        bad_metadata["neighbor_topology"] = ()
        bad_case = BenchmarkCase(
            case_id=base_case.case_id,
            description=base_case.description,
            frames=base_case.frames,
            target_state=base_case.target_state,
            metadata=bad_metadata,
        )

        result = neighbor_variant.run(bad_case)

        self.assertEqual(result.status, "scaffold-only-contract-unmet")
        self.assertIn("at least one edge", result.summary)

    def test_neighbor_only_variant_refuses_case_without_topology_metadata(self):
        # The neighbor-only contract model declares that neighbor topology
        # metadata is a precondition. Without it, the scaffold must refuse the
        # case instead of silently emitting a "scaffold-only" pass.
        from nfem_suite.benchmarks.temporal_predictive_processing import (
            make_default_harness,
            make_smoke_case,
        )

        harness = make_default_harness()
        neighbor_variant = next(
            v for v in harness.variants if v.variant_id == "neighbor-only-contract-model"
        )

        base_case = make_smoke_case()
        stripped_metadata = {
            k: v for k, v in base_case.metadata.items() if k != "neighbor_topology"
        }
        bad_case = BenchmarkCase(
            case_id=base_case.case_id,
            description=base_case.description,
            frames=base_case.frames,
            target_state=base_case.target_state,
            metadata=stripped_metadata,
        )

        result = neighbor_variant.run(bad_case)

        self.assertEqual(result.status, "scaffold-only-contract-unmet")
        self.assertIn("neighbor_topology", result.summary)
        self.assertEqual(
            result.placeholder_metrics["missing_metadata_keys"], ["neighbor_topology"]
        )
        self.assertIsNone(result.placeholder_metrics["prediction_error"])


if __name__ == "__main__":
    unittest.main()
