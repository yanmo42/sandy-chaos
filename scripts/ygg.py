#!/usr/bin/env python3
"""Minimal Ygg continuity CLI.

Commands:
- status: show latest checkpoint
- checkpoint: write a new continuity checkpoint
- promote: alias for checkpoint with a required promotion target
- resume-status: show latest cross-session resume artifact
- resume: write a durable cross-session resume artifact
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nfem_suite.intelligence.ygg import (
    load_latest_checkpoint,
    load_latest_resume_artifact,
    write_checkpoint,
    write_resume_artifact,
)


def cmd_status(_: argparse.Namespace) -> int:
    checkpoint = load_latest_checkpoint(ROOT)
    if checkpoint is None:
        print(json.dumps({"status": "empty", "message": "no Ygg checkpoints yet"}, indent=2))
        return 0
    print(json.dumps(checkpoint.to_dict(), indent=2))
    return 0


def cmd_resume_status(_: argparse.Namespace) -> int:
    artifact = load_latest_resume_artifact(ROOT)
    if artifact is None:
        print(json.dumps({"status": "empty", "message": "no Ygg resume artifacts yet"}, indent=2))
        return 0
    print(json.dumps(artifact.to_dict(), indent=2))
    return 0


def cmd_checkpoint(args: argparse.Namespace) -> int:
    path = write_checkpoint(
        ROOT,
        lane=args.lane,
        summary=args.summary,
        disposition=args.disposition,
        promotion_target=args.promotion_target,
        evidence=args.evidence,
        next_action=args.next_action,
    )
    print(json.dumps({"status": "ok", "checkpoint": str(path.relative_to(ROOT))}, indent=2))
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    path = write_checkpoint(
        ROOT,
        lane=args.lane,
        summary=args.summary,
        disposition=args.disposition,
        promotion_target=args.promotion_target,
        evidence=args.evidence,
        next_action=args.next_action,
    )
    print(json.dumps({"status": "ok", "promotion_checkpoint": str(path.relative_to(ROOT))}, indent=2))
    return 0


def cmd_resume(args: argparse.Namespace) -> int:
    path = write_resume_artifact(
        ROOT,
        lane=args.lane,
        branch_purpose=args.branch_purpose,
        branch_scope=args.branch_scope,
        current_state=args.current_state,
        summary=args.summary,
        branch_outcome_class=args.branch_outcome_class,
        disposition=args.disposition,
        promotion_target=args.promotion_target,
        next_action=args.next_action,
        blocker=args.blocker,
        evidence=args.evidence,
        relevant_artifact_refs=args.artifact_ref,
    )
    print(json.dumps({"status": "ok", "resume_artifact": str(path.relative_to(ROOT))}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ygg", description="Ygg continuity command surface")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="show latest checkpoint")
    status.set_defaults(func=cmd_status)

    resume_status = sub.add_parser("resume-status", help="show latest resume artifact")
    resume_status.set_defaults(func=cmd_resume_status)

    checkpoint = sub.add_parser("checkpoint", help="write continuity checkpoint")
    checkpoint.add_argument("--lane", required=True)
    checkpoint.add_argument("--summary", required=True)
    checkpoint.add_argument("--disposition", required=True)
    checkpoint.add_argument("--promotion-target", default="")
    checkpoint.add_argument("--evidence", default="")
    checkpoint.add_argument("--next-action", default="")
    checkpoint.set_defaults(func=cmd_checkpoint)

    promote = sub.add_parser("promote", help="write promotion-oriented checkpoint")
    promote.add_argument("--lane", required=True)
    promote.add_argument("--summary", required=True)
    promote.add_argument("--disposition", required=True, choices=["TODO_PROMOTE", "DOC_PROMOTE", "POLICY_PROMOTE", "ESCALATE"])
    promote.add_argument("--promotion-target", required=True)
    promote.add_argument("--evidence", default="")
    promote.add_argument("--next-action", default="")
    promote.set_defaults(func=cmd_promote)

    resume = sub.add_parser("resume", help="write cross-session resume artifact")
    resume.add_argument("--lane", required=True)
    resume.add_argument("--branch-purpose", required=True)
    resume.add_argument("--branch-scope", default="")
    resume.add_argument("--current-state", required=True)
    resume.add_argument("--summary", default="")
    resume.add_argument("--branch-outcome-class", required=True, choices=["local", "promotable", "policy-relevant", "blocked"])
    resume.add_argument("--disposition", required=True, choices=["DROP_LOCAL", "LOG_ONLY", "TODO_PROMOTE", "DOC_PROMOTE", "POLICY_PROMOTE", "ESCALATE"])
    resume.add_argument("--promotion-target", required=True, choices=["todo", "docs", "workflow", "foundations", "tests/config", "log-only"])
    resume.add_argument("--next-action", required=True)
    resume.add_argument("--blocker", default="")
    resume.add_argument("--evidence", default="")
    resume.add_argument("--artifact-ref", action="append", default=[])
    resume.set_defaults(func=cmd_resume)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
