<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Release Identity Rules](#release-identity-rules)
  - [Identity Model](#identity-model)
  - [First-Party Build Version](#first-party-build-version)
  - [Cross-Surface Contract](#cross-surface-contract)
  - [Workflow and Evidence Contract](#workflow-and-evidence-contract)
  - [Independent Scenarios](#independent-scenarios)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Release Identity Rules

Apply this rule when work builds, publishes, deploys or verifies a release or container image, or
when runtime telemetry exposes the deployed version. Documentation-only and unrelated work does
not need release identity evidence.

## Identity Model

Keep these values distinct. One value cannot stand in for another merely because it contains a
Git fragment or appears in the same release record.

| Identity | Purpose and representation | Mutability | Producer | Verification source |
| --- | --- | --- | --- | --- |
| Release version | Human and compatibility version, normally semantic or vendor-defined, such as `v2.9.6` | A published release identifier is stable; its selection can change | Owning release process | Authoritative release metadata and its source revision |
| Full source revision | Verified lowercase full Git object ID for the source commit | Immutable within the verified object format and repository | Source checkout or release workflow | `git rev-parse --verify '<ref>^{commit}'` and repository provenance |
| First-party build version | `git-` plus the first 12 lowercase hexadecimal characters of the verified full source revision | Immutable for one verified source revision under this repository contract | Build workflow, after full-revision verification | Recalculate from the recorded full revision and compare every mapped surface |
| Image tag or reference | Registry repository plus a tag, such as `registry.example/app:git-a05ee4564097` | A tag is mutable unless the registry proves otherwise | Image publication workflow | Registry metadata; never use the tag alone as immutable-image evidence |
| Digest-qualified image identity | Registry repository plus the resolved content digest, such as `registry.example/app@sha256:<64 lowercase hex>` | Content-addressed and immutable for the resolved manifest | Registry after publication | Registry digest resolution or a signed provenance record tied to that digest |

A short Git value does not prove a full source revision. A mutable image tag does not prove the
deployed image digest. Record the tag/reference for discoverability and the digest-qualified image
identity for immutable deployment evidence.

## First-Party Build Version

Resolve and verify the full source commit before deriving the build version. For a SHA-1 repository,
the default commands are:

```sh
source_revision=$(git rev-parse --verify 'HEAD^{commit}')
build_version="git-${source_revision:0:12}"
```

Use an equivalent non-shell implementation when the owning build system requires it. The result
must match `^git-[0-9a-f]{12}$` and its suffix must equal the first 12 characters of the recorded
full revision. Uppercase hexadecimal, a different prefix or length, and a suffix from another
revision are invalid.

`git-000000000000` may remain in a checked-in template only as an explicit unresolved placeholder.
It must fail a release, deployment, runtime verification or acceptance claim. Replace it from a
verified source revision before build or deployment evidence is accepted.

## Cross-Surface Contract

For a first-party source-derived build, propagate the exact same build version to:

- OCI `org.opencontainers.image.version`;
- Kubernetes `app.kubernetes.io/version` labels on the application and affected workload objects;
- OpenTelemetry `service.version` in runtime resource attributes.

Set OCI `org.opencontainers.image.revision` to the full source revision. Record the resolved
registry digest separately and retain the digest-qualified image identity in deployment evidence.
Do not put the digest into a version field or present a version field as digest evidence.

OCI annotations, Kubernetes labels and OpenTelemetry semantic conventions permit values broader
than this repository's first-party convention. Semantic release versions and vendor versions are
valid for independently versioned or third-party components when the evidence names the component,
owner, version source and verification method. Such an exception does not change a first-party
source-derived build into a semantic or vendor build.

## Workflow and Evidence Contract

For an applicable ticket, state before implementation:

- which producer command or workflow verifies the full revision and derives each identity;
- every destination surface and how its value is populated;
- where image tag and registry digest evidence come from;
- how unresolved placeholders stop build, deployment or acceptance;
- any scoped semantic/vendor exception, including owner, component, reason and verification source.

Requirements and specifications define the expected mapping and failure cases. Delivery plans name
the producer, propagation and verification steps. Step summaries and pull request descriptions
record actual values or sanitized fixture identities plus the commands and sources that observed
them. Reviews compare those values and report missing or inconsistent evidence as findings.

Fail the applicable claim when the full revision is absent or unverified; build-version format or
derivation is wrong; mapped surfaces disagree; a placeholder reaches build, deployment or runtime
evidence; or the image evidence contains only a mutable tag. Preserve the original failed evidence
and its tested-state identity. Do not repair or relabel it as a pass without a new observation.

## Independent Scenarios

The structured cases in
[`checks/release-identity-scenarios.json`](../checks/release-identity-scenarios.json) cover valid
first-party and vendor identities plus format, revision, propagation, placeholder and digest
failures. The test owns an independent expected outcome; the fixture is not proof of a live
registry, deployment or telemetry system.

External formats remain owned by the
[OCI annotation specification](https://specs.opencontainers.org/image-spec/annotations/),
[Kubernetes recommended labels](https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/),
[OpenTelemetry service semantic conventions](https://opentelemetry.io/docs/specs/semconv/resource/service/)
and [Git revision parsing](https://git-scm.com/docs/git-rev-parse). This rule narrows those broader
formats for repository-owned first-party builds.
