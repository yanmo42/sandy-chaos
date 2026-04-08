from pathlib import Path

import pytest

from nfem_suite.intelligence.ygg.frontier import (
    FrontierCandidate,
    load_frontier_snapshot,
    write_frontier_snapshot,
)


def test_write_and_load_frontier_snapshot(tmp_path: Path):
    out = write_frontier_snapshot(
        tmp_path,
        active_frontier="SC-CONCEPT-0006",
        selection_note="SC-CONCEPT-0006 remains the strongest bounded Level-4 proof surface.",
        source_artifacts=[
            "docs/proof-path-ladder.md",
            "plans/today_frontier_2026-04-06.md",
            "plans/symbolic_maps_level4_scoring_pass_v0.md",
        ],
        frontier_backlog=[
            FrontierCandidate(
                concept_id="SC-CONCEPT-0006",
                title="symbolic-maps-and-narrative-invariants",
                rank=1,
                proof_path_level=3,
                target_level=4,
                status="candidate",
                rationale="Strongest discriminating benchmark candidate after scoring pass.",
                next_move="Run one more bounded heterogeneous benchmark pass.",
                failure_condition="Arm A advantage collapses on the next bounded pass.",
                evidence=("plans/symbolic_maps_level4_scoring_pass_v0.md",),
            ),
            FrontierCandidate(
                concept_id="SC-CONCEPT-0003",
                title="topological-memory-retrieval",
                rank=2,
                proof_path_level=2,
                target_level=3,
                status="candidate",
                rationale="Still promising, but less immediate proof leverage than SC-CONCEPT-0006.",
                next_move="Tighten benchmark framing without reopening the frontier.",
                failure_condition="Still too thesis-heavy to support a discriminating test.",
            ),
        ],
    )
    assert out.exists()

    snapshot = load_frontier_snapshot(tmp_path)
    assert snapshot is not None
    assert snapshot.active_frontier == "SC-CONCEPT-0006"
    assert [candidate.concept_id for candidate in snapshot.frontier_backlog] == [
        "SC-CONCEPT-0006",
        "SC-CONCEPT-0003",
    ]
    assert snapshot.frontier_backlog[0].status == "active"
    assert snapshot.frontier_backlog[1].status == "candidate"


def test_frontier_snapshot_requires_rank_one_match(tmp_path: Path):
    with pytest.raises(ValueError, match="active_frontier"):
        write_frontier_snapshot(
            tmp_path,
            active_frontier="SC-CONCEPT-0008",
            frontier_backlog=[
                FrontierCandidate(
                    concept_id="SC-CONCEPT-0006",
                    title="symbolic-maps-and-narrative-invariants",
                    rank=1,
                    proof_path_level=3,
                    target_level=4,
                )
            ],
        )


def test_frontier_snapshot_requires_contiguous_ranks(tmp_path: Path):
    with pytest.raises(ValueError, match="contiguous"):
        write_frontier_snapshot(
            tmp_path,
            active_frontier="SC-CONCEPT-0006",
            frontier_backlog=[
                FrontierCandidate(
                    concept_id="SC-CONCEPT-0006",
                    title="symbolic-maps-and-narrative-invariants",
                    rank=2,
                    proof_path_level=3,
                    target_level=4,
                )
            ],
        )
