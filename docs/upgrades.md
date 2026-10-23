<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Explicit Upgrades and Rollback](#explicit-upgrades-and-rollback)
  - [Select and review an upgrade](#select-and-review-an-upgrade)
  - [Roll back the whole integration](#roll-back-the-whole-integration)
  - [Release and evidence boundary](#release-and-evidence-boundary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Explicit Upgrades and Rollback

## Select and review an upgrade

Work from the consumer root. Record current committed/index gitlinks, submodule HEAD/tree/status,
profile/adapters, relevant local guides and unrelated work. Confirm the intended upstream source
and full ref. Dirty or conflicting dependency state requires resolution before mutation; checks
never reset it. Review the proposed framework change and matching profile/adapters, including
workflow authority and historical link compatibility.

Once the adoption/update scope is authorized, explicitly fetch the approved source in the
submodule and select the reviewed full commit. For example, with verified values and clean
nonconflicting state:

```sh
git -C ai/framework fetch origin refs/heads/main
git -C ai/framework checkout --detach "$REVIEWED_SHA"
git add -- ai/framework ai/profile.json
```

Fetch updates Git object/FETCH_HEAD state; checkout changes dependency files; add stages the
candidate pin/profile. Inspect source configuration first; fetching does not prove REVIEWED_SHA
is the required upstream target. Update and explicitly stage matching local adapters/guides only
within the reviewed scope. Never use `submodule update --remote`, pull or reset inside a check.
A successful source check does not authorize these mutations or a commit/publication.

Run offline integrity and task composition against the candidate index, language/application
regressions, historical-link and actual-client trials, and fresh upstream equality. Current
acceptance requires HEAD = checked gitlink = freshly observed configured ref, even if local
history is ahead/diverged. Preserve results and exact identities. Commit only after full change
review and explicit authorization; push/merge/tag/visibility require their own scope.

## Roll back the whole integration

Identify the previous accepted consumer revision and its matching framework/profile/adapters/
local routing. Compare exact selected paths with current unrelated edits before restoring anything.
If they overlap, resolve ownership; do not reset, stash, clean or overwrite as automatic recovery.
Explicitly restore only the reviewed integration paths from that revision and stage that coherent
combination, then initialize/update the dependency to its restored index pin with
`git submodule update --init -- ai/framework`.

Preserve ignored historical ticket records and unrelated staged/unstaged/untracked files. Verify
before/after manifests for those protected paths and re-run local integrity/composition and
relevant compatibility checks. A historical rollback is reproducible even when it fails current
upstream equality. Report that failure; never move the pin forward merely to make freshness green.
An unavailable historical commit is a blocker, not permission to substitute another revision.

## Release and evidence boundary

A content manifest identifies an uncommitted candidate for review; only an authorized commit
establishes its immutable Git revision. Publication to a feature branch does not satisfy equality
with a configured main ref. Before final consumer acceptance, the reviewed revision must be
retrievable from the approved source and equal its freshly observed selected ref. Verify destination,
ownership, visibility, provenance/license and explicit publication authority separately.

An upstream advance or later source/profile/adapter/specification change invalidates affected
acceptance evidence. Preserve historical results; re-run or document an exact unaffected judgment.
Freeze shared source before final consumer trials, and reconcile both consumers to the same
unmodified revision if a release change is necessary.
