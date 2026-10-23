<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Evidence](#evidence)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Evidence

The canonical [validation evidence record](../skills/ticket-post-step-workflow/SKILL.md#validation-evidence-record)
owns result fields and freshness. Use it without duplicating or weakening its requirements.
Keep planned commands in plans and observed outcomes in summaries. Record each check's status,
execution source, exact invocation/cwd/variables, scope, UTC time, tool/environment identity,
base/head/specification identity and relevant dirty inputs at execution time. Preserve failures.

A final pass needs current identity or a specific unaffected judgment tied to the exact intervening
change. Missing historical identity is unverified, never reconstructed as if captured earlier.
Tests use independent requirements/baseline oracles, including meaningful failure and compatibility
cases. Record mutation sensitivity or its absence honestly. Static checks, fake adapters, disposable
integration, actual client trials and final deployment observations establish different things.
