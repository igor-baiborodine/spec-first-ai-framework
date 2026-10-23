<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Go Validation](#go-validation)
  - [Discover the validation boundary](#discover-the-validation-boundary)
  - [Required checks](#required-checks)
  - [Migration acceptance](#migration-acceptance)
  - [Evidence and current availability](#evidence-and-current-availability)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Go Validation

Use only the declared validation owner, including Make targets where selected, as required by
[Go development](development.md#scope-and-makefile-interface). Never invoke underlying test,
lint, build, generation, dependency, or security tools directly to bypass a missing/failing target.
Use [Go rules](README.md) to select architecture, API and transport, or testing details when the
task crosses those boundaries. This file defines which checks to execute and what evidence to
record.

## Discover the validation boundary

- Read module/workspace manifests, declared command owners (including prerequisites), relevant CI, and service
  instructions. Identify changed modules, generated contracts, and dependent consumers.
- For HTTP/gRPC changes, identify contract sources, the actual request path, OpenAPI/gateway
  outputs, and affected callers using [API and transport verification](api-transport.md#verification-and-adoption).
  Check HTTP compatibility separately from protobuf compatibility and exercise the deployed
  transport composition, including middleware, identity, metadata, and deadline propagation.
- For new services or changed boundaries/composition, inspect core imports and port signatures,
  adapter mappings, constructor wiring, and resource ownership against
  [the architecture rule](architecture.md#architecture-handoff-and-review). Verify the affected
  README package map, diagram, and walkthrough against code, and run the owning documentation
  targets. Record inspection separately from test results; the current cross-module topology
  check does not enforce layering within a service.
- Inspect each target's actual coverage: package selection, nested modules, build tags, race
  instrumentation, integration dependencies, and whether it changes files. A root target or a
  workspace does not by itself prove that every service is tested.
- Run the narrowest meaningful checks during implementation, then all applicable module/CI gates.
  Use the declared owner's supported package/test selection interface (Make variables where
  selected); do not invent options or bypass the owner. Include changed packages outside a
  command's default selection.
- Do not run broad aggregates blindly. In the example, `check` tidies dependencies, formats files,
  and runs both unit and integration tests. Dependency maintenance is appropriate only when imports
  or dependencies change, and integration prerequisites must be available.

## Required checks

The table lists capabilities, not claims that a consumer supplies any named target. Resolve exact
commands, cwd, versions and effects from the local profile and source. Make-selected consumers use
their owning Make targets; another command owner must be explicitly declared.

| Capability | When and what to verify |
| --- | --- |
| Format and non-mutating format check | Changed handwritten files; include untracked files, exclude generated/vendor/unrelated content |
| Lint/static analysis | Affected modules, including vet-equivalent checks using pinned configuration |
| Unit tests | Changed behavior, all affected module packages before completion, and affected consumers; inspect discovery and skips |
| Build | Affected executables and contract consumers; unit success does not prove entry points build |
| Integration | Adapters, persistence, migrations, transport/composition, cross-service changes and CI requirements; real disposable dependencies |
| Protobuf format/lint/generation | Changed schemas and all configured output; generator options/versions recorded |
| Breaking compatibility | Published wire and HTTP contracts against independently recorded accepted baseline |
| OpenAPI lint/generation/drift/HTTP | Sources, missing/new output, accepted representation and real transport behavior |
| Mock/client generation | Changed interfaces and reproducibility of affected generated sources |
| Dependency consistency | Changed imports/dependencies or required CI gate; review manifest and checksums |
| Race checks | Concurrency, shared state, workers/caches or race-enabled CI; do not duplicate an equivalent run |
| Vulnerability checks | Dependencies/security-sensitive code or CI requirements; pinned analyzer and reachability where applicable |

Missing required capabilities block acceptance. Add an owning interface only within scope, never
silently downgrade checks. Checks must not provision tools, rewrite dependencies or mutate shared
targets. Keep setup separate. Generation checks compare complete file sets against a valid baseline,
including new/deleted files; never reset/stash/stage user work to make them pass. Verify formatter
idempotence and generation reproducibility when those pipelines change.

## Migration acceptance

- For service rewrites, verify the legacy parity cases recorded in the ticket: success and failure
  responses, validation, permissions, events, persistence, and serialization semantics.
- Test real migrations and transaction/conflict behavior with disposable dependencies. Unit mocks
  cannot prove database constraints, isolation, or compatibility with the coexisting legacy service.
- Before traffic cutover, run the ticket's integration, end-to-end, and performance commands through
  their declared owners (Make targets where selected)
  against the Go service's internal endpoints and compare with the independent legacy baseline. Record rollback
  readiness and rollout criteria; a unit-test pass alone does not authorize traffic changes.
- Verify startup/configuration failures, health probes, cancellation and graceful shutdown, and
  telemetry delivery/correlation through the configured collector pipeline. Report local-only observations separately from
  cluster or collector verification; do not infer delivery merely from instrumentation code.

## Evidence and current availability

- Record exact owning-command invocations, working directories, relevant variables/module coverage, and
  results in the per-step `Validation Evidence` record required by the
  [post-step workflow](../../skills/ticket-post-step-workflow/SKILL.md#validation-evidence-record).
  Use its shared result statuses and record execution source separately. Planned checks belong in
  the delivery plan; they are not evidence of execution.
- Report pre-existing failures separately from regressions. Preserve useful failure evidence;
  never hide failures, weaken gates, or state that unexecuted checks passed.
- After checks, inspect tracked and relevant new files for unintended generated, formatting, or
  dependency changes. Complete the evidence record, map acceptance criteria to evidence at ticket
  completion, and apply the repository before-merge checklist.
- Use the consumer-owned module inventory, each module's command owner and applicable topology
  checks. Root inventory checks cover only recorded modules; a new module needs explicit
  owning targets, consumers, resolution modes, CI triggers, and onboarding before repository
  validation may claim coverage. Documentation-only rule changes still require reference,
  consistency, and whitespace review and do not establish runtime correctness.
