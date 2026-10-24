<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Nice-to-have Ledger](#nice-to-have-ledger)
  - [Deferred items](#deferred-items)
    - [issue-3-N01: Cumulative changelog](#issue-3-n01-cumulative-changelog)
    - [issue-3-N02: Consumer upgrade pull requests](#issue-3-n02-consumer-upgrade-pull-requests)
    - [issue-3-N03: Partial-release recovery](#issue-3-n03-partial-release-recovery)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Nice-to-have Ledger

This ledger retains independently deferrable improvements for the framework. An entry is not a
delivery commitment. Selecting one requires explicit scope and acceptance criteria in a receiving
ticket; existing integrity and security requirements remain mandatory.

IDs combine the originating issue with its stable requirement ID. Keep those IDs when an item is
selected, completed, or superseded, and record the receiving issue and evidence here.

## Deferred items

| ID | Improvement | Origin | Status |
| --- | --- | --- | --- |
| [issue-3-N01](#issue-3-n01-cumulative-changelog) | Committed cumulative changelog | [Issue #3](https://github.com/igor-baiborodine/spec-first-ai-framework/issues/3), N01 | Deferred |
| [issue-3-N02](#issue-3-n02-consumer-upgrade-pull-requests) | Automated consumer upgrade pull requests | [Issue #3](https://github.com/igor-baiborodine/spec-first-ai-framework/issues/3), N02 | Deferred |
| [issue-3-N03](#issue-3-n03-partial-release-recovery) | Automatic partial-release recovery | [Issue #3](https://github.com/igor-baiborodine/spec-first-ai-framework/issues/3), N03 | Deferred |

### issue-3-N01: Cumulative changelog

- **Source:** Issue #3 requirements assessment N01; retained as optional in the published issue's
  deferred nice-to-haves. Added to this ledger at the maintainer's request on 2026-10-24.
- **Proposed outcome:** Maintain a committed cumulative changelog alongside GitHub release notes.
- **Why deferred:** Release notes satisfy the current release outcome. Automatic changelog commits
  add write permissions, source changes, and workflow-recursion complexity.
- **Reconsider when:** Consumers need an offline release history.
- **Acceptance evidence if selected:** Changelog entries match the actual release versions and
  commit ranges. Generating an entry creates no unintended extra release or unrelated source change.
- **Disposition:** Deferred; no receiving implementation ticket or delivery commitment assigned.

### issue-3-N02: Consumer upgrade pull requests

- **Source:** Issue #3 requirements assessment N02; retained as optional in the published issue's
  deferred nice-to-haves. Added to this ledger at the maintainer's request on 2026-10-24.
- **Proposed outcome:** Open consumer upgrade PRs for reviewed framework releases, updating the
  gitlink and matching profile, adapters, or guides where required.
- **Why deferred:** Issue #3 covers guidance and deterministic pins, not changes across consumer
  repositories. Each consumer owns its configuration, checks, and publication authority.
- **Reconsider when:** Release frequency makes manual upgrades costly.
- **Acceptance evidence if selected:** A PR changes only the reviewed framework integration,
  identifies the selected release and SHA, and runs the receiving consumer's checks. Unrelated
  consumer work remains intact; no automatic merge is implied.
- **Disposition:** Deferred; scope and authorization for each receiving repository remain future work.

### issue-3-N03: Partial-release recovery

- **Source:** Issue #3 requirements assessment N03, moved from mandatory M05/Q03a by explicit
  maintainer decision. Added to this ledger at the maintainer's request on 2026-10-24.
- **Proposed outcome:** Automatically resume publication when the intended source tag exists but
  its GitHub Release is missing.
- **Why deferred:** The maintainer classified automatic recovery as nice-to-have. Issue #3 must
  still report the partial state, stop safely, and prevent duplicate or conflicting publication.
- **Reconsider when:** Partial failures or the cost of manual intervention justify automation.
- **Acceptance evidence if selected:** A rerun verifies the existing tag and SHA, reconstructs the
  intended release range and notes, and completes that same release without another version bump,
  duplicate release, or tag rewrite. A conflicting tag fails safely.
- **Disposition:** Deferred; excluded from issue #3's mandatory delivery and tool-selection gates.
