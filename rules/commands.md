<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Command Ownership](#command-ownership)
  - [Validation capabilities](#validation-capabilities)
  - [Review and snapshot capabilities](#review-and-snapshot-capabilities)
  - [Dependency capabilities](#dependency-capabilities)
  - [Source delivery boundary](#source-delivery-boundary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Command Ownership

Commands resolve through the consumer profile: owner, cwd, argv, scope, prerequisites and effects
are specified per capability. Verify owning source before invocation. Do not treat a generic target
name as proof it exists, execute shell text from a profile, install missing tools through a check,
or bypass a missing/denied command. Implement a missing binding only within authorized scope;
otherwise mark its dependent check blocked. Read-only discovery does not require application tools.

## Validation capabilities

Bind Markdown format and non-mutating Markdown check separately. Select only task-owned files.
Bind language setup, runtime verification, formatting, lint, unit/fast, integration, generation,
compatibility, dependency/security and acceptance checks to their actual owners. Setup and mutations
remain separate from normal checks. A consumer may select Make for Go/Python and Maven or a script
for Java; no shared rule mandates another consumer's command paths, pins or build system.

## Review and snapshot capabilities

The `snapshot` binding takes consumer root, intended base, head and output path. Verify refs and
merge base before replacing the output; preserve prior evidence if resolution fails. Record full
base/head/merge-base SHAs and `git diff <base>...<head>`. Its committed patch excludes dirty work;
inspect staged/unstaged/untracked inputs separately. Verify artifact ownership before calling.

The optional `review-upstream` binding verifies the current branch against its configured upstream
only when strict synchronization is requested. Fetch effects and deadlines must be explicit;
absent upstream, failure or unequal commits stop that mode without replacing evidence. This is
not the submodule freshness check and not authoritative published PR identity.

The `published-pr` binding takes consumer root, verified base/head remotes, fetchable refs and
host-reported full SHAs. Fetch with bounded waits, require exact fetched equality, recheck moving
metadata, then snapshot the verified revisions. Missing metadata or failure blocks that mode;
never fall back to local HEAD. Record Git metadata effects separately from application writes.

## Dependency capabilities

Preparation checks out the recorded gitlink, never latest implicitly. Offline integrity requires
clean initialized material and HEAD equal to the selected index pin; report differences from the
committed pin. Explicit commit mode uses that commit and never falls back to the index. Reject
missing/unmerged gitlinks, dirty material, missing files and inconsistent source overrides.
Online freshness additionally queries the exact configured upstream ref with a bounded deadline
and requires exact equality, including detached/shallow consumers. Drift, rewrites, ahead/diverged
pins, missing ref, timeout or denied access are nonzero; no cached-ref success or auto-repair.
Checks preserve consumer/submodule files, indexes, refs and pins; disclose scratch requirements.
Explicit upgrade/rollback uses matching dependency/profile/adapter combinations and preserves
unrelated edits and older artifacts. Do not force a clean tree to make a check pass.

## Source delivery boundary

This source stage defines guidance, catalogs and examples. Portable implementations of snapshot,
review identity, source/integrity/freshness/composition, Markdown tooling and the framework Make
interface are delivered in the helper step. Their absence is blocked executable validation, not
a successful check. No copied consumer toolchain path is a framework runtime dependency.
The accepted initial helper runtime/tool pins belong in framework-owned setup and lockfiles when
those are implemented; guidance loading itself requires no Python, JVM or Go runtime.
