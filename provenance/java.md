<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Java Derivation](#java-derivation)
  - [Source and scope](#source-and-scope)
  - [Coverage inventory](#coverage-inventory)
  - [Independent behavior baseline](#independent-behavior-baseline)
    - [B01 successful read](#b01-successful-read)
    - [B02 creation and availability](#b02-creation-and-availability)
    - [B03 invalid duration](#b03-invalid-duration)
    - [B04 overlapping bookings](#b04-overlapping-bookings)
    - [B05 missing and malformed input](#b05-missing-and-malformed-input)
    - [B06 optimistic compatibility](#b06-optimistic-compatibility)
  - [Deviations and gaps](#deviations-and-gaps)
  - [Rights and notices](#rights-and-notices)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Java Derivation

## Source and scope

Observed source: [campsite-booking](https://github.com/igor-baiborodine/campsite-booking/tree/c3f83a1b69304299ee5fafd5dc0d7a02e0d35ae4),
revision `c3f83a1b69304299ee5fafd5dc0d7a02e0d35ae4`. In the inventory, `S/` means
`campsite-booking-service/src/main/java/com/kiroule/campsitebooking/` and `T/` is the corresponding
`src/test/java/com/kiroule/campsitebooking/` tree. These are historical evidence paths, not required
consumer topology. Shared rules are newly written guidance; application sources are not vendored.

The author's [Revisited 3 article](https://www.kiroule.com/article/campsite-booking-api-revisited-3/)
(17 November 2023) explains the API-first/module/mapping and test evolution. Source/configuration
at the revision above controls factual claims: its parent declares Spring Boot 3.1.5, while the
article describes 3.1.4. Neither version is a shared requirement. Google style is an explicit user
selection, with [the official guide](https://google.github.io/styleguide/javaguide.html) as authority;
existing code is not presumed compliant. The pilot tools/versions and measured results below are
historical evidence, not mandatory tooling for every consumer.

## Coverage inventory

Each row states observation, normative extraction, scope, gap and independent verification.
Rule filenames link to the corresponding complete guidance.

| Area and source anchor | Observation and extracted rule | Scope and gap | Verification |
| --- | --- | --- | --- |
| [Router](../rules/java/README.md); root/API/service POMs, S/controller/BookingApiControllerImpl.java, T/controller/BookingApiControllerTest.java | Separate Java implementation, architecture, API and test boundaries; route implementation to development/formatting/validation and add affected boundaries | Shared new router; none existed in campsite | J01 routing, API-plus-test union, Go-only independence |
| [Development](../rules/java/development.md); root POM, `.mvn/wrapper/maven-wrapper.properties` | Honor declared compiler/runtime/build/dependency owners | Shared principle; Java 17, Maven 3.9.9 trial versus wrapper 3.5.4, plugin pins are consumer-only | Consumer runtime gate; unsupported tool must fail |
| Development; S/service/BookingServiceImpl.java#findByUuidNotTransactional, S/mapper/BookingMapper.java, T/model/mapper/BookingMapperTest.java#given_null_booking_dto__then_null_returned | Optional lookup throws on absence; mapper preserves null; make each boundary's failure/absence explicit | Shared principle; MapStruct is selected stack; validators do not prove universal null safety | J02 swallowed exception; B03/B05 invalid inputs |
| Development; S/model/Booking.java#getBookingDatesWithEndDateExclusive, S/service/BookingServiceImpl.java#findVacantDates | Mutable models and locally built availability list; identify collection/state ownership | Shared principle; no requirement to keep fields mutable; additional aliasing/shared-state safeguard | J04 mutation/parallel isolation |
| Development; T/service/BookingServiceImplConcurrentIT.java, S/repository/context/MysqlCustomRepositoryContextImpl.java | Executor work and container-owned EntityManager have different owners | Resource closure, interruption and collected worker failures are additional safeguards; positive try-with-resources example not established | J03 failure-path leak; J05 worker exception/interruption |
| Development; S/service/BookingServiceImpl.java#createBooking/updateBooking/findByUuid, S/repository/CustomBookingRepositoryImpl.java#findForDateRangeWithPessimisticWriteLocking | Service transactions/retries, lock query and private nontransactional lookup | Shared transaction/proxy reasoning; Spring, REQUIRES_NEW and retry counts remain selected/local | B04/B06 real storage; J05 collected workers |
| [Architecture](../rules/java/architecture.md); root/API/service POMs, S/controller/BookingApiControllerImpl.java | Service depends on generated API and delegates use cases | Shared dependency/contract ownership; package tree and number of layers not imposed | Dependent compile and review reversed dependency |
| Architecture; S/config/AppConfig.java bean methods, S/mapper/BookingMapper.java#toBooking/toBookingEntity, S/repository/entity/BookingEntity.java | Explicit composition and DTO/model/entity mapping | Constructor composition/MapStruct/Lombok/JPA are selected stack conventions; mapper assertions sometimes ignore fields | B01/B06 independent field/version assertions |
| [API](../rules/java/api-transport.md); API POM and `campsite-booking-api/src/main/resources/campsite-booking-api.yaml` | Generated delegate/DTO output belongs to schema/configuration | Shared generation ownership; endpoints/options are local; output is under target | Two clean generations, declared timestamp normalization and compile; J06 |
| API; YAML Booking/ApiError, S/model/validator/BookingAllowedStartDateValidator.java#isValid and BookingMaximumStayValidator.java#isValid | LocalDate booking dates, generated error timestamps, separate validation constraints | Shared explicit null/date/range semantics; Period.getDays and repeated now calls are gaps, not generic guidance | B02/B03/B05 boundary inputs, recorded date D |
| API; S/exception/advice/ControllerExceptionHandler.java handlers, T/exception/advice/ControllerExceptionHandlerTest.java, controller#updateBooking | Dedicated status/body mapping | Shared compatibility rule; schema/body and path/body discrepancies below remain unresolved consumer facts | B01–B06, J06 HTTP plus body checks |
| API; controller/POMs, S/aspect/LoggingAspect.java, advice#handleMethodArgumentNotValid | No positive authorization example in inspected scope; arguments/validation target may be logged | Authorization and sensitive-data safeguards are explicit additions; no claim of secure public access | J07 synthetic authorization/logging review |
| [Testing](../rules/java/test.md); T/service/BookingServiceImplTest.java and T/controller/BookingApiControllerTest.java | Method nested groups, underscore scenarios, Given/When/Then, classUnderTest/result, AssertJ/Mockito | Selected campsite house conventions; preserve legacy consumers' local names; no blanket renaming | Manual comparison and J08 discovery |
| Testing; T/TestDataHelper.java, T/BaseIT.java, concurrent IT and service POM | Easy Random, Testcontainers/MySQL, parallel execution | Selected tools; deterministic fixtures, collected worker failures and isolation require added safeguards | J04/J05, B04 persisted state; actual disposable integration |
| [Formatting](../rules/java/formatting.md); controller imports, source corpus and selected Google guide | Two-space baseline with measured drift and wildcard imports | Explicit Google selection for campsite; Insurance Hub excluded throughout legacy Java | J09 misformat/import/idempotence; retain deviations below |
| [Validation](../rules/java/validation.md); parent/service POMs, service resources/db migrations, `.github/workflows/pull-request.yml` | Surefire/Failsafe phases, coverage and hosted analysis inputs | Shared complete lifecycle/failure propagation; versions, DBs and thresholds local; hosted scanning does not prove portable local validation | J08 failing unit/IT and discovery; J10 static/dependency failures |

## Independent behavior baseline

These are expectations from the pre-adoption source, YAML, requirements and assertions. They are
not new shared API contracts or claims of final runtime acceptance. Use synthetic data, unique
campsites and one recorded reference date D; retain source/fixture identities and actual outcomes.

### B01 successful read

YAML GET `/booking/{uuid}` and T/controller/BookingApiControllerIT.java#GetBooking.happy_path:
HTTP 200; UUID, version, campsiteId, email, fullName, dates and active match the saved entity.
Expected fields come from recorded fixture inputs, not regenerated candidate responses.

### B02 creation and availability

Controller#addBooking, YAML POST and GetVacantDates.happy_path: valid creation returns 201 with
Location containing its UUID and retains supplied fields in an active row. Availability includes
the requested end date; occupied nights exclude checkout day. Capture responses before adoption.

### B03 invalid duration

AddBooking.given_booking_duration_exceeds_maximum_stay__then_status_bad_request and
BookingMaximumStay: D+1 to D+5 expects HTTP/body 400, message
`createBooking.booking: Booking stay length must be less or equal to three days`, empty subErrors.
Set UUID/version null and active true to isolate duration. Existing body-only assertions need an
additional HTTP assertion, not an inferred transport pass.

### B04 overlapping bookings

Controller AddBooking conflict case and service#validateVacantDates: identical occupied interval
expects HTTP/body 400 with `No vacant dates available from <start> to <end>`. Three concurrent
creates for the same campsite/interval must leave exactly one stored booking matching one input.
The pre-existing concurrent assertion supplies the invariant, but its execute/awaitTermination
harness lacks a coordinated start, collected futures and finally cleanup. Use a stronger owned
fixture; do not claim that source alone proves correct failure propagation.

### B05 missing and malformed input

GET missing UUID expects 404. Advice#handleHttpMessageNotReadable expects HTTP/body 400,
`Malformed JSON request`, empty subErrors. Request validation expects 400, `Validation error`
and constraint subErrors. Check runtime timestamp shape/bounds. Malformed GET UUID response was
not independently established; do not silently assign it an expected status from another handler.

### B06 optimistic compatibility

Update stale-version IT and advice#handleStaleObjectStateException expect 409 with
`Optimistic locking error: <entity> with id <id> was updated by another transaction`.
The existing successful-update fixture reaches version 1. Identity/version expectations remain
consumer-owned and must be compared against the preserved fixture.

## Deviations and gaps

The 54-file handwritten corpus at the source revision was checked with Google Java Format 1.24.0
in Google mode and Checkstyle 10.21.4 AvoidStarImport. Fifteen files failed format; sixteen wildcard
imports occurred in eleven files. Formatter success alone did not remove stars or prove full style.

| Finding | Source-relative files |
| --- | --- |
| Six main format deviations | S/mapper/CampsiteMapper.java; model/Booking.java; repository/BookingRepository.java; repository/CustomBookingRepositoryImpl.java; service/BookingService.java; service/BookingServiceImpl.java |
| Nine test format deviations | T/controller/BookingApiControllerIT.java; controller/BookingApiControllerTest.java; model/mapper/BookingMapperTest.java; repository/BookingRepositoryIT.java; service/BookingServiceImplConcurrentIT.java; service/BookingServiceImplIT.java; service/BookingServiceImplTest.java; service/CampsiteServiceImplIT.java; service/CampsiteServiceImplTest.java |
| Six main star imports, one per file | S/controller/BookingApiControllerImpl.java; exception/advice/ControllerExceptionHandler.java; model/Booking.java; model/Campsite.java; repository/entity/BookingEntity.java; repository/entity/CampsiteEntity.java |
| Ten test star imports | T/controller/BookingApiControllerIT.java (1); controller/BookingApiControllerTest.java (3); exception/advice/ControllerExceptionHandlerTest.java (1); service/BookingServiceImplTest.java (3); service/CampsiteServiceImplTest.java (2) |

A completed prerequisite dependency scan observed 86 dependencies, 14 flagged dependencies and
89 unique advisories. This historical result is nonzero, not a current vulnerability inventory.
Campsite's maintainer owns separate cleanup of the measured style/dependency baseline. Deferral
permits framework inception, not security-risk acceptance or a whole-corpus pass. Preserve original
thresholds; task-owned new/modified handwritten Java must pass selected format/import gates.
New unexplained regressions and missing/incomplete tools/data remain blockers. Insurance Hub has
no Google-style cleanup obligation. No application correction is included in this extraction.

YAML error responses sometimes name Booking where advice returns ApiError. PUT does not reconcile
path and body UUID. Null validators, elapsed-date logic, repeated clock reads, random fixtures,
worker cleanup/failure visibility and logging of payloads are gaps, not endorsed practices.
Authorization behavior and malformed GET UUID require independent evidence before claims.

## Rights and notices

The inspected application symbols identify Igor Baiborodine as author; no LICENSE/NOTICE file
was present in the inspected campsite revision. This is not a claim that source was publicly
relicensed. The framework contains newly authored principles, factual symbol references and
synthetic review scenarios, without copied application implementations or article/style-guide
passages. External sources keep their own terms. The selected framework [MIT license](../LICENSE)
covers these contributions; it does not relicense the application, Google guide, JDK documentation
or downloaded tools. See [framework provenance](framework.md) for the release review boundary.
