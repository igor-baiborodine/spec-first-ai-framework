<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Safety Rules](#safety-rules)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Safety Rules

- Never silently change security, authentication, authorization, or data-retention behavior.
- Never silently change API contracts, event payloads, database schemas, or deployment behavior.
- Surface ambiguous or conflicting requirements before implementation.
- Treat customer, payment, policy, and authentication data paths as sensitive.
- Do not introduce new dependencies without a concrete reason and validation path.
- Do not remove tests, validation, or operational checks to make implementation easier.
- Document residual risk when validation cannot fully prove the change.
