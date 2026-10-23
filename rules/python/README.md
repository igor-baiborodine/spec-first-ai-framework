<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Python Rules](#python-rules)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Python Rules

Select Python only for affected Python boundaries. The consumer defines whether it is auxiliary
or an application language; selecting these rules does not change that role or migrate services.
Read all four linked rules for implementation or review:

- [Development](development.md): ownership, CLI contracts, processes, resources and operations.
- [Testing](test.md): meaningful scenarios, discovery, isolation and integration boundaries.
- [Formatting](formatting.md): selected Ruff configuration, scope and non-mutating checks.
- [Validation](validation.md): changed-boundary gates and evidence.

Use the consumer's declared setup/runtime/toolchain and command owners. Missing required bindings
block dependent checks, never trigger installation or a system-Python fallback. Runtime/tool pins
and lockfiles stay with their owner. Apply [naming](../naming-rules.md) and [Make](../makefile-rules.md)
conventions when selected and applicable. Follow [consumer composition](../../consumer.md).
