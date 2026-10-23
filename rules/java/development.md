<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Java Development](#java-development)
  - [Runtime and dependencies](#runtime-and-dependencies)
  - [Failures and null boundaries](#failures-and-null-boundaries)
  - [Ownership and concurrency](#ownership-and-concurrency)
  - [Resources and persistence](#resources-and-persistence)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Java Development

## Runtime and dependencies

Respect the consumer's compiler release, JDK runtime, dependency graph, build wrapper and plugin
owners. Verify their compatibility before execution; do not upgrade or select a host tool merely
because it is installed. Keep generated/vendor code with its generator. Versions and application
frameworks are consumer choices, not Java-wide requirements.

## Failures and null boundaries

Define absence separately from failure at each boundary. Validate externally supplied inputs;
use Optional, exceptions or nullable mappings according to the existing contract. A mapper's
null-to-null behavior does not make every service input nullable. Preserve meaningful causes
when translating exceptions. Catch only failures that can be handled or translated there; do
not swallow exceptions, return success after failure, or expose sensitive payloads in diagnostics.
Test both the error result and absence of unintended persistence effects.

## Ownership and concurrency

Identify who owns mutable objects and collections. Avoid exposing writable internal collections
or storing request state in a singleton/static field. `final` references do not make their contents
immutable; an unmodifiable view does not isolate its backing collection. Use defensive copies,
confinement or explicit synchronization consistent with the required semantics. Do not replace
existing mutable models wholesale without a scoped requirement.

Bound asynchronous work and collect every worker result or exception. Awaiting termination alone
does not propagate worker failures to a test/caller. Coordinate starts for contention tests and
assert the persisted invariant. Handle interruption explicitly: propagate InterruptedException
where allowed, or restore interrupt status when translating it and terminate the operation.
Never turn cancellation into normal success. See the [JDK interruption contract](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Thread.html#interrupt()).

## Resources and persistence

Close resources owned by the operation on success and failure, preferably with try-with-resources
for AutoCloseable values. Register cleanup during partial setup; bound executor shutdown and
cleanup even when work fails. Do not close a container-managed EntityManager or a caller-owned
resource merely because it is accessible. Ownership, not type alone, determines cleanup.

State transaction, retry and locking boundaries explicitly. For proxy-based stacks, verify which
calls cross the proxy; self-invocation does not establish advice execution. Retry only selected
transient failures with a bound and known replay semantics. Keep identity/version and rollback
behavior intact. Locks and transaction annotations require real-storage evidence for concurrent
invariants; mocks cannot establish them. Resource/interruption/shared-state safeguards are
[explicit additions](../../provenance/java.md#coverage-inventory), not claims of proven campsite safety.
