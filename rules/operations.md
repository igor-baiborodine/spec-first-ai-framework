<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Operations](#operations)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Operations

Apply only to affected CI, deployment, infrastructure, administration or observability boundaries.
For CI configuration, also apply the dedicated [CI workflow rules](ci-workflows.md).
Read the consumer's change-to-check index and relevant runbooks before selecting commands; concrete
cluster, namespace, registry, database, GitOps and telemetry identities remain consumer-owned.
Classify stale source/image, DNS or network state through the owning recovery procedure before
calling it a repository defect. Never copy another consumer's target coordinates or recovery action.

Separate inspection, non-mutating validation, disposable tests, provisioning and live mutation.
Declare target, credentials, effects, cleanup and recovery; verify target read-only before authorized
mutation. Preserve GitOps/resource ownership and role-specific permissions. A successful local
fixture does not authorize a live operation or prove deployed permissions/TLS/telemetry delivery.
Use bounded waits and owned-resource cleanup; capture sanitized diagnostics before teardown and
inspect postconditions before retrying a remotely ambiguous action. Never prune unrelated resources.
Read [agent trust](agent-security-rules.md) and relevant language lifecycle rules for scripts.
