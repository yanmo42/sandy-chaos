# Φ Fluid Probe v0 — Single-Probe Downstream Deflection

## Claim tier

**Defensible now:** the repo contains a deterministic, bounded simulation probe that applies a localized observer-coupling perturbation to a toy velocity field and measures downstream transverse deflection.

**Not claimed:** this is not evidence for retrocausality, non-local signaling, or physical fluid dynamics fidelity. It is a code-level pressure test for the read/write observer-coupling surface.

## Scenario

SPDD v0 means **single-probe downstream deflection**.

- State variable affected: nodewise 2D velocity field.
- Coupling surface: `ObserverCouplingConfig` from `nfem_suite.simulation.agents.observer_coupling`.
- Coupling scale λ: `ObserverCouplingConfig.gain`.
- Default implementation: `nfem_suite.simulation.flows.phi_fluid_probe.run_spdd`.
- Observable: downstream transverse velocity change, reported as `deflection_by_distance` and `max_downstream_deflection`.

The perturbation is forward-causal inside the simulation step: the probe changes the present velocity field locally, then downstream observables are computed from the resulting perturbed field.

## Boundedness

The implementation clips perturbation magnitude by `ObserverCouplingConfig.max_perturbation` and reports whether the observed maximum stayed within that bound plus a numerical `noise_floor`.

## Falsification / failure conditions

This probe should be treated as failed if any of the following occur:

1. A zero-gain probe produces downstream deflection above the declared noise floor.
2. A nonzero-gain probe produces no reproducible downstream transverse deflection in the configured grid.
3. The realized perturbation exceeds `max_perturbation + noise_floor`.
4. Repeated runs with the same config produce different reported deflection values.
5. Documentation or downstream claims treat this toy probe as physical evidence rather than bounded implementation evidence.

## Validation

Current validation surface:

```bash
python3 -m unittest tests.test_phi_fluid_probe -v
```

The test covers deterministic grid construction, nonzero-gain deflection, zero-gain null behavior, perturbation boundedness, and reproducibility.
