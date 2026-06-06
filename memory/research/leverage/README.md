# Causal leverage cards

This directory holds causal leverage cards (`leverage-card/v1`) and the evidence
payloads emitted by `scripts/run_leverage_card.py`.

See `docs/22_causal_leverage_card_protocol.md` for the schema, lifecycle, and
matrix-wiring rules.

Layout:

```
YYYY-MM-DD-NNN-<slug>.json           # the card
YYYY-MM-DD-NNN-<slug>.evidence.json  # scorer output (generated)
```

Generated evidence files are committed alongside the card so matrix rows can
link a stable path; regenerate with:

```
python3 scripts/run_leverage_card.py <card.json> --emit-evidence
```
