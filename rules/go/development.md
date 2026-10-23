<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Go Development](#go-development)
  - [Scope and Makefile interface](#scope-and-makefile-interface)
  - [Service structure and dependencies](#service-structure-and-dependencies)
  - [Implementation and lifecycle](#implementation-and-lifecycle)
  - [Contracts and persistence](#contracts-and-persistence)
  - [Migration and operations](#migration-and-operations)
  - [Tests](#tests)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Go Development

Apply to handwritten Go services and their contracts, persistence, and runtime configuration.
Use [Go rules](README.md) to select the other policies for the affected boundary.
Before planning or editing, discover and read the service-local `AGENTS.md` files applicable to
each affected path, following the scope, precedence, and conflict procedure in
[the root guide](../../consumer.md). Local Go conventions may add scoped detail; they do not silently
override canonical repository requirements. Stop and surface conflicts for resolution.

## Scope and Makefile interface

- Identify services, packages, manifests/workspace, nested guides, build owners, tool configuration,
  CI gates and affected contract consumers before editing.
- Invoke the profile's owning commands for setup, dependencies, formatting, lint, tests, builds,
  run, generation, migrations, containers and deployment. When Make is the selected owner, all
  such operations use its targets, including editor/CI paths; no direct-tool bypass.
- Inspect recipes, prerequisites, cwd, supported selection variables and side effects. A root
  aggregate does not prove nested-module coverage. Read-only file/Git discovery remains allowed.
- If a required binding is missing, implement the smallest owning interface only within scope,
  otherwise report the blocked capability. Never invent targets or silently substitute tools.
- Keep versions, flags, exclusions, module selection and tool order in owning configuration.
  Apply [Make conventions](../makefile-rules.md) to affected Make boundaries. Derive versions and import
  prefixes from actual manifests; keep CI/container builds consistent without unrelated upgrades.

## Service structure and dependencies

Follow [Go architecture](architecture.md) for business-oriented organization, inward dependencies,
consumer-owned ports, adapter mappings, explicit composition, resource ownership, and architecture
handoff. Local package responsibilities and source references remain in the consumer guide.

Prefer standard-library facilities and established module libraries. New dependencies need a
concrete purpose and validation path. Maintain dependencies only through the declared command owner,
only in affected modules, and review both `go.mod` and `go.sum` changes.

## Implementation and lifecycle

- Pass `context.Context` first for blocking/I/O operations and propagate it through handlers,
  repositories, and clients. Honor cancellation and deadlines; do not replace request contexts
  with background contexts or store them in business objects.
- Handle meaningful errors; add concise operation context, preserve inspectable causes with `%w`,
  and match wrapped errors with `errors.Is`/`errors.As`. Keep error strings lowercase without final
  punctuation except proper names/acronyms. Do not panic or exit for expected business failures.
- Give every goroutine an owner, cancellation path, and bounded shutdown. Synchronize shared state;
  avoid mutable package globals. Release resources on partial startup failures as well as shutdown.
- Handle termination signals, stop accepting work, drain in-flight work within a deadline, and
  close clients, pools, and telemetry exporters. Cleanup needs a usable bounded context, not an
  already-cancelled request context. Preserve the original failure when cleanup also fails.
- Keep retries bounded and cancellation-aware, and only retry operations known to be safe. Preserve
  idempotency for writes; do not stack application and infrastructure retries blindly.

## Contracts and persistence

Follow [Go API and transport](api-transport.md) for versioned protobuf contracts, HTTP facade
design, OpenAPI ownership, validation, wire/error mappings, security, and compatibility. Keep the
ticket's accepted contract and migration behavior authoritative at each transport boundary.

- Never edit generated files manually. Change definitions or interfaces, then invoke the owning
  generation commands for generation and checks. Pin generator versions in repository tooling.
- Keep database details behind repository ports. Preserve the selected driver/ORM and migration
  owner; a reference implementation is not permission to change the persistence stack. Record
  any agreed departure in the specification.
- Make transaction boundaries, isolation, concurrency/version checks, and conflict behavior explicit.
  Use parameterized queries or safe ORM bindings, honor contexts, and handle commit/rollback,
  resource cleanup, and row-iteration errors. Test database-enforced behavior against the actual adopted database in a disposable environment.
- Use versioned migrations and preserve compatibility while old and new services coexist. Do not assume
  application startup may migrate production schemas just because the example does so. The ticket
  must define migration ownership, execution, and rollback/forward-recovery behavior.

## Migration and operations

- Before rewriting, capture existing DTOs, validation/errors, permissions, events, persistence,
  date/time and monetary behavior from authoritative code/contracts. Record parity and explicitly
  agreed differences before building the replacement.
- Keep migration slices independently deployable beside the existing service, with internal
  verification and rollback. Traffic changes, authentication/mesh changes and retirement are
  separate specified actions; never assume another migration phase is complete.
- Preserve specified storage, expressions, search, messaging and document semantics. A scaffold
  does not establish business parity.
- Parse environment configuration into typed startup settings and fail clearly on missing values.
  Use managed secrets; never promote local credentials/defaults into production.
- Use the adopted structured logging and telemetry stack with service identity, trace propagation,
  safe fields and bounded metric cardinality. Collector pipelines and backend endpoints stay local.
  Never copy full payload/result logging or disclose credentials/customer/payment data.
- Provide meaningful readiness/liveness, bounded client/server timeouts and documented exposure
  controls for debug profiling and reflection.

## Tests

Follow [Go testing](test.md) for naming, test structure, assertions, isolation, and integration
boundaries. Use the [Go testing examples](../../examples/go-testing/README.md) for concrete patterns
adapted to the ticket and actual module APIs, and [Go validation](validation.md) for required
owner-bound checks and evidence.
