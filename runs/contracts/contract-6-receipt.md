# Contract 6 Receipt — Kerr↔Channel Wiring or Downscope (AUD-006)

**Date:** 2026-06-14
**Branch taken:** DOWNSCOPE

## Decision basis

- `runs/contracts/contract-2-receipt.md` does not exist.
- T-015 in `docs/theory-implementation-matrix.md` is `REVIEW` (not PASS).
- Contract 2 has not completed the required rebuild with invariant observable and Sagnac baseline.

## Key changes

1. **docs/02_tempo_tracer_protocol.md §2.2** — Added `[A-005 DOWNSCOPE 2026-06-14]` blockquote: Kerr geometry illustrative only pending Contract-2 T-015 PASS.

2. **docs/math_foundations_zf.md §9** — Added `[A-005 DOWNSCOPE 2026-06-14]` blockquote at section header: load-bearing curvature claim suspended.

3. **docs/assumptions_register.md** — A-004 and A-005 status updated to `DOWNSCOPED 2026-06-14`. A-004 consequence field notes affine-parameter proxy non-discriminating. A-005 consequence field requires Contract-2 invariant-observable rebuild before reinstatement.

4. **nfem_suite/simulation/communication/vortex_channel.py** — Module docstring extended with `NOTE [A-005 DOWNSCOPE 2026-06-14]`: `backward_attenuation = 0.5` is an empirically unconstrained placeholder scalar, not a Kerr-derived quantity.

## Validation results

- `python3 scripts/validate_foundations.py --payload-file memory/research/kerr_asymmetry_2026-03/t015_ledger_repair_evidence.json` → `decision=REVIEW`, `ok=true`, no hard gate violations.
- `python3 -m pytest tests/ -q` → 346 passed, 6 subtests passed.

## Branch

`contracts/contract-6-kerr-channel` — pushed to origin.
