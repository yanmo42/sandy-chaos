#!/usr/bin/env python3
"""Minimal Ygg continuity CLI.

Commands:
- status: show latest checkpoint
- checkpoint: write a new continuity checkpoint
- promote: alias for checkpoint with a required promotion target
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nfem_suite.intelligence.ygg import load_latest_checkpoint, write_checkpoint


def cmd_status(_: argparse.Namespace) -> int:
    checkpoint = load_latest_checkpoint(ROOT)
    if checkpoint is None:
        print(json.dumps({"status": "empty", "message": "no Ygg checkpoints yet"}, indent=2))
        return 0
    print(json.dumps(checkpoint.to_dict(), indent=2))
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ygg", description="Ygg continuity command surface")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="show latest checkpoint")
    status.set_defaults(func=cmd_status)

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

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
