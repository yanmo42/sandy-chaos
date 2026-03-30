from pathlib import Path

import pytest

from nfem_suite.intelligence.ygg.continuity import (
    load_latest_checkpoint,
    load_latest_resume_artifact,
    write_checkpoint,
    write_resume_artifact,
)


def test_write_and_load_checkpoint(tmp_path: Path):
    out = write_checkpoint(
        tmp_path,
        lane="Symbolic Maps",
        summary="Validated and normalized starter lane",
        disposition="DOC_PROMOTE",
        promotion_target="docs",
        evidence="compile/import/test passed",
        next_action="build retrieval stack",
    )
    assert out.exists()

    checkpoint = load_latest_checkpoint(tmp_path)
    assert checkpoint is not None
    assert checkpoint.lane == "Symbolic Maps"
    assert checkpoint.disposition == "DOC_PROMOTE"
    assert checkpoint.promotion_target == "docs"


def test_write_and_load_resume_artifact(tmp_path: Path):
    out = write_resume_artifact(
        tmp_path,
        lane="continuity",
        branch_purpose="Land the first durable resume helper",
        branch_scope="scripts/ygg.py, nfem_suite/intelligence/ygg/continuity.py, tests/test_ygg.py",
        current_state="Helper is implemented locally and needs targeted validation before commit.",
        summary="Resume helper is ready for targeted validation.",
        branch_outcome_class="policy-relevant",
        disposition="POLICY_PROMOTE",
        promotion_target="tests/config",
        next_action="Run targeted validation, then stage the scoped patch.",
        blocker="Need to confirm the repo test runner path in this environment.",
        evidence="Library + CLI surface both added.",
        relevant_artifact_refs=[
            "scripts/ygg.py",
            "nfem_suite/intelligence/ygg/continuity.py",
            "tests/test_ygg.py",
            "scripts/ygg.py",
        ],
    )
    assert out.exists()
    assert out.parent.name == "resume"

    artifact = load_latest_resume_artifact(tmp_path)
    assert artifact is not None
    assert artifact.branch_purpose == "Land the first durable resume helper"
    assert artifact.branch_outcome_class == "policy-relevant"
    assert artifact.disposition == "POLICY_PROMOTE"
    assert artifact.promotion_target == "tests/config"
    assert list(artifact.relevant_artifact_refs) == [
        "scripts/ygg.py",
        "nfem_suite/intelligence/ygg/continuity.py",
        "tests/test_ygg.py",
    ]


def test_resume_artifact_requires_valid_contract(tmp_path: Path):
    with pytest.raises(ValueError, match="branch_outcome_class"):
        write_resume_artifact(
            tmp_path,
            lane="continuity",
            branch_purpose="Broken artifact",
            current_state="Missing a valid outcome class.",
            branch_outcome_class="maybe",
            disposition="POLICY_PROMOTE",
            promotion_target="workflow",
            next_action="Do the real thing.",
        )
