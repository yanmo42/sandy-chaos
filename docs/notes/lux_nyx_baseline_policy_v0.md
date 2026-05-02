# Lux–Nyx Pilot Baseline Policy v0

## Status

Baseline decision note, 2026-05-02.

## Claim tier

**Defensible now:** the repo has instrumentation for Lux–Nyx pilot metrics, but it does not contain a trustworthy pre-Lux-Nyx historical baseline artifact.

**Plausible but unproven:** a prospective baseline window can become useful after enough explicitly recorded operator events accumulate.

**Not allowed:** manufacturing a baseline from zero counters or current empty state just to satisfy a TODO. That would make later promotion verdicts look quantitative while resting on a synthetic comparison.

## Decision

Do **not** freeze a pre-Lux-Nyx baseline unless explicit historical evidence is recovered.

Until then, baseline comparison should use one of these honest modes:

1. **baseline-unconfigured** — default state; pilot report can show live counters but cannot claim lift.
2. **recovered historical baseline** — allowed only if a dated artifact with pre-Lux-Nyx event counts is found.
3. **prospective baseline window** — allowed after a declared window of future observed events is collected before any promotion decision uses it.

## Operational rules

- `state/lux_nyx/metrics.json` remains generated/ignored runtime state.
- `scripts/lux_nyx_pilot_baseline.py --from-current` is permitted only for explicit proxy experiments, not canonical promotion evidence.
- Promotion verdicts must remain gated by valid counters, configured baseline, sufficient sample size, sufficient resolution coverage, and no worse headline metric.

## Failure conditions

Demote this policy if:

1. a real pre-Lux-Nyx baseline artifact is found and this note is not updated,
2. automation silently uses zero/current counters as promotion evidence,
3. pilot metrics are promoted without satisfying the configured sample gates,
4. accepted/corrected suggestions stop consuming unresolved suggestions one-for-one.

## Next action

Collect prospective operator events with the CLI or workflow hooks, then freeze a clearly labeled prospective baseline only after the sampling window is explicit.
