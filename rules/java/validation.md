<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Java Validation](#java-validation)
  - [Select checks by changed boundary](#select-checks-by-changed-boundary)
  - [Results and freshness](#results-and-freshness)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Java Validation

## Select checks by changed boundary

Use the consumer's declared command owner, cwd, JDK/build/runtime and tool configuration. Inspect
prerequisites/effects before running; no Java Make wrapper is required by shared policy.

| Changed boundary | Required evidence |
| --- | --- |
| Handwritten source/tests | Selected format/import checks, compilation and relevant unit cases; actual counts/skips |
| Contract/schema/mapper | Clean reproducible generation with input/output identities, explicit metadata normalization, dependent compilation and independent field/error assertions |
| Persistence/transaction/concurrency | Complete integration lifecycle with actual disposable database, migration/config identities, bounded workers, collected failures and persisted invariants |
| Runner/includes/lifecycle | Discovery manifest and nonzero counts; seeded failing unit and IT each fail the owning command; omitted test is detected |
| Static/dependency policy | Selected static rules and seeded counterexample; pinned dependency scan with complete/current data and original thresholds; no suppressed failure |
| Format/configuration | Misformat and wildcard rejection, unchanged check inputs, formatter idempotence and selected-file/generated exclusions |

Run the narrowest gates proving the affected boundary, then required consumer aggregate gates.
Unavailable tools, incomplete dependency databases, skips or partial integration phases cannot
satisfy required checks. Keep dependency setup/network/cache mutations separate and explicit.
Do not upload to hosted scanners just to obtain local evidence without authorization.

## Results and freshness

Record source/specification/profile/framework identities, dirty inputs, exact commands/cwd,
versions/configuration, UTC, names/counts/skips, independent expectations and observed outcomes
under the [evidence rules](../evidence.md). Real database observations identify the owned target
and teardown. Pre-existing nonzero findings remain failures with a scoped disposition; deferral
is neither a passing scan nor security-risk acceptance. New unexplained regressions block their
acceptance. Recheck affected evidence after relevant source/configuration/specification changes.

The [review cases](../../examples/java/README.md) challenge swallowed errors, leaks, shared state,
transport drift and missed discovery. They require semantic review; source checks are not a Java
analyzer. Pilot counts and commands belong to consumer evidence, never universal thresholds here.
