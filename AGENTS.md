<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Framework Contributor Guide](#framework-contributor-guide)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Framework Contributor Guide

This guide governs edits to this framework checkout. Consumers must load [consumer.md](consumer.md)
through their own trusted root guide; this file must not become exported consumer policy.

Preserve user changes, discover applicable nested guides and keep edits within the requested step.
Use the source-to-destination inventory in [provenance/extraction.md](provenance/extraction.md) to
preserve capabilities. Read the affected canonical workflows/rules before changing their meaning.
Compare authority changes with their trusted source and obtain independent human maintainer review
before acceptance. Proposed policy does not itself grant execution or publication authority.

Keep consumer topology, tool paths, operational targets, business behavior and ticket artifacts out
of shared source. The consumer profile owns those bindings. Keep the catalog and workflow table
consistent with actual files; no route may reference a missing component. Do not silently remove a
safeguard to make portability easier. Preserve the existing README/ignore setup.

The current delivery stage is guidance only. Shared executable tooling, locks and command owners
are a subsequent step. Record unavailable source-check/runtime targets as blocked; do not invent
passes or require an undeclared sibling checkout. For this extraction, task records stay in their
already resolved consumer artifact home. Do not create or repair a local artifact exclusion here.

Validate all changed Markdown with the explicitly provisioned doctoc 2.5.0 owner, format then
check. Record the command and tool identity; keep transient authoring tools out of source. Static
link/catalog/metadata checks are not client compatibility tests. New Python helpers require declared
runtime/dependencies, formatting/lint, separate fast/integration/collection checks and bounded
process/resource handling. Apply the selected Python rules when implementing them.

Before any commit inspect the full change and obtain the user's explicit authorization unless
already supplied for that scope in this session. Push, merge, tags and live operations need their
own scope. Never commit local artifacts, credential data or disposable outputs.
