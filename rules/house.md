<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Selected House Conventions](#selected-house-conventions)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Selected House Conventions

Load this component only when the consumer profile selects it. Read the local guide to identify
which conventions are adopted, then the applicable [Git](git-rules.md), [naming](naming-rules.md)
and [Make](makefile-rules.md) documents. Make conventions apply only to Make boundaries; they do
not require every language to use Make. These are supported defaults, not universal mandates.

The default Go style uses gofumpt, goimports and golines with a 100-column readability target;
the consumer owns compatible pins, ordering, prefixes and exclusions. The default Python style
uses pinned Ruff with E4/E7/E9/F/I/UP/B and a 100-column limit; the target Python release comes from
the consumer's declared runtime. Test naming and Given/When/Then markers in language rules are
selected house conventions. Discovery, isolation, independent assertions and security safeguards
are mandatory regardless of style selection. Preserve established conventions when not selected;
do not normalize unrelated source or rename tests incidentally.

Java style is a separate explicit consumer choice; selecting house guidance never automatically
applies Google Java Style. A consumer with legacy Java may retain its existing style for existing,
modified and new files while another selects Google Style. Language availability and formatting
selection are independent. The complete Java rules and provenance are delivered separately.
