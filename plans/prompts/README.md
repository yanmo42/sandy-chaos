# Sandy Chaos Implementation Prompts

This directory turns canonical Sandy Chaos surfaces into bounded implementation work packets.

The point is simple:

- canon should not stay decorative,
- theory should not be forced to pretend it is implementation,
- and implementation should not get to self-promote into doctrine.

So the operating loop is:

```text
canonical docs
  -> implementation prompt packet
  -> code / tests / instrumentation / benchmarks
  -> evidence artifacts
  -> adversarial review
  -> promotion, revision, or rejection
```

## Why this surface exists

Sandy Chaos now has enough architecture, theory, and governance to generate meaningful engineering work, but not all of that work should be improvised ad hoc.

This directory exists to:

- translate canon into buildable tasks,
- attract outside implementation pressure cleanly,
- preserve claim-tier discipline during execution,
- and keep review and promotion legible.

## Role split

### Theory owner / adversarial reviewer
Usually Ian.

Primary value:
- spots category errors,
- rejects fake rigor,
- identifies broken invariants,
- attacks weak implementations,
- decides whether outputs deserve another round.

### Coordinator
Usually the assistant.

Primary value:
- translates canon into work packets,
- scopes tasks to disciplined engineering gradients,
- routes work to builders/verifiers,
- summarizes results without laundering uncertainty.

### Builder / expert implementer
Human expert, coding agent, or contributor.

Primary value:
- implements,
- instruments,
- benchmarks,
- documents assumptions,
- reports failures honestly.

### Verifier
May be separate from the builder.

Primary value:
- checks that outputs satisfy the packet rather than merely looking impressive.

## Packet rules

Every prompt packet should declare, either in top metadata bullets or clearly named sections:

- `prompt_id`
- `status`
- `task_type`
- `surface_class`
- `authority_class`
- `source_surfaces`
- `claim_tier_ceiling`
- `objective`
- `non_goals`
- `required_constraints`
- `deliverables`
- `acceptance_criteria`
- `failure_conditions`
- `review_questions`

Recommended extras:

- `prompt_class`
- `expertise_requested`
- `interface_targets`
- `expected_artifacts`
- `out_of_scope_temptations`
- `promotion_if_successful`

## Claim-tier rule

Prompt packets do not raise claim tier.

A packet may only ask for work that is compatible with the maximum claim tier declared in the packet.
If implementation seems to suggest something bigger, that becomes a new review question, not an automatic promotion.

## Authority rule

Prompt packets are derivative execution surfaces.
Within the top-level Sandy Chaos surface taxonomy, they should normally be classified as:

- `surface_class: experimental`
- `authority_class: advisory`
- optional `prompt_class: execution-prompt`

They are not canonical authority surfaces.

That means:
- they may translate canon into work,
- they may not silently rewrite canon,
- they may not grant legitimacy to their own outputs,
- and they may not convert suggestive benchmark results into theory claims.

## Good prompt shape

A good packet:
- names a narrow interface,
- points at explicit source docs,
- requests concrete artifacts,
- has a failure condition,
- and gives the reviewer good places to attack.

A bad packet:
- asks for vibes,
- asks for proof by implementation theater,
- collapses theory into code without interfaces,
- or rewards elegance over inspectable evidence.

## Naming

Use:

- `SC-PROMPT-0001-*.md`
- `SC-PROMPT-0002-*.md`
- etc.

One packet should correspond to one bounded unit of pressureable work.

## Initial operating recommendation

Favor packets that move a subsystem from:
- decorative -> inspectable,
- enclave -> interface-bearing,
- suggestive -> benchmarked,
- merged -> actually integrated.

That is the disciplined engineering gradient.
