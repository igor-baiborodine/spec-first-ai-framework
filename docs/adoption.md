<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Consumer Adoption](#consumer-adoption)
  - [Prepare a reviewed dependency](#prepare-a-reviewed-dependency)
  - [Bind local ownership](#bind-local-ownership)
  - [Install routing and validate](#install-routing-and-validate)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Consumer Adoption

## Prepare a reviewed dependency

Adoption is a consumer change: preserve its root guide, nested rules, artifact policy, historical
links and application commands. Review [consumer composition](../consumer.md) and the selected
[language routes](../catalog.json). Choose an immutable revision available from the approved source;
a dirty framework tree or an unpublished local candidate cannot be the final release pin.

For an existing committed installation, inspect consumer/submodule status and local source
configuration first. Resolve overlapping work before this explicit preparation command, run at
the consumer root:

```sh
git submodule update --init -- ai/framework
```

It retrieves/checks out the recorded index gitlink, not the latest upstream branch. Do not use
`--remote` for preparation. Inspect submodule HEAD/tree and run the bound integrity command with
the [declared runtime](runtime.md). Normal checks never initialize or repair the dependency.
An already prepared installation supports offline local checks; a fresh clone may need network.

For a first adoption with no existing submodule, the approved change uses `git submodule add`
with the verified source and `ai/framework` path, explicitly selects the reviewed detached commit,
and records `.gitmodules` branch as the full `refs/heads/main`. Adding a submodule stages files;
inspect that index before proceeding. The initial add may select current upstream, so it is not
itself evidence that the reviewed pin was selected. Do not overwrite an occupied path or infer
remote creation/publication permission. See [upgrades](upgrades.md) for selection/review semantics.

## Bind local ownership

Create `ai/profile.json` version 1 and `ai/consumer-profile.md`. This illustrative profile requires
real existing owner files and an implemented command before it can serve as an installation:

```json
{
  "version": 1,
  "consumer": "example-java-consumer",
  "framework_path": "ai/framework",
  "components": ["core", "java"],
  "guides": ["AGENTS.md", "ai/consumer-profile.md"],
  "tool_sources": ["pom.xml", "scripts/ai/java.sh"],
  "artifact_root": "ai/artifacts",
  "issue_sync": "consumer guide owns provider, exact body comparison and publication permission",
  "conflicts": "stop-and-report",
  "styles": {"java": "google"},
  "commands": {
    "unit": {
      "owner": "scripts/ai/java.sh",
      "cwd": ".",
      "argv": ["scripts/ai/java.sh", "unit"],
      "prerequisites": "consumer-declared JDK, build tool and dependency cache",
      "effects": "build output and declared local caches",
      "scope": "consumer-defined unit modules and discovery"
    }
  }
}
```

Supply every capability required by the chosen workflows: artifact preflight, issue synchronization
when applicable, Markdown format/check, snapshot/review helpers and language checks. The
[command contract](../rules/commands.md) defines their behavior. Bind exact argv/cwd/owner,
prerequisites, effects and scope; command declarations are not executed by composition. Never add
successful no-op bindings to satisfy missing capabilities. Verify application pins through their
local POM/Make/configuration sources instead of copying them into shared rules.

Select only needed components. Core is mandatory; house/operations are explicit selections.
Java `google` and `local` are supported style choices; Insurance Hub's legacy Java uses local.
Omit Java and its style map for a Go-only consumer. A task in a mixed consumer still loads only
its affected language and boundary routes.

## Install routing and validate

Retain local authority in AGENTS.md and add the exported consumer/profile route. Install six
thin workflow adapters per selected client from [adapter templates](../adapters/), substituting
`{{framework_path}}` with `ai/framework`. Codex uses `.agents/skills`; Claude uses `.claude/skills`
and a root CLAUDE.md import. Preserve existing local instructions and any still-used historical
links/anchors via reviewed local redirects. See [client trials](clients.md).

Before writing consumer artifacts, the maintainer must configure the exact local exclusion
`/ai/artifacts/` (or the adopted root), and verify ignored paths plus empty indexed/staged artifact
listings. The framework never edits exclusions or untracks data. Existing records retain their
resolved directories; new evidence fields do not invalidate historical readability.

Use the bound integrity and compose checks with explicit roots and required capabilities, then
run actual owning language/application checks. For example, with verified absolute interpreter
`FRAMEWORK_PYTHON` and absolute `CONSUMER_ROOT`, from the consumer root:

```sh
"$FRAMEWORK_PYTHON" -B ai/framework/tools/framework_check.py integrity --consumer-root "$CONSUMER_ROOT" --framework-root "$CONSUMER_ROOT/ai/framework"
"$FRAMEWORK_PYTHON" -B ai/framework/tools/framework_check.py compose --consumer-root "$CONSUMER_ROOT" --framework-root "$CONSUMER_ROOT/ai/framework" --language java --boundary api --boundary test --require unit
"$FRAMEWORK_PYTHON" -B ai/framework/tools/framework_check.py freshness --consumer-root "$CONSUMER_ROOT" --framework-root "$CONSUMER_ROOT/ai/framework" --timeout 20
```

Check JSON reports identify the index pin; use `--commit <consumer-ref>` only when explicitly
validating that commit, retaining the separately reported current profile identity. Freshness
must query the configured source/ref now. Failed/offline equality blocks adoption acceptance;
it does not prevent reproducible prepared local work. Perform actual root/nested client trials
and record identities/results before acceptance. Static success is insufficient.
