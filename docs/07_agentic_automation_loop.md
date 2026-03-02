# 07 Agentic Automation Loop (Human ↔ Repo ↔ Telegram)

## 1) Purpose

Define a closed operational loop for Sandy Chaos where assistant work on the repo is automatically summarized and pushed to operator on Telegram.

## 2) Loop model (three-layer alignment)

- **Fast loop (per interaction):** quality checks + immediate corrections.
- **Meso loop (daily):** summarize completed work, blockers, and policy tweaks.
- **Slow loop (weekly):** distill stable behavior updates into workflow/policy docs.

## 3) Operational flow

1. Human gives objective/constraints.
2. Agent executes repo work and logs outcomes.
3. Scheduler triggers daily/weekly loop checks.
4. Digest text is generated and queued.
5. Digest is pushed to Telegram (operator-chat chat).
6. Human feedback modifies next loop policy.

## 4) Scheduler policy

- **Primary:** OpenClaw heartbeat (context-aware batching)
- **Fallback:** host cron (strict timing/failover)

## 5) Notification policy

Target chat: `telegram:<REDACTED_CHAT_ID>`

Guardrails:
- max 1 daily digest
- max 1 weekly distill
- suppress duplicates from repeated triggers

## 6) Minimal implementation backlog

- [x] Add `run` mode to `scripts/self_improve.py`
- [x] Add `memory/self_improve_state.json`
- [x] Add `memory/notification_outbox.md`
- [x] Add Telegram sender integration for rich full-pass digests
- [x] Add dry-run preview mode for notification text
- [x] Add systemd user timer for 5-minute unattended cycles (`ops/systemd/` + installer script)
- [ ] Enforce runtime rate-limit and quiet-hour checks in sender

## 7) Safety and reliability constraints

- All improvements must be forward-causal and evidence-based.
- No policy promotion without repeated success over multiple days.
- Notification failures must not block core repo work.

## 8) Orchestrator v1 (custom agent lanes + subagent contracts)

v1 adds a coordinator prep step that generates explicit task contracts for OpenClaw subagents.

### Files

- `config/agents.json` — lane definitions (planner/builder/verifier/reporter), model pinned to `openai-codex/gpt-5.3-codex`
- `config/orchestrator.json` — selection policy, gates, output paths
- `scripts/automation_orchestrator.py` — builds task plan JSONL + cycle summary

### Run

```bash
python3 scripts/automation_orchestrator.py
```

Outputs:

- `memory/orchestrator_task_plan.jsonl`
- `memory/orchestrator_cycle_summary.md`

### Execution pattern

1. Coordinator script selects top open/partial TODO tasks.
2. For each selected item, it emits a bounded task contract:
   - goal
   - constraints
   - definition of done
   - validation command
3. OpenClaw main session spawns subagents from these contracts (`sessions_spawn`) and routes by lane.
4. Reporter lane composes daily/weekly Telegram summary after completion.

### Why this shape

- Keeps the automation deterministic and inspectable.
- Separates **planning**, **building**, **verification**, and **reporting** concerns.
- Allows gradual expansion to fully automatic spawn execution later.


## 9) Auto-spawn executor (v1.5 bridge)

Added `scripts/orchestrator_autospawn.py` to consume `memory/orchestrator_task_plan.jsonl` and emit concrete spawn payloads:

- Input: `memory/orchestrator_task_plan.jsonl`
- Output: `memory/orchestrator_spawn_requests.json`
- Log: `memory/orchestrator_dispatch_log.jsonl`

Run:

```bash
python3 scripts/orchestrator_autospawn.py --limit 3
```

This is a bridge design: repo automation prepares deterministic `sessions_spawn` payloads, then the active OpenClaw coordinator executes them.


### One-command wrapper

Use:

```bash
./scripts/run_sandy_cycle.sh 3
```

This wraps:

1. `automation_orchestrator.py`
2. `orchestrator_autospawn.py --limit 3`

and leaves dispatch-ready artifacts for immediate `sessions_spawn` execution.


## 10) Probabilistic 5-minute cadence (4-6 min window)

The automation timer now models a flexible "around 5 minutes" cadence:

- `OnUnitActiveSec=4min`
- `RandomizedDelaySec=2min`

So each cycle is sampled from a **4-6 minute** interval, centered near 5 minutes.
This preserves the symbolic/operational target of 5 while introducing jitter to avoid rigid synchronization effects.

