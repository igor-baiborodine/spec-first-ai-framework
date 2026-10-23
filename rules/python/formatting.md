<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Python Formatting](#python-formatting)
  - [Policy and scope](#policy-and-scope)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Python Formatting

Apply to changed handwritten Python, including approved changed tests and helpers.
Also load [development](development.md), [testing](test.md), and
[validation](validation.md). Formatting and linting are mandatory and distinct from
behavioral testing.

## Policy and scope

The Ruff/style selections below are supported house defaults applied only when adopted by the
consumer profile. Preserve the actual owner's conventions otherwise. Required formatting/lint
checks, narrow scope and honest results apply independently of the selected tool.

- Use a pinned Ruff formatter for layout and a pinned Ruff linter with selected rules
  `E4`, `E7`, `E9`, `F`, `I`, `UP`, and `B`. Use a **100-character line length** and
  the target matching the declared Python runtime. `I` owns import sorting; configure known first-party imports
  for each owner so local modules are grouped correctly. Owned configuration MUST declare these
  selections, exclusions and exact Ruff pin. The owning configuration and lockfile
  record direct/resolved dependencies and artifact hashes. Do not
  hand-sort imports or substitute an IDE-only formatter.
- Owning commands MUST apply the same configuration to explicitly selected changed
  handwritten files, including new untracked files and intentional test changes. Exclude
  generated/vendor/third-party code and data fixtures from incidental formatting. Do not sweep
  unrelated working-tree changes into selection. Repository-wide checks are appropriate only
  when the owner declares that scope and existing failures are accounted for.
- Run formatting first, review its diff, then run non-mutating format-check and lint. Format-check
  MUST compare selected content without relying on a clean `git diff`, staging, committing,
  resetting, or stashing. It MUST reject drift in new handwritten files in an edited checkout.
  Check idempotence when introducing or changing the pipeline.

Use owning commands and the declared environment's Ruff executable. A missing target, pin,
configuration, or tool is a blocked check; do not substitute an arbitrary executable on `PATH`.
Ruff success proves source conformance only. Record the exact file set and tool identity in
[validation evidence](validation.md#evidence-limits).


Bind format, format-check and lint separately with explicit changed-file selection, including
untracked files. A repository-wide mode requires an inspectable tracked/unignored-untracked
scope. Format alone mutates source; format-check and lint never repair or reset user files.
