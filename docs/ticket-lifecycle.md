<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Ticket Lifecycle](#ticket-lifecycle)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Ticket Lifecycle

Each skill stops at its own output. The next stage runs only when requested and may resume in a
later session from the saved artifact. All ticket artifacts share the resolved `<ticket-dir>`;
filenames below omit the `<ticket>-` prefix for readability. This diagram summarizes the
[canonical workflows](../consumer.md#workflow-catalog); it does not add requirements to them.

```mermaid
flowchart TD
    input["Product or technical input<br/>With or without explicit ACs"]
    assess["ticket-requirements-workflow<br/>Assess scope and classify requirements"]
    requirements["requirements.md<br/>Assessment complete; stop here"]
    ledger["Optional requirements<br/>Applicable ledger or local assessment"]
    readiness{"Recheck drafting readiness"}
    clarify["Resolve blocking questions<br/>Update requirements and evidence"]
    specification["ticket-specification-workflow<br/>ticket-content.md; stop here"]
    plan["ticket-implementation-workflow<br/>delivery-steps.md<br/>Plan-only requests stop here"]
    decision{"Prerequisite decision still open?"}
    resolve["Execute bounded decision step<br/>Update specification and recheck readiness"]
    implement["Execute next ready delivery step"]
    validate{"Step validation passes?"}
    fix["Fix or clarify within the authorized scope"]
    post["ticket-post-step-workflow<br/>Update tracker, evidence and branch snapshot"]
    more{"More delivery steps?"}
    verify["Check AC coverage and completion evidence<br/>Review and PR preparation when requested"]
    accepted{"All required outcomes and checks satisfied?"}
    remaining["Record blockers and resolve remaining work"]
    complete["Ticket work complete"]

    input --> assess --> requirements
    assess -. "Defer nice-to-haves" .-> ledger
    requirements -->|Drafting requested| readiness
    readiness -->|Blocked| clarify --> assess
    readiness -->|Ready or bounded decision work| specification
    specification -->|Planning requested| plan
    plan -->|Implementation requested| decision
    decision -->|Yes; dependent work stays blocked| resolve
    decision -->|No| implement
    resolve --> validate
    implement --> validate
    validate -->|No| fix --> decision
    validate -->|Yes| post --> more
    more -->|Yes| decision
    more -->|No| verify --> accepted
    accepted -->|No| remaining --> plan
    accepted -->|Yes| complete
```

Bounded decision work requires a safe investigation scope, responsible role, expected evidence,
acceptance condition, and blocked dependencies. Unresolved security or personal-data safeguards
cannot be treated as optional work. A scope or contract change returns to requirements and
specification reconciliation before dependent implementation resumes.

An existing implementation-ready ticket can enter at planning without a retrospective requirements
assessment. Review reports findings; authorized implementation resolves them. Completion requires
the ticket's applicable outcomes and evidence, including any required CI, manual, or operational
checks. Commits, pushes, publication, merge, and remote issue closure remain separately authorized
actions; this diagram does not trigger them.

For issue-based work, [GitHub ticket synchronization](../rules/spec-first-rules.md#github-ticket-synchronization)
also gates planning, implementation/resume, and completion. Every local specification edit
triggers preparation of a GitHub update with explicit permission; local review checks the match
without repairing drift. Ad hoc tickets are exempt.
