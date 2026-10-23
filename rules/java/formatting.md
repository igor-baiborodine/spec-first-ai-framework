<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Java Formatting](#java-formatting)
  - [Explicit selection and scope](#explicit-selection-and-scope)
  - [Owned tooling and checks](#owned-tooling-and-checks)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Java Formatting

## Explicit selection and scope

Read the consumer's style selection and owning commands. `styles.java: google` adopts
[Google Java Style](https://google.github.io/styleguide/javaguide.html); `local` preserves the
consumer's declared existing style. Missing selection blocks formatting decisions. Insurance Hub
is excluded from Google style for all legacy Java, including new/modified files/tests; no Google
migration or formatting gate applies there. Campsite-booking selects Google style.

For Google selection, use two-space block indentation and a 100-column limit with the guide's
exceptions; use explicit imports, including static imports. A formatter alone may retain wildcard
imports, so run the bound import check separately. Formatting and import checks do not certify
all style rules, house naming or behavior. Do not rename tests to satisfy a formatting operation.

## Owned tooling and checks

The consumer owns compatible pinned formatter/checker versions, acquisition checksums, JDK,
configuration, file selection and explicit setup. Normal checks never install or silently choose
IDE defaults. Format only selected handwritten task files; exclude generated/vendor output and
unrelated files. A task-owned new or modified file must pass its applicable gates.

Run format, inspect the diff, then non-mutating format and import checks. Show formatter
idempotence and reject deliberately misformatted input while preserving check inputs. Keep
existing corpus deviations visible with their owner and disposition; a scoped pass is not a
whole-corpus pass. Do not suppress new findings or reformat the repository to make adoption pass.
The [measured deviations](../../provenance/java.md#deviations-and-gaps) retain the pilot baseline.
