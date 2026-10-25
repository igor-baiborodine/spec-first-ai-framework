<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Consumer Adoption](#consumer-adoption)
  - [Prepare a reviewed dependency](#prepare-a-reviewed-dependency)
    - [1. Choose the source and release tag](#1-choose-the-source-and-release-tag)
    - [2. Add the submodule and select the tag's commit](#2-add-the-submodule-and-select-the-tags-commit)
  - [Bind local ownership](#bind-local-ownership)
    - [3. Create the consumer profile and local guidance](#3-create-the-consumer-profile-and-local-guidance)
  - [Install routing and validate](#install-routing-and-validate)
    - [4. Install the selected clients' routing](#4-install-the-selected-clients-routing)
    - [5. Stage and validate the complete integration](#5-stage-and-validate-the-complete-integration)
    - [6. Review and commit the consumer change](#6-review-and-commit-the-consumer-change)
    - [7. Verify a fresh clone](#7-verify-a-fresh-clone)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Consumer Adoption

**Recommended for new consumers: select a published release tag and use profile version 2.**
The profile records which tag to verify, and the consumer's submodule gitlink records its exact
commit. This keeps the installation reproducible and allows freshness checks to pass when main
advances beyond that release. Branch mode remains supported for existing consumers; see
[upgrades](upgrades.md) for both upgrade methods.

Follow the steps below for a first installation at `ai/framework`. They assume Git, access to
the approved source, and a consumer repository with an existing commit. Run commands from the
consumer root and stop if any command fails. Preserve its root guide, nested rules, artifact
policy, historical links and application commands.

## Prepare a reviewed dependency

### 1. Choose the source and release tag

Start in the consumer repository and inspect existing work:

```sh
CONSUMER_ROOT=$(git rev-parse --show-toplevel)
cd "$CONSUMER_ROOT"
git status --short
```

Resolve overlapping changes before proceeding. The `ai/framework` path must be available for
the new submodule. If the consumer already has a framework installation, follow
[upgrades](upgrades.md) instead of adding it again.

Confirm the source URL, inspect its releases, and choose a specific approved tag containing
profile-version-2 support. `v1.0.0` predates that support. The `v1.2.3` below is an example;
replace it with the actual approved release before continuing. An unpublished candidate or
dirty framework tree cannot be the final adoption pin.

```sh
SOURCE=https://github.com/igor-baiborodine/spec-first-ai-framework.git
git ls-remote --tags "$SOURCE"
TAG=refs/tags/v1.2.3
```

Review that release's changes and [consumer composition](../consumer.md). The commands below
use the selected tag explicitly; they do not select the newest release automatically.

### 2. Add the submodule and select the tag's commit

```sh
git submodule add "$SOURCE" ai/framework
git config -f .gitmodules submodule.ai/framework.branch refs/heads/main
git -C ai/framework fetch origin "$TAG"
REVIEWED_SHA=$(git -C ai/framework rev-parse --verify 'FETCH_HEAD^{commit}')
git -C ai/framework checkout --detach "$REVIEWED_SHA"
git add -- .gitmodules ai/framework
git rev-parse :ai/framework
```

The printed gitlink must equal `REVIEWED_SHA`. `FETCH_HEAD^{commit}` resolves both lightweight
and annotated tags to their commit SHA. The initial submodule add can check out branch HEAD;
the explicit fetch and detached checkout select the reviewed release. Keep `.gitmodules`' branch
as `refs/heads/main`; the profile created next selects the tag for freshness checks.

## Bind local ownership

### 3. Create the consumer profile and local guidance

Use the profile example from the selected release as a starting point, only if `ai/profile.json`
does not already exist:

```sh
cp ai/framework/profile.example.json ai/profile.json
```

Set `version` to 2 and `upstream_ref` to the exact `TAG` from step 1. Set `consumer` to your
repository's name, select its language components, and replace example guides, tool sources
and commands with real consumer owners. Create `ai/consumer-profile.md` to document those local
choices, tool prerequisites, artifact policy and issue synchronization procedure.

The following illustrative binding requires real existing owner files and an implemented command
before it can serve as an installation:

```json
{
  "version": 2,
  "upstream_ref": "refs/tags/v1.2.3",
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

Replace `v1.2.3` with the approved tag used above; the example does not claim that version is
published. Do not put `REVIEWED_SHA` in the profile or change `.gitmodules`' branch to a tag.
Version 1 without `upstream_ref` remains the supported branch-head mode. An older checker cannot
validate version 2, and a version-1 profile must not contain `upstream_ref`.

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

### 4. Install the selected clients' routing

Retain local authority in AGENTS.md and add the exported consumer/profile route. Install six
thin workflow adapters per selected client from [adapter templates](../adapters/), substituting
`{{framework_path}}` with `ai/framework`. Codex uses `.agents/skills`; Claude uses `.claude/skills`
and a root CLAUDE.md import. Preserve existing local instructions and any still-used historical
links/anchors via reviewed local redirects. See [client trials](clients.md).

Use templates from the checked-out release. The source/destination mapping is:

| Selected client | Source under `ai/framework/` | Consumer destination |
| --- | --- | --- |
| Codex | `adapters/codex/AGENTS.md.in` | Merge the rendered block into `AGENTS.md` |
| Codex | `adapters/codex/skills/<name>/SKILL.md.in` | `.agents/skills/<name>/SKILL.md` |
| Claude | `adapters/claude/AGENTS.md.in` | Merge the rendered block into `AGENTS.md` |
| Claude | `adapters/claude/CLAUDE.md.in` | Merge the `@AGENTS.md` import into `CLAUDE.md` |
| Claude | `adapters/claude/skills/<name>/SKILL.md.in` | `.claude/skills/<name>/SKILL.md` |

Render `{{framework_path}}` as `ai/framework`. Install each of the six concrete skill templates
for every selected client. Preserve existing files' local policy rather than overwriting it;
the [rendering contract](helpers.md#runtime-and-command-owners) explains the required exact content.

Before writing consumer artifacts, the maintainer must configure the exact local exclusion
`/ai/artifacts/` (or the adopted root), and verify ignored paths plus empty indexed/staged artifact
listings. The framework never edits exclusions or untracks data. Existing records retain their
resolved directories; new evidence fields do not invalidate historical readability.

### 5. Stage and validate the complete integration

Stage the profile, local guidance and reviewed pin, plus explicit paths for the client adapters
installed in step 4. Stage before checking because integrity uses the index gitlink:

```sh
git add -- .gitmodules ai/framework ai/profile.json ai/consumer-profile.md AGENTS.md
git rev-parse :ai/framework
```

The printed SHA must still equal `REVIEWED_SHA`. Set `FRAMEWORK_PYTHON` to an absolute, verified
CPython 3.14.8 interpreter from the consumer's existing [runtime owner](runtime.md). If none is
available, explicitly provision the framework environment using uv 0.13.1:

```sh
make -C ai/framework setup
FRAMEWORK_PYTHON="$CONSUMER_ROOT/ai/framework/.venv/bin/python"
```

Setup installs locked development dependencies and writes the ignored environment/cache. Normal
checks never install packages. With the interpreter selected, run integrity, composition and
online freshness. This composition example matches the Java profile above and both clients;
adapt the language, boundaries, required commands and clients to the actual installation:

```sh
"$FRAMEWORK_PYTHON" -B ai/framework/tools/framework_check.py integrity --consumer-root "$CONSUMER_ROOT" --framework-root "$CONSUMER_ROOT/ai/framework"
"$FRAMEWORK_PYTHON" -B ai/framework/tools/framework_check.py compose --consumer-root "$CONSUMER_ROOT" --framework-root "$CONSUMER_ROOT/ai/framework" --language java --boundary api --boundary test --require unit --client codex --client claude
"$FRAMEWORK_PYTHON" -B ai/framework/tools/framework_check.py freshness --consumer-root "$CONSUMER_ROOT" --framework-root "$CONSUMER_ROOT/ai/framework" --timeout 20
```

Pass `--client` for every client selected for this adoption (the example selects both).
Install root blocks and skill files using the [rendering contract](helpers.md#runtime-and-command-owners).
A language-only compose result reports installation `not_checked` and is insufficient for adoption.

Check JSON reports identify the index pin; use `--commit <consumer-ref>` only when explicitly
validating that commit, retaining the separately reported current profile identity. Freshness
must query the selected tag from the configured source now; it does not select the latest tag.
The resolved tag commit, clean submodule HEAD and indexed gitlink must match. Failed/offline
equality blocks adoption acceptance; it does not prevent reproducible prepared local work.
Run the owning language/application checks and actual root/nested client trials, and record their
identities/results before acceptance. Static success is insufficient.

### 6. Review and commit the consumer change

Inspect the full staged, unstaged, untracked and generated change, including the pin, profile,
adapters and guides. After review and explicit consumer commit authorization:

```sh
git diff --cached --submodule=log
git commit -m "chore: adopt shared framework release"
```

Exclude unrelated staged work from this commit. This parent commit stores the exact framework
SHA and its matching configuration. Push and merge require their own authorization.

### 7. Verify a fresh clone

In a fresh clone checked out at that consumer commit, run:

```sh
git submodule update --init -- ai/framework
git rev-parse HEAD:ai/framework
git -C ai/framework rev-parse HEAD
```

Both printed SHAs must equal the release commit from step 2, even if upstream main has advanced.
Initialization may need network access; a prepared dependency supports offline integrity checks.
Do not use `--remote` to reproduce the committed pin. For later releases or rollback, follow
the [upgrade guide](upgrades.md).
