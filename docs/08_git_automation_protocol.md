# 08 Git Automation Protocol (Safe Auto-Push)

## Purpose

Define a reproducible, low-risk method for automating git pushes from Sandy automation cycles.

This protocol is intentionally conservative:
- never stores secrets in tracked files,
- never force-pushes from unattended automation,
- never bypasses validation gates.

## Scope

Applies to automated push behavior for this repository only.

## Preconditions

Before enabling auto-push, ensure all of the following are true:

1. SSH auth works in the same user context as systemd automation.
2. Repo remote uses SSH (`git@github.com:owner/repo.git`).
3. Local secrets file exists (`.secrets.local.env`) and is gitignored.
4. Push workflow has been tested manually end-to-end at least once.

## Security model

Sensitive values are loaded from local environment files only:
- preferred: `.secrets.local.env` (repo-local, gitignored)
- fallback: `~/.config/sandy-chaos/automation.env`

Do not commit:
- personal names
- chat IDs
- bot tokens
- absolute home paths

Use placeholders in docs and tracked configs.

## Automation goals

### Goal A: Deterministic push policy

Auto-push should only target:
- one branch (default `main`)
- one remote (default `origin`)

No tag pushes, no force pushes, no branch creation from unattended runs.

### Goal B: Validation gate before push

A push is allowed only if:
1. working tree has changes,
2. validation command(s) pass,
3. commit is created with scoped message,
4. remote is reachable.

If any gate fails, skip push and log the reason.

### Goal C: Safe failure behavior

On failure:
- keep local commit(s),
- do not retry in a tight loop,
- append structured error to automation logs,
- notify via digest channel (non-sensitive summary).

### Goal D: Reproducible configuration

Use environment variables (from local secrets file) to configure behavior:

- `GIT_AUTOPUSH_ENABLED` (`0|1`)
- `GIT_AUTOPUSH_REMOTE` (default `origin`)
- `GIT_AUTOPUSH_BRANCH` (default `main`)
- `GIT_AUTOPUSH_REQUIRE_CLEAN_BASE` (`0|1`)
- `GIT_AUTOPUSH_VALIDATE_CMD` (optional)

These are optional until implementation is complete.

## Proposed execution order (when implemented)

1. `git fetch <remote> <branch>`
2. Optional base check (`require_clean_base`): local branch is not behind remote
3. Run validation command
4. `git add` scoped files
5. `git commit -m "..."` (skip if no changes)
6. `git push <remote> <branch>`
7. Log + digest summary

For continuity architecture purposes, this execution order should be read as a cadence map rather than only a shell sequence:

- fetch, validation, staging, commit creation, and push attempts operate at the **edge / fast** layer because they are local, reversible run-time actions,
- structured logs, digest summaries, and operator review cues operate at the **bridge / meso** layer because they summarize and route the run's outcome,
- branch policy, remote policy, and validation requirements operate at the **spine / slow** layer because they define the durable rules the run must obey.

That mapping stays strictly forward-causal: fast git-run artifacts can feed bridge summaries, and bridge review can justify slow policy edits later, but a single unattended run should not imply raw edge activity directly rewriting spine policy.

## Non-goals

- No automatic history rewrites
- No automatic force pushes
- No secret rotation in git hooks
- No changes to remote repository settings

## Rollout plan

1. Document protocol (this file)
2. Add dry-run mode for git push stage
3. Add guardrail checks + structured logs
4. Enable `GIT_AUTOPUSH_ENABLED=1` only after manual verification

## Operator checklist

- [ ] `ssh -T git@github.com` succeeds
- [ ] `git remote -v` shows SSH URL
- [ ] `.secrets.local.env` exists and permissions are `600`
- [ ] Validation command is stable
- [ ] Dry-run output reviewed
- [ ] First live auto-push observed in logs
