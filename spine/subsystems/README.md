# Subsystem Registry (v0)

This directory holds host-assimilation records for major Sandy Chaos subsystems.

Purpose:
- declare subsystem authority and host role explicitly,
- make integration status inspectable,
- connect subsystem identity to membranes, workflows, and evidence classes.

## Relationship to existing spine objects

- `spine/concepts/*` tracks concept evolution and pressure/promotion outcomes.
- `spine/subsystems/*` tracks subsystem architecture status and authority boundaries.

A concept can inspire a subsystem, and a subsystem can host multiple concepts.

## Minimal file shape

Each record should be a flat YAML object with simple lists (no advanced YAML features):

- `subsystem_id`
- `name`
- `status` (experimental|advisory|infrastructural|canonical)
- `authority_class`
- `host_layer`
- `repo_lane`
- `host_function`
- `purpose`
- `non_goals`
- `inputs`
- `outputs`
- `upstream_dependencies`
- `downstream_consumers`
- `governed_by`
- `claim_classes_supported`
- `evidence_classes_produced`
- `promotion_relevance`
- `workflow_participation`
- `interface_clarity`
- `evidence_maturity`
- `bounded_influence`
- `removal_impact`
- `failure_if_removed`
- `main_risks`
- `membrane_contracts`
- `source_docs`
- `notes`

## Initial operating rule

Do not use a single numeric assimilation score yet.
Track explicit dimensions instead (`workflow_participation`, `interface_clarity`, `evidence_maturity`, `bounded_influence`, `removal_impact`) until update rules are empirically grounded.
