<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Java API and Transport](#java-api-and-transport)
  - [Contracts and mapping](#contracts-and-mapping)
  - [Validation and errors](#validation-and-errors)
  - [Authorization and evidence](#authorization-and-evidence)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Java API and Transport

## Contracts and mapping

Identify the source schema, generator configuration, output directories and dependent modules.
Edit the authoritative contract or generator inputs, never generated DTOs/delegates directly.
Reproduce clean generation, compare with an independent baseline and compile affected consumers.
Normalize only documented nondeterministic metadata, never semantic fields to make a diff pass.
Keep generator/runtime/plugin versions in the consumer.

Preserve request/response fields, status, headers, absence, date/time and serialization semantics.
Distinguish calendar dates from instants/timezones; specify inclusive/exclusive ranges and capture
one reference time in boundary tests. Do not use a Period day component as a generic elapsed-day
calculation. Explicitly check path/body identifier consistency against the existing contract;
a discovered discrepancy is a scoped decision, not permission for an incidental API fix.

## Validation and errors

Trace transport parsing, bean validation, service invariants and persistence failures separately.
Preserve HTTP status and error-body shape/messages where contractual, including empty versus
missing collections and bounded timestamps. Check representative success, invalid input,
not-found and conflict cases against saved requests/fixtures. A body status assertion alone does
not verify the HTTP status. Catch-all success or an exception stack trace in a response is invalid.
Report discrepancies between schema and actual handlers without silently adopting either as a fix.

## Authorization and evidence

Identify the applicable authentication/authorization owner for the operation. Missing evidence
is a gap; absence of security code is not approval for public access. Keep personal data, tokens
and internal diagnostics out of responses/logs; use synthetic values in tests. Preserve existing
security behavior unless the specification changes it.

The [B01–B06 baseline](../../provenance/java.md#independent-behavior-baseline) documents campsite
expectations and discrepancies, including the unverified malformed-GET-UUID response. It is
consumer provenance, not a universal endpoint design. Real API/database/generation checks remain
consumer-owned; shared static checks do not certify those outcomes.
