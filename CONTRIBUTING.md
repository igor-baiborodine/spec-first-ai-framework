<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Contributing](#contributing)
  - [Script language choices](#script-language-choices)
  - [Setup](#setup)
  - [Checks and scope](#checks-and-scope)
  - [Squash releases and publication](#squash-releases-and-publication)
  - [Portable helper interfaces](#portable-helper-interfaces)
  - [License and provenance](#license-and-provenance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Contributing

Read [AGENTS.md](AGENTS.md) for contributor scope and [consumer.md](consumer.md) for exported
consumer behavior. Keep rule changes traceable to observed practice and independent expected
outcomes. Submit a focused branch and pull request describing the problem, final behavior,
validation and remaining limitations. Authority changes require independent maintainer review.

## Script language choices

Use shell for simple command wiring and Python for auxiliary scripts that parse structured data,
validate repository state, or orchestrate processes. JavaScript is a specific exception for the
issue-3 release calculator: the reviewed D01 decision selected the Node Conventional Commit
parser, preset, and SemVer libraries, so the adapter calls those libraries directly. Node was
already a development prerequisite for Markdown tooling; the release packages are exact-pinned in
`package-lock.json` and exercised by `make release-test`. This exception does not make JavaScript
the default for new scripts or change the Python ownership of consumer checks.

## Setup

The initial supported environment is POSIX with Git, a shell, uv 0.13.1 and CPython 3.14.8.
Node tooling was tested with Node 24.13.0 and npm. The lockfile contains doctoc 2.5.0 and exact
release-calculation libraries. Workflow lint setup is checksum-verified for Linux amd64 with
actionlint 1.7.12. Other versions and platforms are unverified. Install/provision those
prerequisites explicitly before setup.

From this checkout root:

```sh
make setup
make markdown-setup
make actionlint-setup
make gh-setup
```

Setup downloads the locked packages and creates `.venv`, `node_modules`, or the ignored
`.tools/actionlint/1.7.12` and `.tools/gh/2.103.0` binaries; uv/npm caches can also be written.
Both archives are checked against their reviewed Linux amd64 SHA-256 before extraction. `uv.lock` and
`package-lock.json` carry resolved Python/Node versions and artifact hashes.
Normal checks do not invoke setup, download packages or substitute an interpreter. Dependencies
are development-only; consumer integrity/freshness/composition use Python's standard library.
PyYAML is imported by source checking for real YAML frontmatter validation and by the fast CI
contract tests. Runtime consumer integrity/freshness/composition does not import it.

The owner-managed interpreter is `.venv/bin/python`. `PYTHON=/absolute/path/to/python` is
supported if it is CPython 3.14.8; development checks also require the exact declared package pins.
Development checks compare the selected environment against the lock offline with `uv sync
--locked --check`; they do not install or resolve new versions. Python children use the selected interpreter. Run `make help` for the safe default interface.

## Checks and scope

```sh
make runtime-check development-check
make format PYTHON_FILES='tools tests examples/python-testing'
make format-check lint test-collect test-fast test-integration source-check
make workflow-check workflow-test
make gh-check
make release-test
make check test-collect
make markdown-format MARKDOWN_FILES='README.md CONTRIBUTING.md'
make markdown-check MARKDOWN_FILES='README.md CONTRIBUTING.md'
```

Use only task-owned paths for format/Markdown operations. Python defaults cover the framework's
handwritten tools, tests and preserved examples; narrow `PYTHON_FILES` for subsequent changes.
Format mutates selected files; format-check/lint never fix them. Ruff caches and bytecode are
disabled by Make. Markdown check uses disposable copies; its originals remain byte-identical.
`AI_DOCTOC_DIR` can point to another explicitly provisioned prefix containing
`node_modules/doctoc/package.json` at version 2.5.0. No `npx` installation occurs during checks.

`test-collect` checks no-path default discovery and the separately selected example integration
suite. Fast tests cover pure decisions/fakes and example logic. Integration tests create local
Git repositories, synthetic commits and subprocesses in owned temporary directories; they
never target a shared service. Fixtures clean themselves up. They include the prototype's
48 cases plus extraction regressions. Routing regressions reject incomplete Go, Java and Python
routes. Installed-client cases cover selection, missing/altered/escaped adapters, root routing,
custom profiles, standard-library operation and explicit unchecked language-only results.
Non-Make command bindings remain supported and are never executed by composition.
Java routing uses the complete delivered rule family;
semantic review scenarios live in [Java examples](examples/java/README.md). Those scenarios are
not executable Java application tests. No client/application acceptance suite is implied by `make check`.

`workflow-check` uses the preinstalled, checksum-verified actionlint 1.7.12. It lints every
`.github/workflows/*.yml` or `*.yaml` file without installing dependencies; ShellCheck and
pyflakes integration are intentionally disabled. `workflow-test` checks that an invalid GitHub
expression fails the owning lint command. `make check` includes both through `workflow-test`,
so a missing binary or a lint failure stops the gate. `ACTIONLINT=/absolute/path/to/actionlint`
may select another copy only when its binary checksum and version match the pinned release.

The `Framework Validation` GitHub Actions workflow runs on every pull request and main push
without path filters. Its validation job uses read-only `contents` permission, checks out full
history, provisions dependencies in explicit setup steps, runs `make check test-collect`, and
checks all tracked Markdown files. PR title/body inputs are checked on open, synchronize, reopen,
and edit. The title must be a Conventional Commit header; a breaking-change footer belongs in
the proposed squash body. This PR check is preliminary: before squash merging, inspect the final
title and body in the merge dialog and retain the footer. Release calculation checks actual main
commits after merge. The workflow does not publish a release. Local success does not prove that a
hosted run or repository settings enforce the same checks.

`make release-test` checks the release adapter with disposable Git histories. For a local preview
with complete history and the baseline tag available, run
`node tools/release-calculation.mjs calculate --repo . --head <full-validated-SHA>`.
The command emits JSON with the previous tag, highest bump, and candidate tag or `null`; it writes
no tag, release, package version, or changelog. To check a proposed squash message saved locally,
run `node tools/release-calculation.mjs validate-message --message-file <path>`.

Make resolves this checkout from its own file: root `make`, `make -C /path/to/framework`, and
nested `make -f /path/to/framework/Makefile` work. Recursive callers must use `$(MAKE)` and pass
an explicit absolute interpreter if overriding it. Make maps a failed recipe to its own nonzero
exit (normally 2); direct helper CLIs use 0 success, 1 operational failure, 2 usage error,
130 interruption and 143 handled termination.

## Squash releases and publication

Use a Conventional Commit title for the pull request and inspect the proposed squash title and
body in the merge dialog. Keep a `BREAKING CHANGE:` footer in the final body when the change is
breaking. The PR validation checks title/body inputs; release calculation checks the actual
commits on main. A valid PR title does not repair a malformed squash commit. This ticket supports
squash merges only; a maintainer must configure and verify repository merge settings separately.

The single framework version stream starts at `v1.0.0`. Across all commits since the previous
reachable release, `fix` and `perf` require a patch, `feat` requires a minor, and a breaking marker
or footer requires a major release, including on another type. The highest required bump wins.
Nonbreaking docs, chore and test commits alone produce no release. The private package version
is unrelated to the framework tag. Release notes cover the selected range; a cumulative changelog
is deferred in the [ledger](docs/nice-to-have-ledger.md).

`Framework Validation` checks PRs and main pushes with read-only contents permission. After a
successful main-push run, `Framework Release` checks the exact validated SHA and current main,
then may create its tag and GitHub Release with job-scoped `contents: write`. It does not publish
from PRs, forks or manual validation. Maintainers own the repository's Actions permissions, merge
settings and any branch protection; these local files do not prove those settings or hosted event
behavior. Use the [release workflow](.github/workflows/release.yml) and
[publisher](tools/release_publish.py) as the implementation contract. New releases are automatically
marked Latest. Before tag and release creation, the publisher requires the candidate version to
exceed the currently designated Latest version, then rechecks the validated main SHA. It verifies
the Latest designation after publishing. Serialized workflow execution prevents competing workflow
runs from replacing a newer release with an older one. Manual release changes are outside that
serialization boundary; GitHub reads and writes are not atomic, and unexpected readback stops for
inspection. Completed reruns and non-releasing ranges remain no-ops; they do not relabel existing
releases, including releases created under the earlier manual-designation policy.

A rerun of the same completed version/SHA is a no-op. A conflicting tag, missing history, stale
run, or partial tag-without-release state stops with an error for maintainer inspection. Do not
force-move the tag or assume a rerun repairs the missing release. Automatic recovery and consumer
upgrade PRs remain deferred in the [ledger](docs/nice-to-have-ledger.md). Local disposable tests
and workflow lint do not establish a successful hosted run, actual token permissions, or a live
release; record those observations separately before claiming them.

## Portable helper interfaces

The [helper reference](docs/helpers.md) describes exact arguments, output, deadlines, artifact
ownership, local writes and network effects. Profile commands are declarations, never shell
programs evaluated by the composer. Inspect their owner before executing them. Source integrity,
offline dependency integrity, fresh upstream equality and actual agent behavior are distinct
checks. Retain failed/stale evidence rather than relabeling it as success.

Keep the six workflows, five templates, catalog and twelve client skill adapters consistent.
Add regression cases for changed routing, missing bindings, path escapes, permissions and
failure propagation. Examples are independent expected outcomes, not copies of new helper output.
Changes to a pin/configuration/test/specification require affected evidence to be reassessed.

## License and provenance

Contributions are intended for distribution under the [MIT license](LICENSE). Confirm you may
contribute the material under those terms and retain applicable upstream notices. Record copied
or derived material in [extraction provenance](provenance/extraction.md); third-party tools keep
their own licenses. The initial copyright holder is Igor Baiborodine, matching the source history
and the maintainer's explicit MIT selection. The [Java derivation](provenance/java.md) and
[release provenance](provenance/framework.md) record coverage, additional safeguards, measured
deviations and the rights/notice boundary. Do not add a contributor agreement or certify
third-party relicensing by inference. Publication, commits and pushes retain their separately authorized workflows.
