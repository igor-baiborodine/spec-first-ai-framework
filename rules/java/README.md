<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Java Rules](#java-rules)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Java Rules

Select Java only for an affected Java boundary and a consumer profile that includes `java`.
The [catalog](../../catalog.json) routes implementation to this entry point,
[development](development.md), [formatting](formatting.md) and [validation](validation.md).
Add [architecture](architecture.md) for module/dependency/composition changes,
[API and transport](api-transport.md) for contracts/controllers/mapping, and [testing](test.md)
for tests or test configuration. Combine affected routes; API-plus-test work needs both.
Go-only work must not load these rules, and removing Java from one consumer must not change
another consumer's Java support.

Read the consumer's declared guides and tool sources first. Missing command, runtime, style or
scope information blocks the dependent action; it does not license guessed Maven/Gradle commands.
The framework helper runtime is distinct from the application's JDK/build runtime.

The [derivation inventory](../../provenance/java.md) separates shared JVM principles, selected
house/stack conventions, consumer details and additional safeguards. Google formatting requires
an explicit `styles.java: google` selection. `local` retains the consumer's existing style.
Insurance Hub selects local style throughout its legacy Java, including new/modified tests;
campsite-booking selects Google style. No Java retirement or blanket migration follows from routing.

Use [review scenarios](../../examples/java/README.md) to challenge meaning. Catalog/link checks
prove routing structure, not Java correctness or client loading.
