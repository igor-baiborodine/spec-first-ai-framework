<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Java Review Scenarios](#java-review-scenarios)
  - [Failure and ownership cases](#failure-and-ownership-cases)
  - [Transport and discovery cases](#transport-and-discovery-cases)
  - [Routing and evidence cases](#routing-and-evidence-cases)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Java Review Scenarios

These deliberately defective synthetic fragments challenge the [Java rules](../../rules/java/README.md).
They are review fixtures, not compilable application examples or a static Java analyzer. Review the
trigger, expected finding and corrective criterion together; headings/text matches cannot prove
that an agent recognizes a defect. Record actual manual findings separately. Consumer tool/DB
trials run through the consumer's bindings on owned copies.

## Failure and ownership cases

| Case | Defective input and trigger | Independent expected finding and corrective criterion |
| --- | --- | --- |
| J02 swallowed failure | `try { repository.save(input); } catch (RuntimeException ignored) {} return success();` with save throwing | Reject normal success after failed persistence; propagate/translate with cause and assert failure plus no committed row |
| J03 leaked resource | `var in = Files.newInputStream(path); parse(in); in.close();` with parse throwing | Close owned stream on every path, e.g. try-with-resources; injected parse failure must still observe close. Do not extend this to closing an injected EntityManager |
| J04 unsafe shared state | Singleton `private final List<String> names = new ArrayList<>();` followed by `names.clear(); names.add(request.name()); return names;` for two requests | final protects the reference only; shared mutation and returned alias cross request ownership. Use operation-owned state/copies or a justified synchronized design; mutate one returned collection and verify another result/state stays independent |
| J05 lost worker failure | `executor.execute(() -> { throw new IllegalStateException(); }); executor.shutdown(); assertTrue(executor.awaitTermination(1, MINUTES));` | Termination can succeed while the worker failed; collect every future/outcome, assert expected failures, bound waits and finally clean resources. Catching InterruptedException then returning success also fails; propagate or restore status and abort |

## Transport and discovery cases

| Case | Defective input and trigger | Independent expected finding and corrective criterion |
| --- | --- | --- |
| J06 transport drift | Return HTTP 200 with an error body whose status is 400; test asserts only body status. Hand-edit generated DTO to make compilation pass | Reject status mismatch and generated edit; assert HTTP plus body against saved invalid request, repair owning schema/config only under scope and regenerate/compile dependents. Preserve documented baseline discrepancies rather than inventing an API fix |
| J07 missing authority and payload exposure | Infer endpoint is public because no annotation exists; log the whole request including synthetic email/token | Missing authorization evidence blocks that assumption; identify owner and test explicit allow/deny when applicable. Sensitive input must be absent from logs/errors; never add a real credential to the fixture |
| J08 missed tests | Rename `BookingServiceTest` outside runner includes; accept build success with zero tests. Run only `failsafe:integration-test` after seeding an assertion failure | Expected discovery manifest must detect the missing case; complete the verification lifecycle and require nonzero failure exit. Record actual unit/IT names/counts/skips; a green command alone is insufficient |
| J09 false style pass | One-line handwritten class and `import java.util.*;`; run format check or import check | Google-selected checks reject the appropriate drift without modifying input; explicit format reaches independent expected layout and is idempotent. Local-style consumers use their own owner, never an inferred Google gate |
| J10 incomplete validation | Static gate ignores an empty catch; dependency scanner uses incomplete data and reports no findings | Seeded defect must fail the selected rule; unavailable/incomplete scanner data blocks evidence, thresholds stay unchanged. Historical nonzero baseline remains a separate cleanup finding |

## Routing and evidence cases

J01 composes the actual catalog in disposable Git consumers: Java implementation must include
README/development/formatting/validation; API-plus-test adds both corresponding rules; architecture
adds its own rule. Go-only profiles omit Java without altering another Java consumer. Exercise
both `google` and `local` style outputs. Missing required commands or Java routes fail explicitly.
The framework's fast and integration tests automate these structural cases and preserve files/Git
metadata across checks. They do not execute the Java fragments above.

For J02–J10, manual semantic review is justified because the framework ships guidance and does
not own a Java compiler, application runtime or generic Java analyzer. Consumer adoption must
also provide real format/static/unit/IT/generation/API/database observations where specified.
Retain [B01–B06](../../provenance/java.md#independent-behavior-baseline), fixture identities and
known limitations; a prose review is not a replacement for those runtime gates.
