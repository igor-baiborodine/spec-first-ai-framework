<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Explicit Upgrades and Rollback](#explicit-upgrades-and-rollback)
  - [Select and review an upgrade](#select-and-review-an-upgrade)
    - [Before either method](#before-either-method)
    - [Old way: upgrade to a branch commit](#old-way-upgrade-to-a-branch-commit)
    - [New way: switch to or upgrade a release tag](#new-way-switch-to-or-upgrade-a-release-tag)
    - [Validate and commit](#validate-and-commit)
  - [Roll back the whole integration](#roll-back-the-whole-integration)
  - [Release and evidence boundary](#release-and-evidence-boundary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Explicit Upgrades and Rollback

## Select and review an upgrade

Choose either the existing branch workflow or the release-tag workflow. Both record an exact
framework commit in the consumer's submodule gitlink. The difference is what online freshness
compares that commit against:

| Method | Profile selection | Freshness passes when |
| --- | --- | --- |
| Old way: branch | Version 1 or 2, without `upstream_ref` | The pin equals the configured branch head now |
| New way: release tag | Version 2 with `upstream_ref` | The pin equals the selected tag's commit, even after main advances |

These examples assume an existing installation at `ai/framework`, profile `ai/profile.json`,
and approved source remote `origin`. For a new installation, use [adoption](adoption.md).
Run each step from the consumer repository root and stop if a command fails.

### Before either method

1. Check the consumer and dependency for existing work:

   ```sh
   git status --short
   git -C ai/framework status --short
   git -C ai/framework remote get-url origin
   git config -f .gitmodules --get submodule.ai/framework.branch
   ```

   Confirm the source URL is approved. Resolve dirty dependency state or overlapping consumer
   edits before continuing; preserve unrelated work. Initialize a missing dependency using
   `git submodule update --init -- ai/framework` before checking its status.

2. Record the current integration for review and possible rollback:

   ```sh
   PREVIOUS_CONSUMER_COMMIT=$(git rev-parse HEAD)
   git rev-parse HEAD:ai/framework
   git rev-parse :ai/framework
   git -C ai/framework rev-parse HEAD
   ```

   The first command records the parent commit. Confirm it contains the accepted profile,
   gitlink, adapters and local guides; resolve any existing staged integration changes first.

### Old way: upgrade to a branch commit

1. Keep the existing version-1 profile without `upstream_ref`. Version 2 without that field also
   uses branch mode. If switching back from tag mode, remove `upstream_ref` from the profile.
   Keep `.gitmodules`' branch as a full branch ref, such as `refs/heads/main`.

2. Fetch the configured branch and resolve its commit. This example assumes `refs/heads/main`;
   substitute the branch recorded in `.gitmodules` if different:

   ```sh
   git -C ai/framework fetch origin refs/heads/main
   REVIEWED_SHA=$(git -C ai/framework rev-parse --verify 'FETCH_HEAD^{commit}')
   git -C ai/framework log --oneline HEAD.."$REVIEWED_SHA"
   git -C ai/framework diff HEAD "$REVIEWED_SHA"
   ```

   Review the fetched changes before selecting that revision. If selecting an older framework
   checker that only supports version 1, the matching profile must also use version 1.

3. Check out the reviewed commit, then follow **Validate and commit** below:

   ```sh
   git -C ai/framework checkout --detach "$REVIEWED_SHA"
   ```

   If the branch advances afterward, the recorded pin still reproduces the same files, but online
   freshness fails until a subsequent reviewed upgrade matches the new branch head.

### New way: switch to or upgrade a release tag

1. Choose an approved published release that contains profile-version-2 support. `v1.0.0`
   predates that support. The `v1.2.3` below is illustrative; replace it with the actual selected
   release. Set the full tag ref, fetch it, and review its changes:

   ```sh
   TAG=refs/tags/v1.2.3
   git -C ai/framework fetch origin "$TAG"
   REVIEWED_SHA=$(git -C ai/framework rev-parse --verify 'FETCH_HEAD^{commit}')
   git -C ai/framework log --oneline HEAD.."$REVIEWED_SHA"
   git -C ai/framework diff HEAD "$REVIEWED_SHA"
   ```

   `FETCH_HEAD^{commit}` resolves both lightweight and annotated tags to their commit SHA.

2. Check out that reviewed commit:

   ```sh
   git -C ai/framework checkout --detach "$REVIEWED_SHA"
   ```

3. Edit only these fields in `ai/profile.json`, preserving the remaining consumer configuration:

   ```json
   "version": 2,
   "upstream_ref": "refs/tags/v1.2.3"
   ```

   Use the exact tag selected in step 1. Keep `.gitmodules`' branch as `refs/heads/main` (or its
   existing configured branch). The profile stores the tag name; Git stores its commit SHA in
   the gitlink. An older checker rejects version 2, so update the dependency and profile together.

4. Follow **Validate and commit** below. For later tag upgrades, repeat these steps with the next
   approved tag. No check automatically selects the newest release or falls back to a branch
   when the selected tag is missing or has moved.

### Validate and commit

1. Review any adapter or local-guide changes required by the selected framework version. Update
   them from that version's templates when necessary, preserving consumer-owned guidance.
   Stage the pin and profile, plus explicit paths for any matching adapter/guide edits:

   ```sh
   git add -- ai/framework ai/profile.json
   git rev-parse :ai/framework
   ```

   The printed gitlink must equal `REVIEWED_SHA`. Stage before validation because the default
   integrity check uses the index pin. Fetch writes Git objects/FETCH_HEAD; checkout changes the
   dependency files; add changes the consumer index. Checks perform none of those operations.

2. Run the consumer's bound integrity, composition, regression and freshness commands. The
   portable integrity/freshness equivalents below require `FRAMEWORK_PYTHON` to identify an
   absolute, provisioned CPython 3.14.8 interpreter; see [runtime setup](runtime.md):

   ```sh
   CONSUMER_ROOT=$(git rev-parse --show-toplevel)
   "$FRAMEWORK_PYTHON" -B ai/framework/tools/framework_check.py integrity --consumer-root "$CONSUMER_ROOT" --framework-root "$CONSUMER_ROOT/ai/framework"
   "$FRAMEWORK_PYTHON" -B ai/framework/tools/framework_check.py freshness --consumer-root "$CONSUMER_ROOT" --framework-root "$CONSUMER_ROOT/ai/framework" --timeout 20
   ```

   Integrity requires the clean submodule HEAD to equal the indexed gitlink. Freshness additionally
   requires that SHA to equal the current configured branch head or selected tag's commit.
   Use the [composition checks](helpers.md#runtime-and-command-owners) with explicit installed
   clients, and run relevant application, historical-link and actual-client trials. These two
   commands alone do not establish full consumer acceptance.

3. Review the entire proposed consumer change. After review and explicit commit authorization,
   commit it in the parent repository:

   ```sh
   git diff --cached --submodule=log
   git commit -m "chore: upgrade shared framework"
   ```

   Inspect staged, unstaged, untracked and generated files before committing; unrelated staged
   work must not be included. Commit authority does not authorize a push, merge, tag or release.

4. Check reproduction in a fresh clone of that consumer commit:

   ```sh
   git submodule update --init -- ai/framework
   git rev-parse HEAD:ai/framework
   git -C ai/framework rev-parse HEAD
   ```

   Both SHAs must equal the reviewed commit even after upstream main advances. Tag-mode freshness
   still passes while the selected tag resolves to that SHA; branch-mode freshness may now fail.
   Never use `submodule update --remote` to reproduce a recorded pin.

## Roll back the whole integration

Identify the previous accepted consumer revision and its matching framework/profile/adapters/
local routing. Compare exact selected paths with current unrelated edits before restoring anything.
If they overlap, resolve ownership; do not reset, stash, clean or overwrite as automatic recovery.
Explicitly restore only the reviewed integration paths from that revision and stage that coherent
combination, then initialize/update the dependency to its restored index pin with
`git submodule update --init -- ai/framework`.

For a reviewed previous consumer commit, a path-scoped example is:

```sh
git restore --source="$PREVIOUS_CONSUMER_COMMIT" --staged --worktree -- .gitmodules ai/framework ai/profile.json
git submodule update --init -- ai/framework
git rev-parse :ai/framework
git -C ai/framework rev-parse HEAD
```

Include exactly the matching adapters and local guides in the reviewed restore path set. Do not
run the example until those paths have been checked for unrelated edits. The previous profile may
select an older tag or use version-1 branch mode; restore it with its matching checker and gitlink.

Preserve ignored historical ticket records and unrelated staged/unstaged/untracked files. Verify
before/after manifests for those protected paths and re-run local integrity/composition and
relevant compatibility checks. A historical rollback is reproducible even when version-1 branch
mode fails current upstream equality. A previous tag passes online freshness only while that
exact tag still resolves to its recorded commit. Report a failure; never move the pin merely to
make freshness green.
An unavailable historical commit is a blocker, not permission to substitute another revision.

## Release and evidence boundary

A content manifest identifies an uncommitted candidate for review; only an authorized commit
establishes its immutable Git revision. Publication to a feature branch does not satisfy equality
with a configured main ref. Before final consumer acceptance, the reviewed revision must be
retrievable from the approved source and equal its freshly observed selected tag or configured
branch. Verify destination, ownership, visibility, provenance/license and explicit publication
authority separately.

An upstream advance or later source/profile/adapter/specification change invalidates affected
acceptance evidence. Preserve historical results; re-run or document an exact unaffected judgment.
Freeze shared source before final consumer trials, and reconcile both consumers to the same
unmodified revision if a release change is necessary.
