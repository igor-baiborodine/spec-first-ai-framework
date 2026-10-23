<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Java Testing](#java-testing)
  - [Selected house conventions](#selected-house-conventions)
  - [Independent scenarios and isolation](#independent-scenarios-and-isolation)
  - [Discovery and failure propagation](#discovery-and-failure-propagation)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Java Testing

## Selected house conventions

For consumers adopting the campsite house conventions, group tests by method in JUnit nested
classes, use `happy_path` or `given_<conditions>__then_<outcome>`, and name the subject
`classUnderTest` and the observed return `result`. Separate setup, invocation and assertions with
`// given`, `// when` and `// then`; the when block contains the operation under test. These are
[observed conventions](../../provenance/java.md#coverage-inventory), not JVM rules. Preserve
Insurance Hub's local legacy `happyPath` naming and do not rename existing tests incidentally.

Use AssertJ and Mockito where the consumer selects them. Mock external collaborators for focused
unit behavior; do not mock the invariant being tested. Easy Random is a fixture convenience,
not an oracle: explicitly set contract-relevant fields and retain repeatable seeds/inputs.

## Independent scenarios and isolation

Derive expected values from requirements, saved fixtures and pre-change behavior; never copy the
new implementation's output as its own expected result. Assert important mapped fields, failure
results and side effects. Include success, failure and compatibility cases. Retain known source
quirks explicitly rather than claiming all historical tests already follow the convention.

Control time/randomness and give parallel cases distinct resources, IDs and database rows. Avoid
mutable static fixtures, shared clocks or cleanup that destroys another test's state. Collect
worker results/exceptions, use bounded synchronization and clean owned resources in finally or
fixture teardown even after failed assertions. Verify concurrency invariants in real storage.
Mocks, awaitTermination, sleeps and an empty report cannot prove database behavior.

## Discovery and failure propagation

Respect the actual runner patterns and lifecycle for units and integration tests. Record discovered
and executed names/counts, failures and skips; fail required gates on zero discovery or unexpected
omissions. For Maven Failsafe, run the bound verification phase as well as integration execution;
calling integration-test alone may leave failures unreported by the build.

Seed a failing unit and a failing integration case in owned copies and require each owning gate
to return nonzero. A renamed test outside includes must be detected by the expected discovery
manifest. Keep disposable integration separate from unit checks and live operations. Required
missing tools, containers or database access are blocked checks, never successful skips.
See [validation](validation.md) and [counterexamples](../../examples/java/README.md).
