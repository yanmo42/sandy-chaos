# 07 Agentic Automation Loop (Human ↔ Repo ↔ Telegram)

## 1) Purpose

Define a closed operational loop for Sandy Chaos where assistant work on the repo is automatically summarized and pushed to the designated operator via Telegram.

## 2) Loop model (three-layer alignment)

- **Fast loop (per interaction):** quality checks + immediate corrections.
- **Meso loop (daily):** summarize completed work, blockers, and policy tweaks.
- **Slow loop (weekly):** distill stable behavior updates into workflow/policy docs.

## 3) Operational flow

1. Human gives objective/constraints.
2. Agent executes repo work and logs outcomes.
3. Scheduler triggers loop checks.
4. Orchestrator builds bounded task contracts.
5. Spawn-request artifacts are generated and dispatch is attempted via OpenClaw session bridge.
6. Digest text is generated (outbox + optional Telegram delivery).
7. Human feedback modifies next loop policy.

## 4) Scheduler policy

- **Primary:** OpenClaw heartbeat (context-aware batching)
- **Fallback:** host cron (strict timing/failover)

## 5) Notification policy

Default target chat (when enabled): value from `OPENCLAW_TELEGRAM_TARGET`

Current operating mode:
- Full-pass Telegram emission is enabled in the systemd service wiring.
- Digests are also generated in `memory/notification_outbox.md`.

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
- [x] Enforce runtime rate-limit and quiet-hour checks in sender

## 7) Safety and reliability constraints

- All improvements must be forward-causal and evidence-based.
- No policy promotion without repeated success over multiple days.
- Notification failures must not block core repo work.

## 8) Orchestrator v1 (custom agent lanes + subagent contracts)

v1 adds a coordinator prep step that generates explicit task contracts for OpenClaw subagents.

### Files

- `config/agents.json` — lane definitions (planner/builder/verifier/reporter), model pinned to `openai-codex/gpt-5.3-codex`
- `config/orchestrator.json` — selection policy, gates, output paths, and dispatch target agent
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
   - disposition
   - promotion target
   - constraints
   - definition of done
   - validation command
3. OpenClaw coordinator dispatches these contracts through the Gateway `agent` bridge and routes by lane.
4. Reporter lane composes daily/weekly Telegram summary after completion.

### Why this shape

- Keeps the automation deterministic and inspectable.
- Separates **planning**, **building**, **verification**, and **reporting** concerns.
- Allows gradual expansion to fully automatic spawn execution later.


## 9) Auto-spawn executor (v2 direct dispatch)

`scripts/orchestrator_autospawn.py` consumes `memory/orchestrator_task_plan.jsonl`, emits concrete spawn payloads, and can dispatch them directly via the OpenClaw Gateway `agent` API.

- Input: `memory/orchestrator_task_plan.jsonl`
- Output: `memory/orchestrator_spawn_requests.json`
- Log: `memory/orchestrator_dispatch_log.jsonl`

Prepare only:

```bash
python3 scripts/orchestrator_autospawn.py --limit 3
```

Prepare + dispatch:

```bash
python3 scripts/orchestrator_autospawn.py --limit 3 --execute
```

Dry-run dispatch path (no API call):

```bash
python3 scripts/orchestrator_autospawn.py --limit 3 --execute --dry-run
```


### One-command wrapper

Use:

```bash
./scripts/run_sandy_cycle.sh 3
```

This wraps:

1. `automation_orchestrator.py`
2. `orchestrator_autospawn.py --limit 3`

and leaves dispatch-ready artifacts for immediate coordinator dispatch execution.


### Validation policy source of truth

Validation command routing + gate policy are now configured in `config/orchestrator.json` under:

- `validation.commands.default`
- `validation.commands.byLane`
- `validation.policy`

This makes tuning and audits configuration-driven instead of hardcoded in scripts.

### Prompting template source of truth

Task prompt structure is also config-driven in `config/orchestrator.json` under:

- `prompting.template`
- `prompting.globalConstraints`
- `prompting.byLane`
- `prompting.outputContract`
- `prompting.forbidden`

`orchestrator_autospawn.py` renders subagent contract prompts from this schema, and `self_improve.py` can re-render from `prompt_context` during dispatch if needed.

### Dispatch target source of truth

Gateway agent dispatch now resolves its target from `config/orchestrator.json` under:

- `dispatch.agentId`

If unset, the scripts fall back to `OPENCLAW_AGENT_ID`, then the repo root name.
This prevents unattended cycles from accidentally targeting the wrong local agent runtime.

## 10) Probabilistic 5-minute cadence (4-6 min window)

The automation timer now models a flexible "around 5 minutes" cadence:

- `OnUnitActiveSec=4min`
- `RandomizedDelaySec=2min`

So each cycle is sampled from a **4-6 minute** interval, centered near 5 minutes.
This preserves the symbolic/operational target of 5 while introducing jitter to avoid rigid synchronization effects.


## 11) Full automation wiring (service-level)

`ops/systemd/sandy-automation.service` now runs:

```bash
python3 scripts/self_improve.py full-pass \
  --scheduler host-cron \
  --with-orchestration \
  --with-dispatch \
  --dispatch-limit 3 \
  --send-telegram
```

This means each timer cycle executes:

1. cadence checks,
2. orchestrator task-plan generation,
3. spawn-request generation,
4. coordinator-side Gateway `agent` dispatch in the active OpenClaw runtime,
5. lane-aware productivity digest generation (outbox-first, Telegram optional).

## 12) Auto-improvement definition (repo-native)

To keep autonomy aligned with Sandy Chaos goals, each cycle should score itself on **project-functional outcomes**, not just loop health.

### A) Capability lanes (what "improvement" means)

1. **Theory lane** (`docs/`)
   - Improves formal clarity, claim-tier discipline, falsification criteria.
2. **Continuity lane** (`memory/`, retrieval tooling, continuity infrastructure)
   - Improves inspectable recall, retrieval provenance, and continuity-aware automation.
3. **Simulation lane** (`nfem_suite/`)
   - Improves causal-observer coupling implementation and metrics.
4. **Validation lane** (`tests/`)
   - Adds/updates tests proving forward-causal behavior and asymmetry claims.
5. **Ops lane** (`scripts/`, `ops/`, `config/`)
   - Improves orchestration reliability, scheduling, and digest quality.

### B) Cycle acceptance gates

A full pass counts as "productive" only if at least one of these is true:
- TODO state advanced (open→partial/done), or
- test/validation coverage improved, or
- docs/spec quality improved with falsification condition updates, or
- orchestration reliability improved (fewer failures/cleaner dispatch).

### C) Telegram digest minimum fields

Every `[SANDY-FULLPASS]` update should include:
- what project lane(s) were touched,
- concrete files changed,
- validation commands run + outcomes,
- TODO delta vs previous snapshot,
- branch outcome classes + dispositions + promotion targets observed in the current orchestrator plan,
- next best action (single highest-leverage task).

This keeps the automation loop tied to real Sandy Chaos progress instead of generic background churn.

## 13) Current execution setup (agent automation as implemented)

### Active scheduler

- `systemd --user` timer: `sandy-automation.timer`
- cadence: probabilistic 4-6 minute window around a 5-minute center
- unit: `sandy-automation.service` (oneshot)

### What runs each cycle

1. `self_improve.py full-pass`
2. `automation_orchestrator.py` builds task contracts from TODO priorities
3. `orchestrator_autospawn.py` emits spawn-request payloads
4. coordinator dispatch executes Gateway `agent` calls directly from the active OpenClaw runtime (with session-id telemetry retained for debugging)
5. digest and telemetry are written to memory artifacts

### Core artifacts

- `memory/orchestrator_task_plan.jsonl` (continuity tasks may carry `memory_artifact_ids` so downstream dispatch/runtime evidence cites concrete retrieval and governance artifacts)
- task-plan entries now also carry explicit `disposition` + `promotion_target` fields so non-trivial continuity work cannot end silently
- `memory/orchestrator_spawn_requests.json`
- `memory/orchestrator_dispatch_log.jsonl` (includes `control_mode`, `governance_policy_ref`, `continuity_relevant`, `memory_consulted`, `memory_artifact_ids`, and when applicable `memory_policy_ref` plus `memory_request_provenance` per dispatch event; validator now requires inspectable repo-relative artifact refs, `<request-id>:<source>` provenance formatting, provenance ids that match the dispatch entry id, and artifact-bearing provenance sources only when inspectable artifact refs are actually present)
- `python3 scripts/dispatch_log_validator.py memory/orchestrator_dispatch_log.jsonl` provides a lightweight JSONL pass that reports line-numbered membrane evidence violations before those artifacts are promoted into tests/config review flows
- `memory/orchestrator_cycle_summary.md`
- `memory/self_improve_state.json`
- `memory/notification_outbox.md` (append-only markdown outbox grouped by `## YYYY-MM-DD` with timestamped `### [YYYY-MM-DD HH:MM]` entries)

### Why this matters for temporal forecasting advantage

In Sandy Chaos terms, this automation provides a practical "forecasting edge" by continuously converting near-term structural signals into actionable policy updates, while preserving forward causality:

- **Faster legibility of downstream constraints:** TODO drift, dispatch reliability, and test-state changes are surfaced every cycle.
- **Observer-state updates in bounded time:** each cycle updates policy traces and next actions before backlog noise accumulates.
- **Cross-lane temporal coupling:** theory/simulation/validation/ops signals are co-reported, improving intervention timing.
- **No retrocausal claims:** gains come from higher-frequency inference + disciplined feedback loops, not backward-time effects.

Operationally: the system is useful when it reduces decision latency and increases the proportion of productive interventions per unit time.



## 14) Secrets & portability

Use repo-local secrets for portable setups without committing PII:

1. Copy `.secrets.example.env` -> `.secrets.local.env`
2. Fill values for `OPENCLAW_TELEGRAM_BOT_TOKEN` and `OPENCLAW_TELEGRAM_TARGET`
3. Keep `.secrets.local.env` out of git (already in `.gitignore`)

The systemd service loads:
- `%h/dev/sandy-chaos/.secrets.local.env` (preferred)
- `%h/.config/sandy-chaos/automation.env` (legacy fallback)


## 15) Git push automation guardrails (planned)

Git automation will follow `docs/08_git_automation_protocol.md`.

Key constraints:
- unattended jobs may run normal `git push`, but never force-push
- push only to configured remote/branch
- require validation gate before push
- log failures with non-sensitive summaries
