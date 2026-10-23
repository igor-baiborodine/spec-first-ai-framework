<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Extraction Provenance and Authority Review](#extraction-provenance-and-authority-review)
  - [Trusted baseline and scope](#trusted-baseline-and-scope)
  - [Source inventory](#source-inventory)
  - [Concrete authority comparison](#concrete-authority-comparison)
  - [Deferred validation ownership](#deferred-validation-ownership)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Extraction Provenance and Authority Review

## Trusted baseline and scope

Derived from Insurance Hub commit `b2257e42bfd5749bd9d5bb0aa0b5826ea35ee198`, using the approved
ownership inventory and Step 8 contract for the extraction ticket. The framework base is
`744aa705891cac79841758ba27cdb2711f43d449`; its original README title and ignore configuration
are preserved. Source references here record provenance, not a runtime dependency on a sibling
checkout or additional instruction authority. No private ticket contents are distributed here.

## Source inventory

Each original capability is retained, split into consumer-owned bindings, or explicitly assigned
to its later helper/Java step. Historical paths and adapter references in consumers are preserved
until their separately validated cutover; this new tree does not relocate their local records.

| Original path at trusted baseline | Shared destination | Disposition |
| --- | --- | --- |
| `ai/checks/agent-security-scenarios.md` | [checks/agent-security-scenarios.md](../checks/agent-security-scenarios.md) | Adapted source; local facts/bindings separated |
| `ai/checks/before-coding.md` | [checks/before-coding.md](../checks/before-coding.md) | Adapted source; local facts/bindings separated |
| `ai/checks/before-merge.md` | [checks/before-merge.md](../checks/before-merge.md) | Adapted source; local facts/bindings separated |
| `ai/checks/check_ai_framework.py` | Consumer-owned / later step | Portable helper/test owner deferred to Step 10; blocked executable capability, no pass claimed |
| `ai/checks/client-compatibility-scenarios.md` | [checks/client-compatibility-scenarios.md](../checks/client-compatibility-scenarios.md) | Adapted source; local facts/bindings separated |
| `ai/checks/test_check_ai_framework.py` | Consumer-owned / later step | Portable helper/test owner deferred to Step 10; blocked executable capability, no pass claimed |
| `ai/client-compatibility.md` | [checks/client-compatibility.md](../checks/client-compatibility.md) | Historical matrix remains consumer-owned; final four-cell evidence required |
| `ai/examples/README.md` | [examples/README.md](../examples/README.md) | Adapted source; local facts/bindings separated |
| `ai/examples/go-testing/README.md` | [examples/go-testing/README.md](../examples/go-testing/README.md) | Adapted source; local facts/bindings separated |
| `ai/examples/go-testing/application-tests.md` | [examples/go-testing/application-tests.md](../examples/go-testing/application-tests.md) | Adapted source; local facts/bindings separated |
| `ai/examples/go-testing/grpc-tests.md` | [examples/go-testing/grpc-tests.md](../examples/go-testing/grpc-tests.md) | Adapted source; local facts/bindings separated |
| `ai/examples/go-testing/postgres-integration-tests.md` | [examples/go-testing/postgres-integration-tests.md](../examples/go-testing/postgres-integration-tests.md) | Adapted source; local facts/bindings separated |
| `ai/examples/go-testing/sql-adapter-tests.md` | [examples/go-testing/sql-adapter-tests.md](../examples/go-testing/sql-adapter-tests.md) | Adapted source; local facts/bindings separated |
| `ai/examples/go-testing/unit-tests.md` | [examples/go-testing/unit-tests.md](../examples/go-testing/unit-tests.md) | Adapted source; local facts/bindings separated |
| `ai/examples/python-testing/README.md` | [examples/python-testing/README.md](../examples/python-testing/README.md) | Adapted source; local facts/bindings separated |
| `ai/examples/python-testing/example_cli.py` | [examples/python-testing/example_cli.py](../examples/python-testing/example_cli.py) | Unchanged executable example; Step 10 owns wiring and execution gates |
| `ai/examples/python-testing/integration/test_disposable_cli.py` | [examples/python-testing/integration/test_disposable_cli.py](../examples/python-testing/integration/test_disposable_cli.py) | Unchanged executable example; Step 10 owns wiring and execution gates |
| `ai/examples/python-testing/tests/conftest.py` | [examples/python-testing/tests/conftest.py](../examples/python-testing/tests/conftest.py) | Unchanged executable example; Step 10 owns wiring and execution gates |
| `ai/examples/python-testing/tests/test_example_cli.py` | [examples/python-testing/tests/test_example_cli.py](../examples/python-testing/tests/test_example_cli.py) | Unchanged executable example; Step 10 owns wiring and execution gates |
| `ai/manifest.md` | [consumer.md](../consumer.md) | Split into exported composition, catalog and contributor guide |
| `ai/prompts/README.md` | [prompts/README.md](../prompts/README.md) | Adapted source; local facts/bindings separated |
| `ai/prompts/session-bootstrap.md` | [prompts/session-bootstrap.md](../prompts/session-bootstrap.md) | Adapted source; local facts/bindings separated |
| `ai/rules/agent-security-rules.md` | [rules/agent-security-rules.md](../rules/agent-security-rules.md) | Adapted source; local facts/bindings separated |
| `ai/rules/git-rules.md` | [rules/git-rules.md](../rules/git-rules.md) | Adapted source; local facts/bindings separated |
| `ai/rules/go-api-transport.md` | [rules/go-api-transport.md](../rules/go-api-transport.md) | Adapted source; local facts/bindings separated |
| `ai/rules/go-architecture.md` | [rules/go-architecture.md](../rules/go-architecture.md) | Adapted source; local facts/bindings separated |
| `ai/rules/go-development.md` | [rules/go-development.md](../rules/go-development.md) | Adapted source; local facts/bindings separated |
| `ai/rules/go-formatting.md` | [rules/go-formatting.md](../rules/go-formatting.md) | Adapted source; local facts/bindings separated |
| `ai/rules/go-rules.md` | [rules/go-rules.md](../rules/go-rules.md) | Adapted source; local facts/bindings separated |
| `ai/rules/go-test.md` | [rules/go-test.md](../rules/go-test.md) | Adapted source; local facts/bindings separated |
| `ai/rules/go-validation.md` | [rules/go-validation.md](../rules/go-validation.md) | Adapted source; local facts/bindings separated |
| `ai/rules/infrastructure-rules.md` | [rules/operations.md](../rules/operations.md) | Shared safeguards only; concrete check index/runbooks stay consumer-owned |
| `ai/rules/java-rules.md` | Consumer-owned / later step | Consumer retains legacy rule; full seven-area shared Java and provenance in Step 11 |
| `ai/rules/makefile-rules.md` | [rules/makefile-rules.md](../rules/makefile-rules.md) | Adapted source; local facts/bindings separated |
| `ai/rules/naming-rules.md` | [rules/naming-rules.md](../rules/naming-rules.md) | Adapted source; local facts/bindings separated |
| `ai/rules/python-development.md` | [rules/python-development.md](../rules/python-development.md) | Adapted source; local facts/bindings separated |
| `ai/rules/python-formatting.md` | [rules/python-formatting.md](../rules/python-formatting.md) | Adapted source; local facts/bindings separated |
| `ai/rules/python-rules.md` | [rules/python-rules.md](../rules/python-rules.md) | Adapted source; local facts/bindings separated |
| `ai/rules/python-test.md` | [rules/python-test.md](../rules/python-test.md) | Adapted source; local facts/bindings separated |
| `ai/rules/python-validation.md` | [rules/python-validation.md](../rules/python-validation.md) | Adapted source; local facts/bindings separated |
| `ai/rules/repo-rules.md` | [rules/repo-rules.md](../rules/repo-rules.md) | Adapted source; local facts/bindings separated |
| `ai/rules/safety-rules.md` | [rules/safety-rules.md](../rules/safety-rules.md) | Adapted source; local facts/bindings separated |
| `ai/rules/spec-first-rules.md` | [rules/spec-first-rules.md](../rules/spec-first-rules.md) | Adapted source; local facts/bindings separated |
| `ai/skills/code-review/SKILL.md` | [skills/code-review/SKILL.md](../skills/code-review/SKILL.md) | Adapted source; local facts/bindings separated |
| `ai/skills/code-review/references/github-review.md` | [skills/code-review/references/github-review.md](../skills/code-review/references/github-review.md) | Adapted source; local facts/bindings separated |
| `ai/skills/code-review/references/local-review.md` | [skills/code-review/references/local-review.md](../skills/code-review/references/local-review.md) | Adapted source; local facts/bindings separated |
| `ai/skills/code-review/scripts/check-upstream-sync.sh` | Consumer-owned / later step | Portable helper/test owner deferred to Step 10; blocked executable capability, no pass claimed |
| `ai/skills/code-review/scripts/check_upstream_sync.py` | Consumer-owned / later step | Portable helper/test owner deferred to Step 10; blocked executable capability, no pass claimed |
| `ai/skills/code-review/scripts/test_check_upstream_sync.py` | Consumer-owned / later step | Portable helper/test owner deferred to Step 10; blocked executable capability, no pass claimed |
| `ai/skills/code-review/scripts/test_verify_published_pr.sh` | Consumer-owned / later step | Portable helper/test owner deferred to Step 10; blocked executable capability, no pass claimed |
| `ai/skills/code-review/scripts/verify_published_pr.sh` | Consumer-owned / later step | Portable helper/test owner deferred to Step 10; blocked executable capability, no pass claimed |
| `ai/skills/pr-description/SKILL.md` | [skills/pr-description/SKILL.md](../skills/pr-description/SKILL.md) | Adapted source; local facts/bindings separated |
| `ai/skills/pr-description/references/github-drafting.md` | [skills/pr-description/references/github-drafting.md](../skills/pr-description/references/github-drafting.md) | Adapted source; local facts/bindings separated |
| `ai/skills/pr-description/references/local-drafting.md` | [skills/pr-description/references/local-drafting.md](../skills/pr-description/references/local-drafting.md) | Adapted source; local facts/bindings separated |
| `ai/skills/ticket-implementation-workflow/SKILL.md` | [skills/ticket-implementation-workflow/SKILL.md](../skills/ticket-implementation-workflow/SKILL.md) | Adapted source; local facts/bindings separated |
| `ai/skills/ticket-post-step-workflow/SKILL.md` | [skills/ticket-post-step-workflow/SKILL.md](../skills/ticket-post-step-workflow/SKILL.md) | Adapted source; local facts/bindings separated |
| `ai/skills/ticket-post-step-workflow/scripts/refresh_git_diff.sh` | Consumer-owned / later step | Portable helper/test owner deferred to Step 10; blocked executable capability, no pass claimed |
| `ai/skills/ticket-post-step-workflow/scripts/test_refresh_git_diff.sh` | Consumer-owned / later step | Portable helper/test owner deferred to Step 10; blocked executable capability, no pass claimed |
| `ai/skills/ticket-requirements-workflow/SKILL.md` | [skills/ticket-requirements-workflow/SKILL.md](../skills/ticket-requirements-workflow/SKILL.md) | Adapted source; local facts/bindings separated |
| `ai/skills/ticket-specification-workflow/SKILL.md` | [skills/ticket-specification-workflow/SKILL.md](../skills/ticket-specification-workflow/SKILL.md) | Adapted source; local facts/bindings separated |
| `ai/templates/delivery-steps-template.md` | [templates/delivery-steps-template.md](../templates/delivery-steps-template.md) | Adapted source; local facts/bindings separated |
| `ai/templates/pr-description-template.md` | [templates/pr-description-template.md](../templates/pr-description-template.md) | Adapted source; local facts/bindings separated |
| `ai/templates/pr-review-template.md` | [templates/pr-review-template.md](../templates/pr-review-template.md) | Adapted source; local facts/bindings separated |
| `ai/templates/requirements-template.md` | [templates/requirements-template.md](../templates/requirements-template.md) | Adapted source; local facts/bindings separated |
| `ai/templates/ticket-content-template.md` | [templates/ticket-content-template.md](../templates/ticket-content-template.md) | Adapted source; local facts/bindings separated |

Root consumer `AGENTS.md` authority/artifact rules become the exported composition contract while
repository topology and local command specifics remain consumer-owned. Original client adapters,
CI, Make/module inventory, operational tooling and hooks remain in their consumers; later cutover
updates references and caller wiring. No application assets, tool databases or credentials move.

## Concrete authority comparison

This table identifies the proposed policy changes for independent human maintainer review.
All linked shared files are review subjects until that review accepts them. The accepted design
alone is not acceptance of these concrete policy bodies.

| Baseline contract | Shared implementation | Change and preserved boundary |
| --- | --- | --- |
| Root precedence and scoped guides | [consumer composition](../consumer.md#precedence-and-conflicts), [trust](../rules/agent-security-rules.md) | Explicit consumer/framework roots replace implicit local root; conflicts still stop dependent work; host and direct-user authority retained |
| Root artifact resolver/exclusion | [artifact rules](../consumer.md#artifact-rules) | Consumer artifact-root binding replaces fixed directory; exact local exclusion, ignored discovery, no indexed/staged artifacts, no automatic repair/move/untrack retained |
| Local-authority GitHub synchronization | [spec-first](../rules/spec-first-rules.md#github-ticket-synchronization) | Provider binding is explicit; exact-body checkpoints, explicit update scope/read-back, ad hoc exemption and external evidence retained |
| Assessment/specification/plan stopping points | [six workflows](../consumer.md#workflow-catalog) | Full workflow bodies preserved with portable references; no automatic implementation/publication or retrospective assessment for ready tickets |
| Post-step and truthful evidence | [post-step](../skills/ticket-post-step-workflow/SKILL.md), [evidence](../rules/evidence.md) | Snapshot uses declared capability; full identity, dirty manifests, freshness, independent expected outcomes and historical failures preserved |
| Local review, optional hosted review, exact published revisions | [review](../skills/code-review/SKILL.md), [commands](../rules/commands.md#review-and-snapshot-capabilities) | Helper paths become declared bindings; read-only boundary, optional strict sync, exact remote SHAs, dirty-work separation and unavailable-capability stop preserved |
| Draft versus authorized PR-body update | [description](../skills/pr-description/SKILL.md) | Three-section standard retained; no creation/merge/other metadata changes; authorized body update requires read-back |
| Worktree/commit/publication safety | [consumer authority](../consumer.md#authority-and-actions), [Git](../rules/git-rules.md) | Complete change review and explicit session-scoped commit/push permissions retained; no implicit permission from checks or extracted policy |
| Language/house/operational separation | [catalog](../catalog.json), [house](../rules/house.md), [operations](../rules/operations.md) | Consumer-specific Make mandate, language purpose, versions, package maps and runbooks become explicit selections; mandatory safety, discovery and meaningful validation do not become optional |

The Go package map is illustrative for consumers selecting that architecture; it is not a universal
layout migration. Formatting/test naming are selected house conventions. Python keeps its full
process/CLI/resource/security and verification IDs while runtime/build owners become local. Java
style remains a separate selection, preserving the legacy consumer's exclusion. Supplied Go
snippets retain fictional policy contracts and historical source provenance; they are not compiled
or runtime evidence. Python example source is byte-preserved; new executable checks await Step 10.

## Deferred validation ownership

Step 10 supplies independent source-check, runtime/lock, snapshot/review/dependency helpers, adapters,
Markdown commands and test ownership. Step 11 supplies full Java coverage/provenance and final
release-candidate validation. Consumer adoption later validates actual application/client behavior
and same-revision upstream equality. Static metadata/link/routing review at this step cannot certify
any of those future executions. Independent human authority review remains a Step 9 acceptance gate.
