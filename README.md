<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [spec-first-ai-framework](#spec-first-ai-framework)
  - [Start here](#start-here)
  - [Current delivery boundary](#current-delivery-boundary)
  - [Adoption contract](#adoption-contract)
  - [Validation and release](#validation-and-release)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# spec-first-ai-framework

Shared specification-first workflows and selectable engineering guidance, composed with a
consumer-owned profile and a pinned Git submodule. The shared source owns lifecycle and safeguards;
consumers own business behavior, topology, tool/runtime pins, commands, artifacts and operations.

## Start here

- Framework contributors: [AGENTS.md](AGENTS.md) governs this checkout;
  [CONTRIBUTING.md](CONTRIBUTING.md) documents setup and validation.
- Consumer integration: [consumer.md](consumer.md) defines roots, authority, artifacts and routing.
- Language entry points: [Go](rules/go/README.md), [Java](rules/java/README.md) and [Python](rules/python/README.md).
  Each language folder contains its focused rules; shared rules remain directly under `rules/`.
- Components and workflow paths: [catalog.json](catalog.json).
- Source lineage and review boundaries: [extraction provenance](provenance/extraction.md).
- Reusable request examples: [prompts](prompts/README.md).
- Validation evidence: [evidence](rules/evidence.md) and [client scenarios](checks/client-compatibility.md).

## Current delivery boundary

Shared lifecycle, portable helpers and complete Go/Python/Java guidance are delivered as a local
release candidate. Six canonical workflows, five templates, selectable house/operations rules,
adapter templates, runtime locks and source/integrity/freshness/composition checks are included.
See the [helper reference](docs/helpers.md), [Java provenance](provenance/java.md) and semantic
[review scenarios](examples/java/README.md). Missing capabilities fail explicitly. Actual consumer
adoption/client/application checks and an authorized immutable release remain separate gates.

The existing Python example source is retained unchanged with its fast and disposable process
tests. Framework-owned fast/integration commands execute these examples; they are not application
contracts. Historical prototype/client trials do not certify this extracted source.

## Adoption contract

The selected consumer layout uses `ai/framework`, `ai/profile.json` and `ai/consumer-profile.md`.
The gitlink is the immutable pin; `.gitmodules` owns source/path/explicit upstream branch. Both
consumers must use the same unmodified revision. Preparation follows the pin; online freshness
separately requires clean HEAD/pin/upstream equality. Updates and rollback are explicit and preserve
unrelated work and historical artifacts. Follow [adoption](docs/adoption.md), [runtime ownership](docs/runtime.md),
[client verification](docs/clients.md) and [upgrades/rollback](docs/upgrades.md).
See [commands](rules/commands.md) for required semantics.

Codex and Claude Code local-checkout surfaces need actual root/nested loading and stage trials.
Hosted review remains an optional workflow mode, not additional client support. Consumer cutover
must preserve historical paths/references through local compatibility routing where needed.

## Validation and release

Before acceptance, compare source changes with the trusted baseline and obtain independent human
review of authority changes. Current static/manual evidence is recorded in the owning ticket,
not copied into this source tree. Final helper checks, actual client/application trials and fresh
upstream equality remain required before adoption. A local check does not authorize publication.

The framework is licensed under [MIT](LICENSE), selected by the maintainer. Preserve applicable
upstream notices; [release provenance](provenance/framework.md) records the Java coverage/rights
boundary. Publication ownership, visibility and direct authorization remain separate release gates;
upstream availability is not implied. No tracked runtime/cache/tool artifacts or consumer ticket
data belong in this repository.
