#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIMIT="${1:-3}"

cd "$ROOT"

echo "[1/2] Building orchestrator task plan..."
python3 scripts/automation_orchestrator.py

echo "[2/2] Building spawn requests..."
python3 scripts/orchestrator_autospawn.py --limit "$LIMIT"

echo
echo "✅ Sandy cycle artifacts prepared"
echo "- Task plan:    $ROOT/memory/orchestrator_task_plan.jsonl"
echo "- Spawn reqs:   $ROOT/memory/orchestrator_spawn_requests.json"
echo "- Cycle summary:$ROOT/memory/orchestrator_cycle_summary.md"
echo
echo "Next: dispatch spawn requests via OpenClaw Gateway agent bridge."
