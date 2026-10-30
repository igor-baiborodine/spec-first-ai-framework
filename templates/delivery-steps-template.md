<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Delivery Plan: <Ticket>](#delivery-plan-ticket)
  - [Specification](#specification)
  - [Readiness](#readiness)
  - [Pull Request Strategy](#pull-request-strategy)
  - [Progress](#progress)
  - [Steps](#steps)
    - [Step 1: <Title> <PR1 when applicable>](#step-1-title-pr1-when-applicable)
  - [Decisions](#decisions)
  - [Risks](#risks)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Delivery Plan: <Ticket>

## Specification

- Ticket content: `<ticket-dir>/<ticket>-ticket-content.md`

Resolve `<ticket-dir>` using [Consumer artifact rules](../consumer.md#artifact-rules). Replace
this placeholder with the actual standalone or epic-grouped path and save the plan in that same
directory. When copying this template, update relative links for the destination directory.

## Readiness

- Objective clear:
- Scope clear:
- Contracts clear:
- Validation clear:
- Behavior evidence ready, when applicable: [AC IDs and example/check IDs have independent
  expected results, boundaries, and runnable checks or justified manual scenarios; retain bug
  reproduction and migration baseline provenance.]
- Prerequisite decision gates, when conditionally ready: [Decision IDs, safe resolution scope,
  responsible role, evidence/acceptance conditions, and blocked dependent steps. Resolve and
  update ticket content before rechecking readiness for those steps.]

## Pull Request Strategy

- Delivery: Single PR / Multiple PRs
- Assessment and rationale:
- PR sequence, branch suffixes, or dependencies when multiple PRs are planned:

## Progress

Keep this section to status, step title, planned PR when applicable, and the step summary artifact
reference. Record implementation details, findings, decisions, and validation results in the
dedicated step execution summary.

- [ ] Step 1: <Title> | PR: <PR1 when applicable> | Summary: <artifact after execution>
- [ ] Step 2: <Title> | PR: <PR1 or PR2 when applicable> | Summary: <artifact after execution>

## Steps

For multi-PR delivery, mark every step heading with `PR1`, `PR2`, and so on.
Assign integer step identifiers when the plan is established and keep them stable. If work must be
inserted between established integer steps, suffix the preceding integer with uppercase letters in
execution order (`7A`, `7B` between Steps 7 and 8) and record why the insertion is needed. Use the
same identifier in Progress and in the step summary filename, with a zero-padded numeric portion
(`step-07A`). Put retained logs, JSON/XML results, state captures, bundles and other secondary
delivery evidence under `<ticket-dir>/aux/` and link it from the owning step summary.

### Step 1: <Title> <PR1 when applicable>

- Modules:
- Changes:
- Planned validation:
- Acceptance examples/check IDs: [Assign applicable specification examples to this step and name
  the expected failure for a relevant behavior mutation; note property/differential checks when useful.]
- Artifact:
- Planned auxiliary evidence: `<ticket-dir>/aux/<step-prefixed-path>` / None

## Decisions

- [For substantial contract, persistence, or architecture choices, summarize alternatives,
  tradeoffs, failure modes, migration impact, and why the chosen design meets ACs before dependent
  work. Link the specification's bounded decision gate if unresolved; do not assume its outcome.]

## Risks

-
