# Rimuru Snap Simulation Plan

## Objective

Build a toy simulation that tests whether an adaptive substrate can transition from **reactive local adaptation** into **external coherence organization** after crossing an operational snap threshold.

This artifact is for model exploration, not ontology proof.

## Claim tiers

### Defensible now
- A Rimuru-like figure is a useful metaphor for adaptive-substrate-to-coherence-organizer transitions.
- A toy simulation can test whether thresholded behavioral reorganization appears under simple gradient and capability dynamics.

### Plausible but unproven
- A capability-dependent basin shift may appear when environmental modification becomes cheaper than pure adaptation.
- The resulting transition may be detectable through changes in control radius, action cost, and external order generation.

### Speculative
- That this toy model captures anything physically deep rather than a useful systems metaphor.

## Minimal world

Use a 2D grid world with:
- resource field
- hazard field
- disorder field
- one adaptive agent

## Agent state

The agent tracks:
- position
- energy
- capability score
- sensing radius
- control radius
- predictive depth
- snap state (pre/post)

## Capabilities

Capability acquisition should alter reachable behavior, not just scores. Early version:
- lower movement cost
- reduce hazard penalty
- increase sensing radius
- unlock one-step prediction
- increase control radius

## Snap criterion

Primary operational criterion:

> Snap occurs when the estimated cost of modifying the local environment becomes lower than the rolling cost of surviving reactively for a fixed number of steps.

This should be computed, not manually triggered.

## Post-snap behavior

After snap, unlock a new action class:
- stabilize nearby cells
- reduce local disorder
- create low-cost corridors through hazards

This is the coherence-organizer phase.

## Measurements

Track over time:
- energy
- capability score
- movement cost
- hazard exposure
- control radius
- stabilized cells per step
- local disorder in neighborhood
- ratio of reactive vs organizing actions

## Primary plots

1. capability score over time
2. rolling action cost over time
3. stabilized cells / external order over time
4. detected snap point annotation

## Success condition

The model is useful if it shows a robust threshold region where:
- behavior reorganizes qualitatively,
- external order generation persists,
- and the change is not reducible to a smooth power increase.

## Failure conditions

The model fails if:
- snap is arbitrary rather than operational,
- behavior changes only smoothly,
- organizing behavior is indistinguishable from generic increased power,
- or results are too brittle to parameter variation.

## Smallest build

- Python
- numpy
- matplotlib
- single script
- no ML, no GPUs, no external dependencies beyond scientific Python basics

## First experiments

Sweep:
- resource density
- hazard intensity
- capability acquisition rate
- snap threshold margin

Questions:
- Does a snap emerge naturally?
- Is there hysteresis or stable post-snap organization?
- Which metrics best detect transition onset?

## Next action

Implement the smallest runnable version and validate that the metrics can distinguish pre-snap reactive behavior from post-snap coherence organization.
