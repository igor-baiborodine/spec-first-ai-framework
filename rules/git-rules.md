<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Git Rules](#git-rules)
  - [Branch Names](#branch-names)
  - [Commit Messages](#commit-messages)
  - [Pull Request Titles](#pull-request-titles)
  - [Authorized Pull Request Merge](#authorized-pull-request-merge)
  - [Commit Content and Staged Review](#commit-content-and-staged-review)
  - [Working Tree and History Safety](#working-tree-and-history-safety)
  - [Sensitive and Generated Content](#sensitive-and-generated-content)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Git Rules

Naming and style choices in this document are supported house conventions, applied only when
selected by the consumer profile. Worktree preservation, explicit authorization, safe invocation
and truthful validation remain mandatory. Preserve the consumer's existing public interfaces.


Apply these rules when creating or renaming a branch, preparing or reviewing a commit, or managing
the Git working tree or history. They implement the repository's use of the
[Conventional Commits specification](https://www.conventionalcommits.org/en/v1.0.0/).

## Branch Names

Choose one of these types according to the branch's primary purpose:

- `feat`: a new feature
- `fix`: a bug fix
- `docs`: documentation-only changes
- `style`: formatting or other changes that do not affect behavior
- `refactor`: a code change that neither fixes a bug nor adds a feature
- `perf`: a performance improvement
- `test`: additions or corrections to tests
- `chore`: build, tooling, dependency, or other maintenance work

Use one of these formats:

```text
<type>/issue-<number>-<description>
<type>/issue-<number>-<description>-<pr-number>
<type>/<description>
```

- Include the issue prefix when the branch corresponds to a ticket. The prefix is optional for
  work without a ticket.
- Write the description with lowercase ASCII letters, digits, and hyphens. Do not use spaces,
  underscores, or uppercase letters.
- Keep the description concise and specific, preferably about five words or fewer.
- When a ticket is delivered through multiple PRs, suffix each PR branch with its planned PR
  number from the delivery plan (`-1` for `PR1`, `-2` for `PR2`, and so on). Use the unsuffixed
  ticket format for a single-PR ticket. The suffix identifies the PR's position in the ticket
  plan, not the hosting platform's global pull request number.
- Give each branch one purpose. Use the type that best represents its primary outcome; supporting
  commits may use other accurate commit types.

Examples:

- `feat/issue-6-provision-kind-and-microk8s-clusters`
- `feat/issue-174-move-auxiliary-tooling-to-python-7` (`PR7` of a multi-PR ticket)
- `fix/issue-14-handle-null-pointer-in-payment-service`
- `docs/issue-22-update-api-specification`
- `feat/add-basic-authentication`
- `refactor/cleanup-database-migrations`
- `chore/update-dependencies`

Consumer-owned hooks may enforce the adopted naming rules; verify their actual configuration
before claiming enforcement.

## Commit Messages

Use the applicable form:

```text
<type>: [issue-123] <description>
<type>(<scope>): [issue-123] <description>
<type>!: [issue-123] <description>
<type>(<scope>)!: [issue-123] <description>
```

When the commit corresponds to a specific delivery step, use:

```text
<type>: [issue-123][step-4] <description>
<type>(<scope>): [issue-123][step-4] <description>
<type>!: [issue-123][step-4] <description>
<type>(<scope>)!: [issue-123][step-4] <description>
```

- Use one of the eight branch types listed above as the lowercase commit type.
- Use an optional lowercase scope in parentheses when it adds useful subsystem context, such as
  `ai`, `ci`, or `k8s`.
- Include the lowercase issue reference when the commit relates to a ticket. The square brackets
  are literal, as in `[issue-123]`. Omit the entire reference when there is no ticket.
- Append the lowercase delivery-step reference immediately after the issue reference when the
  commit corresponds to one step in the delivery plan. Use the step identifier without a leading
  zero in its numeric portion, as in `[issue-123][step-4]` or `[issue-123][step-7A]`, even though
  artifact filenames use `step-04` or `step-07A`. Preserve the uppercase suffix assigned to an
  inserted step.
  Omit the step reference when the commit does not correspond to one specific delivery step.
- Write a concise description in imperative mood, such as `add logging support`.
- Use lowercase prose and omit the final period. Preserve the correct case of names and identifiers
  such as `README`, `Go`, and API symbols.
- For a breaking change, place `!` immediately before the colon, after the optional scope: `type!:`
  or `type(scope)!:`. Explain the affected interface and required migration in the commit body or a
  `BREAKING CHANGE:` footer.

Examples:

- `feat: [issue-12] add new user login endpoint`
- `feat: [issue-3][step-4] implement release calculation and squash validation`
- `fix(ci): [issue-3][step-7A] restore release validation dependency`
- `fix: handle null pointer on empty request`
- `docs(ai): [issue-174] update repository rules`
- `chore: update dependencies to latest versions`
- `refactor(auth): [issue-6] simplify authentication flow`
- `feat(api)!: [issue-42] replace the legacy authentication contract`

Verify the adopted convention against the consumer's actual hook configuration.
Do not claim a hook is installed or enforcing policy without evidence.

The bracketed subject reference provides traceability but does not declare that the commit closes
the issue. Use a hosting-platform closing reference only when the delivered change satisfies the
issue's completion criteria.

## Pull Request Titles

When authorized to create a pull request, derive its title from the complete planned pull request,
including all of its delivery steps and commits. Use:

```text
<type>: [issue-123] <whole-PR purpose> - PR1
<type>(<scope>): [issue-123] <whole-PR purpose> - PR2
<type>!: [issue-123] <whole-PR purpose> - PR3
<type>(<scope>)!: [issue-123] <whole-PR purpose> - PR4
```

For ad hoc work, omit `[issue-123] ` entirely. Use one of the supported commit types and the same
optional scope and breaking marker rules as commit subjects. `PR<n>` is the planned sequence in the
delivery plan, starting at `PR1` even for a single pull request; it is not the hosting platform's
global pull request number.

The purpose must summarize the outcome of the entire pull request. Do not include a `[step-*]`
reference or summarize only the final commit. Recheck the title after pull request creation and
before merge because an edited title changes the required squash commit message.

Examples:

- `chore(policy-search): [issue-235] quiesce Java consumers - PR4`
- `feat(ai): [issue-10] standardize release identities and PR lifecycle - PR1`
- `fix!: replace an ad hoc compatibility contract - PR1`

## Authorized Pull Request Merge

Merge permission is action-specific. It does not authorize a release, history rewrite, successor
merge, branch deletion or another pull request. Before using valid merge permission on GitHub:

1. Resolve the pull request's current base and head from GitHub and fetch those exact revisions.
2. Produce a formal local review of that published base/head using the canonical
   [code-review workflow](../skills/code-review/SKILL.md) and its required ticket artifact name.
   Record the specification identity, coverage, validation limits and every finding with a stable
   ID and severity.
3. If the review contains any finding, including low/nit, stop until a maintainer records a
   disposition for every finding. An agent fix or earlier merge permission does not clear the
   finding. Refresh the published-revision review after relevant fixes or any base, head or
   specification change. A missing or stale formal review blocks merge. A current review with no
   findings uses the existing merge permission without asking for it again.
4. Verify required checks, review gates, current title, exact reviewed base/head, and that squash
   merge is enabled. If squash is unavailable, stop; do not substitute merge or rebase.
   If a merge queue or branch rule can defer or alter the operation so the exact squash method and
   message cannot be guaranteed, stop instead of enabling auto-merge or enqueueing the PR.

Before merging, derive the final message from the same current pull request revision used by the
review. Construct the subject by appending the hosting platform's global pull request number to the
exact current title:

```text
<exact-current-title> (#<pull-request-number>)
```

The title's `PR<n>` remains the planned sequence within the ticket; `#<pull-request-number>` is the
GitHub pull request identity and provides the link back to that pull request. Construct a non-empty
body from the current source commits in their pull request order. Use one `* <commit-subject>` entry
per commit, separated by a blank line, and do not copy source commit bodies or trailers.

Perform a squash merge while explicitly supplying both constructed values. For `gh`, use the
equivalent of:

```sh
gh pr merge <number> --squash \
  --subject "<exact-current-title> (#<number>)" \
  --body "<generated-commit-list>"
```

Do not depend on repository defaults to construct either field. After GitHub confirms success, read
the pull request state, squash commit SHA and complete commit message from GitHub/the target branch.
The subject must equal the exact current title plus ` (#<number>)`, and the body must equal the
generated commit list byte for byte. A missing, reordered, added or altered entry is a failed
postcondition. Report any mismatch; do not rewrite shared history to hide it.

For stacked pull requests, identify the immediate open successor from the delivery plan and actual
base/head relationships. Only after the parent merge is confirmed, retarget that successor to
`main`. Read back its base, then inspect its changed-file diff and check state to ensure the merged
parent's patch is absent and the successor still represents its planned scope. A failed parent merge
must not trigger retargeting. A failed retarget, wrong base, duplicated parent diff or unavailable
verification leaves the handoff incomplete. When no immediate successor exists, record that fact.
Retargeting does not authorize merging the successor or rewriting its branch.

## Commit Content and Staged Review

- Make each commit one coherent, reviewable change. Keep its implementation, directly associated
  tests, and necessary documentation together.
- Separate unrelated refactoring, broad formatting, and generated-file churn. Do not split a
  contract change from the callers required to keep the affected component working.
- Prefer commits that leave the affected component usable and its applicable checks passing. If an
  intermediate commit intentionally cannot stand alone, explain why and record the intended merge
  strategy in the commit body or delivery documentation.
- Before committing, inspect `git status --short`, `git diff --staged --stat`,
  `git diff --staged`, and `git diff --staged --check`. Review new files, deletions, file modes,
  generated output, and unintended changes as well as the patch content. These checks supplement
  rather than replace the owning module's tests and validation.
- Stage explicit paths or selected hunks when unrelated work is present. Do not include unrelated
  working-tree changes merely because they are available to stage.

## Working Tree and History Safety

- Inspect repository status before editing. Preserve pre-existing staged, unstaged, and untracked
  work. Do not discard, overwrite, stash, unstage, or incorporate unrelated changes without
  explicit authorization.
- Do not use destructive cleanup or recovery commands merely to obtain a clean working tree. Report
  conflicting changes and resolve their ownership before continuing.
- Commit authorization does not authorize a push, merge, branch deletion, release tag, or shared
  history rewrite. Explicit session-start permission to commit and/or push applies only to the
  named operation and scope during that session; it does not carry into another session. Follow
  the review and authorization conditions in [`AGENTS.md`](../consumer.md).
- Do not rename an existing branch or rewrite commit history merely to apply this rule
  retroactively. Perform those operations only when the task explicitly requires them.
- Naming compliance does not authorize creating a commit. Follow the review and commit
  authorization requirements in [`AGENTS.md`](../consumer.md).

## Sensitive and Generated Content

- Never commit credentials, private keys, tokens, or unsanitized sensitive data. Keep secrets out
  of commit subjects, bodies, and recorded diffs, including when documenting their removal.
- Keep developer-specific configuration, local environments, database dumps, disposable test
  output, and local AI artifacts untracked unless an owning workflow explicitly requires a safe,
  sanitized form. Files under `<artifact-root>/` must remain untracked.
- Commit generated files only when the owning workflow or repository contract requires them. Review
  generated changes for unexpected content before staging them.
