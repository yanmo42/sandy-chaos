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



## 10) Git automation goals (planned)

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
