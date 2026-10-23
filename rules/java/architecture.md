<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Java Architecture](#java-architecture)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Java Architecture

Preserve the consumer's module/package ownership and dependency direction. Contract modules own
schemas/generated DTOs; application services own use cases; persistence adapters own storage
translation. Verify affected dependents when a contract changes. Do not import storage/framework
implementation details into a shared contract for convenience.

Make dependencies explicit through the selected composition mechanism. Constructor composition
is the campsite example; Spring beans, MapStruct, Lombok and JPA are scoped stack choices, not
mandatory dependencies for other Java consumers. Micronaut or other existing mechanisms retain
their local conventions. Introduce interfaces/layers only for a concrete substitution or boundary,
not to reproduce the example's package tree.

Keep transport DTO, domain model and entity mapping deliberate. Verify contractual fields, absence,
identity and version behavior independently; automatic mapping is not proof of compatibility.
Place transaction ownership where the business operation and storage guarantees can be reasoned
about together. Identify proxy crossings and avoid assuming private/self-calls receive advice.

Review the dependency graph and compile affected contracts plus consumers. Use the
[API rules](api-transport.md) for generation/mapping changes and the
[source inventory](../../provenance/java.md#coverage-inventory) for the API/service example.
No architectural rewrite is implied by adoption.
