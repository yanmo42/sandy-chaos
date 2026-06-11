# Topological Memory Runtime Adoption v0

- Workflow consumer: `scripts/automation_orchestrator.py task preparation for continuity-lane tasks`
- Query count: **3**
- Topology hit-rate: **1.000**
- Flat hit-rate: **1.000**
- Topology-only hits: `[]`
- Flat-only hits: `[]`

## Per-query traces

### WQ-001

- Question: What script builds lane-aware task contracts from TODO surfaces?
- Expected nodes: ['N_SCRIPT_AUTOMATION_ORCH']
- Topology: hit=True first_match_rank=1 matched_nodes=['N_SCRIPT_AUTOMATION_ORCH'] top_node=N_SCRIPT_AUTOMATION_ORCH mode=topology
- Flat: hit=True first_match_rank=1 matched_nodes=['N_SCRIPT_AUTOMATION_ORCH'] top_node=N_SCRIPT_AUTOMATION_ORCH mode=flat/keyword

### WQ-002

- Question: What script dispatches orchestrator task contracts through the gateway bridge?
- Expected nodes: ['N_SCRIPT_ORCH_AUTOSPAWN']
- Topology: hit=True first_match_rank=1 matched_nodes=['N_SCRIPT_ORCH_AUTOSPAWN'] top_node=N_SCRIPT_ORCH_AUTOSPAWN mode=topology
- Flat: hit=True first_match_rank=1 matched_nodes=['N_SCRIPT_ORCH_AUTOSPAWN'] top_node=N_SCRIPT_ORCH_AUTOSPAWN mode=flat/keyword

### WQ-003

- Question: Which TODO surface currently tracks the execution steps for topological memory?
- Expected nodes: ['N_PLAN_TODO']
- Topology: hit=True first_match_rank=1 matched_nodes=['N_PLAN_TODO'] top_node=N_PLAN_TODO mode=topology
- Flat: hit=True first_match_rank=1 matched_nodes=['N_PLAN_TODO'] top_node=N_PLAN_TODO mode=flat/keyword

## Bounds

- This is a bounded workflow-style comparison, not a promotion argument.
- Flat mode remains a live fallback path.
