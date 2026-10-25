<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Helper Reference](#helper-reference)
  - [Runtime and command owners](#runtime-and-command-owners)
  - [Dependency checks and lifecycle](#dependency-checks-and-lifecycle)
  - [Review and snapshot helpers](#review-and-snapshot-helpers)
  - [Evidence identity and compatibility](#evidence-identity-and-compatibility)
  - [Markdown and adapter templates](#markdown-and-adapter-templates)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Helper Reference

## Runtime and command owners

[CONTRIBUTING.md](../CONTRIBUTING.md) owns setup and checks. `scripts/framework.sh` verifies the
selected CPython 3.14.8 before delegating to `tools/framework_check.py`; a consumer can also invoke
the latter with its own verified interpreter and explicit roots. All operational imports are
standard library; `source` alone loads the declared development PyYAML dependency.

```sh
scripts/framework.sh source --framework-root "$FRAMEWORK_ROOT"
scripts/framework.sh integrity --consumer-root "$CONSUMER_ROOT" --framework-root "$FRAMEWORK_ROOT"
scripts/framework.sh freshness --consumer-root "$CONSUMER_ROOT" --framework-root "$FRAMEWORK_ROOT" --timeout 20
scripts/framework.sh compose --consumer-root "$CONSUMER_ROOT" --framework-root "$FRAMEWORK_ROOT" --language go --boundary api --require markdown-check
```

Variables above identify actual absolute checkout roots, not inferred sibling paths. The default
profile is `ai/profile.json`, relative to the consumer; override with `--profile`. Root discovery
must agree with `git rev-parse --show-toplevel`. Profile owner/cwd paths are consumer-root relative,
including framework-owned scripts reached through the declared `framework_path`. Absolute argv
executables are explicit provisions; relative executables resolve from their declared cwd. Required
executables must exist, but their arguments are not executed or proven successful by composition.
Arbitrary prose prerequisites still require caller verification. Missing capabilities/tools block
only their dependent request. Extra selected language components are not read for unrelated tasks;
selected house/operations components are returned with core. Optional version-1 `styles` maps
`java` to `google` or `local`; absence makes no style selection. Unknown styles fail explicitly.
Profile version 1 keeps branch selection; version 2 permits an optional canonical
`upstream_ref` such as `refs/tags/v1.2.3`. Version 1 rejects that field, and version 2 without it
also keeps branch selection. An older checker rejects version 2, so upgrade the framework checker
with the profile.

Checks reject unknown catalog/profile versions, missing workflows/templates, escaped owner paths,
artifact/source overlap, conflicting configuration and unsupported task options. Results are JSON
on stdout; sanitized diagnostics are on stderr. The composer returns selected shared paths,
consumer guides, capabilities and explicit styles; it never executes profile argv or shell text.
Static conflict policy validation does not replace actual nested-guide/client conflict handling.

For installed routing, add repeatable `--client codex` and/or `--client claude` to `compose`.
The `composition.installation` result reports `passed`, selected clients and checked paths only
when those clients were explicitly selected. With no `--client`, language/capability composition
remains available and installation reports `not_checked`; it cannot certify an adoption.

For each selected client, the consumer AGENTS.md must contain the rendered `AGENTS.md.in` block
from that pinned framework. Substitute `{{framework_path}}` and, for a custom `--profile`, the
profile path. Preserve local guidance around the block. Each of the six installed SKILL.md files
must match its rendered pinned template, apart from surrounding whitespace; keep custom policy
in local guides/profile rather than editing thin adapters. Claude additionally requires the
standalone `@AGENTS.md` import in CLAUDE.md. Missing files, altered names/targets, template drift
and paths escaping the consumer fail without repair. These structural checks do not establish
that a running client discovered or followed the files; actual client trials remain required.

## Dependency checks and lifecycle

Integrity selects the Git index gitlink by default, requiring an initialized clean dependency and
HEAD equality. `--commit <consumer-ref>` instead uses that commit's gitlink/configuration and never
falls back to the index. The current profile is separately validated and hashed, not reconstructed
from that commit. Reported committed-pin differences are evidence, not automatic repair.
`.gitmodules` must name the exact source/path and a full `refs/heads/` upstream ref. Unsafe source
or transport overrides are rejected. Ignored development outputs are not shared-source dirt;
tracked and non-ignored untracked changes, skip-worktree and assume-unchanged flags are blockers.

Freshness adds a bounded `ls-remote` query of the configured source/ref and requires exact equality
with HEAD/pin. Branch mode checks `.gitmodules`' full `refs/heads/` ref. With a version-2
`upstream_ref`, tag mode checks that exact release tag and compares its commit with HEAD/pin;
annotated tags are peeled before comparison. The result reports `ref_kind: tag`,
`configured_branch`, and `tag_object` (the annotated object ID, or `null` for a lightweight tag).
Offline integrity reports the selected tag without claiming remote verification. A missing,
invalid, or moved explicit tag fails online without branch fallback. Neither mode discovers the
newest release. Ahead, behind, rewritten, divergent, unavailable and missing refs are nonzero. No
cached upstream result substitutes for the query. Integrity/freshness/composition never fetch,
write indexes/refs, switch checkout, repair exclusions or install tools. They use restrictive
OS temporary output files and a work deadline of at most 30 seconds, with separate two-second
process-group teardown; stdout is bounded and remote stderr is suppressed to avoid secret leakage.
The initial transport environment disables prompts and global Git configuration; provision access
outside the helper. This does not establish whole-host/network containment.

Preparation, upgrades and rollback are explicit user operations, separate from checks: initialize
at the recorded gitlink; review a proposed revision with matching profile/adapters; stage the
reviewed pin only in the authorized adoption workflow; restore the previous dependency/profile/
adapter combination for rollback. Preserve unrelated work and local artifacts. The integration
fixtures exercise these operations only in owned repositories. Production consumer setup belongs
to its adoption step, and no upgrade/rollback mutation is hidden behind a validation command.

## Review and snapshot helpers

```sh
scripts/refresh_git_diff.sh "$CONSUMER_ROOT" main HEAD ai/artifacts/ticket/ticket-git-diff.txt
scripts/check_upstream_sync.sh "$CONSUMER_ROOT"
scripts/verify_published_pr.sh "$CONSUMER_ROOT" origin refs/heads/main "$BASE_SHA" origin refs/heads/feature "$HEAD_SHA"
```

Snapshot preserves the explicit-root four-argument contract and records resolved base/head/merge
base plus the committed three-dot patch. It excludes dirty work. The output must be in an existing
ignored consumer artifact directory, with the exact checkout-local exclusion and no indexed
artifact paths. For a nondefault artifact root, invoke `tools/git_helpers.py snapshot` directly
with `--artifact-root`. It never creates exclusions/directories and atomically preserves previous
evidence on failure. The patch has a 16 MiB bound; larger output fails explicitly.

Branch synchronization is optional strict review mode: fetch the configured branch upstream and
require exact HEAD equality. Published review requires host-reported full SHAs and valid full refs;
it fetches both revisions, verifies exact equality and a merge base, then queries both refs again
to detect movement. The caller must also recheck host PR metadata before using the result. Neither
uses local HEAD as a published-head substitute. Fetch writes object storage, FETCH_HEAD and possibly
remote-tracking refs; no application/worktree/index mutation or push is intended. These network
operations have one 30-second work deadline and two-second process-group teardown. The output
must be used with the existing review workflow's independent metadata and dirty-work checks.

## Evidence identity and compatibility

```sh
.venv/bin/python -B tools/evidence_check.py capture --consumer-root "$CONSUMER_ROOT" --base main --record ai/artifacts/ticket/identity.json --input ai/artifacts/ticket/ticket-content.md --input ai/profile.json --input AGENTS.md
.venv/bin/python -B tools/evidence_check.py check --consumer-root "$CONSUMER_ROOT" --base main --record ai/artifacts/ticket/identity.json --input ai/artifacts/ticket/ticket-content.md --input ai/profile.json --input AGENTS.md
```

Declare all relevant specification, source, fixture, profile and adapter inputs, including dirty
and untracked files. Capture writes only the validated artifact destination; check never changes
it. Version 1 records base/head, dirty status, selected index entries and SHA-256 input identities.
A changed specification/profile/adapter, index or head fails comparison. Unknown/future versions
and historical records without identities remain readable but cannot prove current validation;
preserve them and capture a new record after rerunning affected checks. Identity equality alone
is not a test pass, tool-environment identity or proof that the caller declared every dependency.
Record command/tool/environment/result evidence using the post-step workflow in addition.

## Markdown and adapter templates

`scripts/markdown.sh format|check <files...>` resolves the current Git checkout, or accepts an
explicit `--root`. Files must stay within that owner. Format runs pinned doctoc on selected files;
check uses disposable copies and fails on drift. Both require explicit provisioning of the tool
prefix; neither invokes npm/npx. A batch has a 30-second work deadline plus two-second teardown.
Split very large selections into explicit batches if needed.

`adapters/codex` and `adapters/claude` contain root-guide additions and six concrete skill templates
each. Substitute `{{framework_path}}` from the consumer profile when installing into `.agents/skills`
or `.claude/skills`; retain local root policy, use explicit consumer-root resolution, and discover
applicable nested guides before action. Claude's root template imports the consumer AGENTS file.
Template presence is structural evidence only; real Codex/Claude observations remain adoption gates.
