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

Lux–Nyx governance routing must remain attached through downstream workflow handoffs. In practice, generated spawn requests and self-improve dispatch validation must preserve `lux_nyx_shaping` plus the review metadata (`promotion_review_requirement`, `promotion_review_status`) so archive outcomes skip dispatch and promotion-queue outcomes stay gated on approved human review.

When `lux_nyx_shaping` includes explicit routed fields such as `routing_disposition` and `routing_promotion_target`, downstream dispatch gates should treat those routed values as authoritative for archive/promotion handling rather than trusting stale pre-routing top-level targets. If Lux–Nyx only supplies an explicit routed disposition, the workflow should still infer the matching routed target (`DOC_PROMOTE` → `docs`, `TODO_PROMOTE` → `todo`, `LOG_ONLY` → `log-only`, and `POLICY_PROMOTE` → the appropriate policy lane inferred from the tweak/goal/section context when possible) before applying promotion gates.

The same rule now applies earlier in the workflow: orchestrator task-contract generation should preserve and honor explicit Lux–Nyx routed disposition/target pairs before deriving review requirements, so policy-relevant promotion candidates do not silently fall back to their pre-routing heuristic targets.

Full-pass/orchestrator summaries should also count the effective Lux–Nyx-routed disposition, promotion target, and derived branch outcome class when shaping metadata is present, even if older task-plan rows still carry stale pre-routing top-level values.

When Lux–Nyx marks work for `promotion-queue` without an explicit routed target, orchestration should still lift pre-routing `log-only` or `todo` work into the appropriate docs/workflow/foundations/tests-config promotion lane based on the task text rather than leaving it parked as bookkeeping.
