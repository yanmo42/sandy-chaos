# Sandy Chaos · OpenClaw Workflow

Quick operating guide for running this repo with OpenClaw as an agentic coding partner.

## 1) Enter the project agent

From WebChat or TUI:

```text
/agent sandy
```

Switch back to default assistant:

```text
/agent main
```

## 2) Use two session lanes

Keep work separated for cleaner context.

### Research lane (theory/docs/math)

```text
/session sandy-research
/think high
```

### Build lane (code/tests/refactors)

```text
/session sandy-build
/think low
```

Reset any lane when it gets noisy:

```text
/new
```

## 3) Planner/Builder split (recommended)

For best quality in this setup, separate architecture from implementation:

- **`main` agent = Architect/Planner**
  - requirements clarification
  - design options + tradeoffs
  - acceptance criteria + rollout plan
  - code review framing and risk checks
- **`sandy` agent = Builder/Executor**
  - code edits, tests, refactors, scripts
  - command execution + quick iteration loops
  - implementation summaries per step

Suggested handoff template from `main` → `sandy`:

```text
Task:
Why:
Constraints:
Files in scope:
Acceptance checks:
Definition of done:
```

Cadence:
- Plan in `main` (5–15 min)
- Build in `sandy` (30–60 min blocks)
- Review in `main` before merge/push

## 4) Daily loop

1. State objective + acceptance criteria
2. Ask for short plan + file map
3. Implement in small increments
4. Run validation commands
5. Summarize result + next step
6. Commit

## 5) Recommended prompt format

Use this pattern for implementation tasks:

```text
Goal:
Constraints:
Files allowed:
Definition of done:
```

Use this pattern for theory tasks:

```text
Claim tier: (defensible / plausible / speculative)
Question:
Evidence required:
Falsification condition:
```

### Kickoff prompt (`main` → `sandy`)

```text
Task:
Why this matters now:
Constraints:
Files in scope:
Out of scope:
Acceptance checks (commands + expected result):
Definition of done:
Deliverable format:
- short plan
- patches by file
- validation output
- risks/unknowns
```

Example:

```text
Task: Add a dry-run flag to scripts/self_improve.py full-pass.
Why this matters now: We need safer unattended automation testing.
Constraints: Keep current behavior unchanged when flag is omitted.
Files in scope: scripts/self_improve.py, tests/*
Out of scope: Telegram delivery refactor.
Acceptance checks:
- python3 scripts/self_improve.py full-pass --dry-run exits 0
- Existing full-pass path still sends when --send-telegram is used
Definition of done: Flag works, tests updated, docs note added.
Deliverable format: plan, diffs, command output, risks.
```

## 6) Suggested terminal commands

From repo root (`~/dev/sandy-chaos`):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r nfem_suite/requirements.txt
export PYTHONPATH=$PYTHONPATH:.
python -m nfem_suite.main
python -m cosmic_comm.main
```

## 7) Git discipline

- Keep commits small and hypothesis-linked
- Include validation note in commit message/body when relevant
- Prefer reversible changes over large rewrites

Example commit flow:

```bash
git status
git add <files>
git commit -m "feat: <small scoped change>"
```

## 8) Useful OpenClaw commands in chat

```text
/status
/model status
/think low|high|xhigh
/verbose off
/reasoning off
```

## 9) Escalate thinking only when needed

- Routine coding / grep / edits: `low` or `minimal`
- Architecture / formalization / critiques: `high` or `xhigh`
- Keep default in build lane at `low` for speed

## 10) Automation loops (daily + weekly)

### Current state (implemented now)

Manual commands:

```bash
python3 scripts/self_improve.py fast "miss=<issue>; fix=<change>"
python3 scripts/self_improve.py post-task --context "..." --decision "..." --outcome "..." --policy-tweak "..."  # auto-promotes at >=3 repeats
python3 scripts/self_improve.py promote-tweaks --min-count 3  # manual backfill / audit
python3 scripts/self_improve.py daily
python3 scripts/self_improve.py weekly
```

### Target state (in progress)

Goal: closed loop where repo activity produces scheduled summaries and Telegram pings.

Planned trigger sources:
- Primary: OpenClaw heartbeat
- Fallback: host cron (for strict timing)

Current artifacts:
- `memory/self_improve_state.json` (run timestamps + missed-run tracking)
- `memory/notification_outbox.md` (rich digest queue)
- `templates/daily_digest_notification.md` (explicit daily markdown format)
- `templates/weekly_digest_notification.md` (explicit weekly markdown format)
- `config/automation.json` (notification target/prefix/guardrails)

Telegram delivery:
- Default routing target: `OPENCLAW_TELEGRAM_TARGET` from local secrets
- `scripts/self_improve.py full-pass --send-telegram` sends a rich narrative digest
- Token/chat source for unattended sends: repo-local `.secrets.local.env` (preferred, gitignored) or `~/.config/sandy-chaos/automation.env` (legacy fallback)

### 5-minute unattended automation (systemd user timer)

Install:

```bash
bash scripts/install_automation_timer.sh
```

Then fill local secrets file:

```bash
cp .secrets.example.env .secrets.local.env
chmod 600 .secrets.local.env
nano .secrets.local.env
# set OPENCLAW_TELEGRAM_BOT_TOKEN=...
# set OPENCLAW_TELEGRAM_TARGET=...
```

(legacy fallback still supported: `~/.config/sandy-chaos/automation.env`)

Check status/logs:

```bash
systemctl --user status sandy-automation.timer --no-pager
journalctl --user -u sandy-automation.service -n 50 --no-pager
```



## 11) Git automation goals (planned)

Reference: `docs/08_git_automation_protocol.md`

Intent:
- reproducible auto-push with guardrails
- no secret leakage
- no force-push from unattended runs

Planned controls:
- branch/remote allowlist (`main` + `origin` by default)
- validation gate before push
- structured logs + digest on failure
- dry-run mode before enabling live push


## 12) Research automation workflow (new default)

Reference: `docs/09_research_automation_protocol.md`

When running evidence-heavy work, use this cycle:

1. Create a scoped contract from `templates/research_task_contract.md`
2. Extract source rows using `templates/evidence_extraction_schema.md`
3. Generate synthesis + adversarial check
4. Run falsification pass via `templates/falsification_report.md`
5. Commit artifacts + one next-best action
6. Run mapping verifier:

```bash
python3 scripts/research_verifier.py --synthesis memory/research/<date>-synthesis.md --evidence memory/research/<date>-evidence.csv
```

Recommended artifact location:

- `memory/research/<date>-query.md`
- `memory/research/<date>-evidence.csv`
- `memory/research/<date>-synthesis.md`
- `memory/research/<date>-falsification.md`

Bootstrap command:

```bash
python3 scripts/init_research_cycle.py --slug <topic>
```

This keeps speed high while preserving reproducibility and claim-tier integrity.

## 13) Yggdrasil continuity hygiene

Reference: `docs/12_yggdrasil_continuity_architecture.md`

When work branches across sessions, tools, or cadences, use these rules:

1. **Name the branch purpose early**
   - objective
   - claim tier (when relevant)
   - expected landing zone (`local`, `memory`, `todo`, `docs`, `workflow`, `foundations`, `tests/config`)

2. **Keep edge work cheap**
   - exploratory sessions, scratch notes, provisional scripts, and local experiments do not need immediate promotion
   - prefer reversibility at the edge

3. **End meaningful branches with an explicit disposition**
   - `DROP_LOCAL`
   - `LOG_ONLY`
   - `TODO_PROMOTE`
   - `DOC_PROMOTE`
   - `POLICY_PROMOTE`
   - `ESCALATE`

4. **Use context carry when switching lanes or sessions**
   Leave a short note containing:
   - current state
   - next step
   - blocking unknown
   - intended destination of the result

5. **Promote conservatively toward the spine**
   - use `plans/todo.md` for tactical work
   - use `docs/` for canonical explanation/design
   - use `WORKFLOW.md` for repeatable operator behavior
   - use `FOUNDATIONS.md` only for hardened rules/constraints

6. **Match cadence to consequence**
   - fast loop = edge sensing / local adaptation
   - meso loop = summary / routing / comparison
   - slow loop = consolidation / policy shaping / durable continuity

The goal is not bureaucracy. The goal is to let many local processes stay alive without losing the center of the project.
