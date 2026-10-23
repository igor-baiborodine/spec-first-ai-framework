<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Contributing](#contributing)
  - [Setup](#setup)
  - [Checks and scope](#checks-and-scope)
  - [Portable helper interfaces](#portable-helper-interfaces)
  - [License and provenance](#license-and-provenance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Contributing

Read [AGENTS.md](AGENTS.md) for contributor scope and [consumer.md](consumer.md) for exported
consumer behavior. Keep rule changes traceable to observed practice and independent expected
outcomes. Submit a focused branch and pull request describing the problem, final behavior,
validation and remaining limitations. Authority changes require independent maintainer review.

## Setup

The initial supported environment is POSIX with Git, a shell, uv 0.13.1 and CPython 3.14.8.
Markdown tooling was tested with Node 24.13.0 and requires npm plus doctoc 2.5.0. Other versions
and platforms are unverified. Install/provision those prerequisites explicitly before setup.

From this checkout root:

```sh
make setup
make markdown-setup
```

Setup downloads the locked packages and creates `.venv` or `node_modules`; uv/npm caches can
also be written. `uv.lock` and `package-lock.json` carry resolved versions and artifact hashes.
Normal checks do not invoke setup, download packages or substitute an interpreter. Dependencies
are development-only; consumer integrity/freshness/composition use Python's standard library.
PyYAML is imported only by the source-check operation for real YAML frontmatter validation.

The owner-managed interpreter is `.venv/bin/python`. `PYTHON=/absolute/path/to/python` is
supported if it is CPython 3.14.8; development checks also require the exact declared package pins.
Development checks compare the selected environment against the lock offline with `uv sync
--locked --check`; they do not install or resolve new versions. Python children use the selected interpreter. Run `make help` for the safe default interface.

## Checks and scope

```sh
make runtime-check development-check
make format PYTHON_FILES='tools tests examples/python-testing'
make format-check lint test-collect test-fast test-integration source-check
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

Make resolves this checkout from its own file: root `make`, `make -C /path/to/framework`, and
nested `make -f /path/to/framework/Makefile` work. Recursive callers must use `$(MAKE)` and pass
an explicit absolute interpreter if overriding it. Make maps a failed recipe to its own nonzero
exit (normally 2); direct helper CLIs use 0 success, 1 operational failure, 2 usage error,
130 interruption and 143 handled termination.

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
