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

## 3) Daily loop

1. State objective + acceptance criteria
2. Ask for short plan + file map
3. Implement in small increments
4. Run validation commands
5. Summarize result + next step
6. Commit

## 4) Recommended prompt format

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

## 5) Suggested terminal commands

From repo root (`~/dev/sandy-chaos`):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r nfem_suite/requirements.txt
export PYTHONPATH=$PYTHONPATH:.
python -m nfem_suite.main
python -m cosmic_comm.main
```

## 6) Git discipline

- Keep commits small and hypothesis-linked
- Include validation note in commit message/body when relevant
- Prefer reversible changes over large rewrites

Example commit flow:

```bash
git status
git add <files>
git commit -m "feat: <small scoped change>"
```

## 7) Useful OpenClaw commands in chat

```text
/status
/model status
/think low|high|xhigh
/verbose off
/reasoning off
```

## 8) Escalate thinking only when needed

- Routine coding / grep / edits: `low` or `minimal`
- Architecture / formalization / critiques: `high` or `xhigh`
- Keep default in build lane at `low` for speed

## 9) Automation loops (daily + weekly)

### Default trigger source

- Primary: OpenClaw heartbeat
- Optional: host cron when strict timing is needed

Run automation check:

```bash
python3 scripts/self_improve.py run --scheduler heartbeat
```

Preview notification text without sending/queuing:

```bash
python3 scripts/self_improve.py run --scheduler heartbeat --dry-run
```

### Cadence

- Daily digest scaffold: once per day (`*-meso-review.md`)
- Weekly distill scaffold: once per ISO week (`*-slow-distill.md`)

### Missed-run detection

State is tracked in `memory/self_improve_state.json`:

- `last_run.daily`, `last_run.weekly`
- `missed_runs.daily`, `missed_runs.weekly`
- recurring `policy_tweak_counts`

### Proactive summary routing

Summaries are queued in `memory/notification_outbox.md`.
If Telegram routing is configured in the active OpenClaw session, deliver queued summaries as:

- Daily digest summary
- Weekly distill summary

