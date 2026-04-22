# Sandy Chaos Promotion Automation Policy (2026-04)

This document defines which classes of system promotions are safe for automated execution versus those requiring explicit human review.

## Promotion Classes

### 1. Local & Observational
- **Branch Outcome Class:** `local`
- **Dispositions:** `LOG_ONLY`, `DROP_LOCAL`
- **Targets:** `log-only`
- **Automation Status:** **SAFE**
- **Review Requirement:** `not-required`
- **Rationale:** These changes do not alter the functional system state or documentation. They represent observational traces and ephemeral session logs.

### 2. Task Management
- **Branch Outcome Class:** `promotable`
- **Dispositions:** `TODO_PROMOTE`
- **Targets:** `todo`
- **Automation Status:** **SAFE**
- **Review Requirement:** `not-required`
- **Rationale:** Updating the backlog to reflect completed or partial work is a bookkeeping task that maintains project momentum without introducing architectural risk.

### 3. Documentation (General)
- **Branch Outcome Class:** `promotable`
- **Dispositions:** `DOC_PROMOTE`
- **Targets:** `docs`
- **Automation Status:** **HUMAN REVIEW REQUIRED**
- **Review Requirement:** `human-review`
- **Rationale:** Documentation represents the system's "claim tier". Automated promotion of claims is forbidden until topological retrieval hit-rates and MRR reach higher confidence thresholds (>0.95).

### 4. Policy & Architecture
- **Branch Outcome Class:** `policy-relevant`
- **Dispositions:** `POLICY_PROMOTE`
- **Targets:** `tests/config`, `workflow`, `foundations`
- **Automation Status:** **HUMAN REVIEW REQUIRED**
- **Review Requirement:** `human-review`
- **Rationale:** Changes to system configuration, validation logic, and foundational specs carry high systemic risk. Human oversight is mandatory to prevent automated drift or legitimation of erroneous patterns.

## Continuity Signaling Integration
Promotions with a `POLICY_PROMOTE` disposition must include a continuity context trace from the topological memory runtime to assist human reviewers in verifying causality and alignment with recent research (e.g., Topological Memory v0 metrics).

## Enforcement
This policy is enforced via `config/orchestrator.json` under the `promotionReview` block, ensuring that any task contract emitted by the Sandy Chaos orchestrator carries the correct review requirements and initial status based on its promotion target and outcome class.
