from pathlib import Path

from nfem_suite.intelligence.ygg.continuity import load_latest_checkpoint, write_checkpoint


def test_write_and_load_checkpoint(tmp_path: Path):
    out = write_checkpoint(
        tmp_path,
        lane="Symbolic Maps",
        summary="Validated and normalized starter lane",
        disposition="DOC_PROMOTE",
        promotion_target="docs/symbolic-maps/",
        evidence="compile/import/test passed",
        next_action="build retrieval stack",
    )
    assert out.exists()

    checkpoint = load_latest_checkpoint(tmp_path)
    assert checkpoint is not None
    assert checkpoint.lane == "Symbolic Maps"
    assert checkpoint.disposition == "DOC_PROMOTE"
