<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Go Formatting](#go-formatting)
  - [Policy](#policy)
  - [Verification](#verification)
  - [Tooling ownership](#tooling-ownership)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Go Formatting

Apply to changed handwritten Go code. Follow the declared command-owner interface in
[Go development](development.md#scope-and-makefile-interface).

## Policy

- When this house style is selected, formatting is mechanical and mandatory: `gofumpt` for Go layout, `goimports` for import
  insertion/removal/grouping, and `golines` with a **100-column target** for long constructs.
  Treat this as an automated readability target, not permission to distort APIs or literal data.
- Invoke only the declared formatting and format-check bindings. Do not run these
  tools directly, hand-sort imports, manually align fields, or substitute IDE-only formatting.
- The owning configuration must pin compatible versions and explicitly define tool order,
  the line target, import prefixes, and exclusions. Do not rely on whichever base formatter happens
  to be installed. Derive local import prefixes from real module paths.
- A standalone formatter pipeline is consistent with the example. A golangci-lint v2 formatter
  configuration is also acceptable when adopted by repository tooling, provided the owning targets
  enforce the same policy. Do not run competing pipelines or duplicate flags in agent instructions.
- Limit formatting to changed handwritten files within the affected modules. Exclude generated
  protobuf/gateway code, generated mocks, vendor/third-party code, fixtures, and unrelated services
  from incidental formatting. Format intentionally changed handwritten test helpers/tests normally.
  Generated outputs remain governed by their generator and generation checks.
- If an existing target formats too broadly or does not enforce this policy, improve its scope or
  configuration within the ticket, or report the tooling gap. Do not silently accept weaker
  formatting or include unrelated normalization in a functional change.

## Verification

- Run formatting before validation, review the resulting changes, then run the non-mutating
  format-check target. It must detect formatting differences in the selected files independently
  of unrelated or intentional working-tree changes, including newly created Go files.
- When introducing/changing the pipeline, verify idempotence: a second formatting run produces
  no further changes. Report formatter disagreement rather than repeatedly cycling tools.
- A Git cleanliness check after formatting can detect drift in a clean CI checkout, but is not a
  substitute for a format check in an edited working tree. Never stage, commit, reset, or stash
  user work simply to satisfy such a check.
- For changed protobuf definitions, use separate owning commands for protobuf formatting/linting and
  regeneration; Go formatting is not protobuf validation.

## Tooling ownership

The consumer profile selects formatting conventions, pins and owning commands. The defaults above
apply only when selected through [house conventions](../house.md). Without that selection, preserve
the actual module's style. Missing required formatting capability remains blocked. Installing a
tool or a clean Git diff is not proof the declared formatting pipeline ran.
