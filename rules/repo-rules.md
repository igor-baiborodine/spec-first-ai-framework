<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Repository Rules](#repository-rules)
  - [General](#general)
  - [Testability](#testability)
  - [CI Workflows](#ci-workflows)
  - [Markdown Tables Of Contents](#markdown-tables-of-contents)
  - [Git And Artifacts](#git-and-artifacts)
  - [Operational Recovery](#operational-recovery)
  - [Validation](#validation)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Repository Rules

## General

- Read relevant local code and docs before changing behavior.
- Prefer existing project patterns over new abstractions.
- Keep changes scoped to the request or ticket.
- Preserve behavior unless the spec explicitly changes it.
- Avoid unrelated formatting, metadata churn, or refactors.
- Update documentation when behavior, setup, workflow, or contracts change.
- Apply [Naming rules](naming-rules.md) when that house convention is selected; otherwise preserve
  the consumer's naming policy when creating or renaming paths.

## Testability

- For non-core functionality such as repository tooling, use an 80/20 test direction: prioritize
  focused likely-path behavior and the smallest useful case matrix. Keep every safety check that is
  applicable to the contract, including target guards, failure handling, deadlines, interruption,
  cleanup, secret protection, permissions, and dry-run boundaries.
- When implementing unit or integration tests, assess the effort required to construct fixtures,
  wire dependencies, and express the test scenarios. Treat disproportionate setup, mocking, or
  test-method complexity as feedback about the production design.
- If that complexity comes from tightly coupled dependencies, broad responsibilities, hidden state,
  or difficult control flow in the method or function under test, revise the production design
  before adding test-only indirection or increasingly elaborate fixtures. Keep the revision within
  the ticket's behavioral and compatibility requirements.
- Complexity inherent in exercising a real integration boundary, such as starting a disposable
  database or transport, does not by itself require a production redesign. Keep that environment
  setup in reusable test infrastructure while preserving realistic boundary coverage.

## CI Workflows

- Name workflows by scope and purpose in the top-level `name:` field, such as `Go Module
  Validation`, `Go Report Card`, and `Legacy API Release`.
- Use a concrete purpose instead of appending `CI` solely because a workflow runs in CI.
- When changing a workflow display name, update badge labels and documentation that refer to it.
  Keep workflow filenames and job identifiers stable unless they also need to change.
- Apply the dedicated [CI workflow rules](ci-workflows.md) whenever the operations component is
  selected and CI configuration is created, reviewed or changed. Consumer-owned CI interfaces,
  provider settings, runner classes, budgets and required-check names remain local bindings.

## Markdown Tables Of Contents

Use the consumer's `markdown-format` and `markdown-check` bindings on every changed Markdown
file, including artifacts. The selected doctoc convention requires a generated TOC; never edit
it by hand. Run format then check on exact task-owned files only. Missing owner/tooling blocks
this check; no sibling script path or implicit package installation is assumed.

## Git And Artifacts

- Do not commit files under `<artifact-root>/`.
- Do not overwrite or revert user changes unless explicitly requested.
- For ticket work, resolve `<ticket-dir>` through [Consumer artifact rules](../consumer.md#artifact-rules).
  Store the specification, delivery plan, step summaries, and diff snapshots together there,
  whether the ticket is standalone or grouped under an epic.
- Keep committed shared framework files concise and reusable; local wrappers remain consumer-owned.

## Operational Recovery

Use the consumer's scoped recovery runbook before classifying source/image or network state as a
repository defect. Follow [operations](operations.md) when that component is selected.

## Validation

- Run the narrowest meaningful tests or checks for the changed modules.
- Run the Markdown TOC check for every Markdown file created or updated by the current task.
- If validation is skipped or unavailable, state that explicitly and explain why.
- Do not treat generated plans or summaries as a substitute for running checks.
