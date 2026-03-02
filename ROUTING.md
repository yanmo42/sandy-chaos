# Sandy Chaos · Prompt Routing Guide

Use per-prompt routing so model effort matches task difficulty.

## Rule of thumb

- Default: `openai-codex/gpt-5.3-codex` + `/think low`
- Escalate thinking only for deep conceptual work
- Keep routine engineering fast

## Task routing table

## A) Engineering execution (default)

Use for:
- implementation
- refactors
- bugfixes
- test writing

Settings:

```text
/model openai-codex/gpt-5.3-codex
/think low
```

## B) Deep theory / formal analysis

Use for:
- theorem/claim structure
- critique synthesis
- causality boundary reasoning
- falsification design

Settings:

```text
/think high
```

If still shallow:

```text
/think xhigh
```

## C) Fast operational actions

Use for:
- path checks
- file listings
- status queries
- simple command execution

Settings:

```text
/think off
```

## Session setup recommendation

### `sandy-build`

```text
/session sandy-build
/think low
```

### `sandy-research`

```text
/session sandy-research
/think high
```

## Prompt templates

### Build template

```text
Goal:
Scope:
Constraints:
Validation command(s):
Definition of done:
```

### Research template

```text
Claim tier:
Question:
Assumptions:
Required evidence:
Failure condition:
Output format:
```
