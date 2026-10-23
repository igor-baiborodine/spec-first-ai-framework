<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Runtime and Tool Ownership](#runtime-and-tool-ownership)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Runtime and Tool Ownership

Reading Markdown guidance needs no Go, Java or Python toolchain. Executing framework helpers needs
the declared framework runtime; application validation separately needs the consumer's tools.

| Operation | Owner and prerequisite | Effects and failure |
| --- | --- | --- |
| Integrity, freshness, compose, snapshot/evidence helpers | Framework helper contract, CPython 3.14.8, Git and POSIX shell for launchers | Standard library only; missing/wrong runtime fails without installation; freshness queries the configured upstream |
| Source validation and development tests | Framework pyproject/uv.lock and `.python-version`; uv 0.13.1, locked pytest/Ruff/PyYAML | Explicit setup creates environment/cache; checks verify offline lock identity; source mode alone imports YAML |
| Markdown format/check | Owning scripts and package lock; provisioned doctoc 2.5.0 with Node/npm | Format changes selected files; check uses owned temporary copies; neither installs |
| Java/Go/application checks | Consumer command/configuration owners | JDK/Go/Maven/plugins/containers and scan data are local selections; no sibling checkout is required |

[CONTRIBUTING.md](../CONTRIBUTING.md) lists exact framework setup/check commands. Framework setup
is explicit, separate from consumer preparation; installing a submodule does not run it. The
framework `.venv` is a contributor default, not a requirement that each consumer install a duplicate
environment. A consumer can bind a verified absolute CPython interpreter. Operational helpers run
without pytest/Ruff/PyYAML; source checks require their development environment. Do not fall back
to system Python or auto-install packages when a check fails.

The tested development surface is POSIX with CPython 3.14.8, uv 0.13.1 and Node 24.13.0. Other
platforms/runtimes are unverified. Client versions in [clients](clients.md) are observed identities,
not permanent runtime pins. Runtime declarations are not evidence of actual compatibility.

Helpers accept explicit roots and profile paths, return JSON for successful checks and sanitized
diagnostics for failures. Direct CLI statuses are 0/1/2/130/143; Make can map failures to 2.
Git/process operations have a maximum 30-second work budget and separate bounded teardown;
see [helper details](helpers.md) for effects, temporary files and supported overrides. Source,
local integrity, upstream equality, application results and client actions remain distinct evidence.
