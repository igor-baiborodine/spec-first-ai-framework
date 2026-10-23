<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Go Rules](#go-rules)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Go Rules

For Go work, select rules by the affected boundary. Read the entry point and these core rules
for implementation, migration, or tooling changes:

- [Go development](development.md): command ownership, implementation, lifecycle, contracts, and migration.
- [Go formatting](formatting.md): mandatory formatter policy and scope.
- [Go validation](validation.md): module-aware checks and evidence.

Load the additional rules when the task crosses their boundary:

- [Go architecture](architecture.md): new or changed service structure, dependencies, ports,
  composition, resource ownership, or architecture handoff.
- [Go API and transport](api-transport.md): HTTP/gRPC APIs, contracts, OpenAPI, transport
  mappings, security, or compatibility.
- [Go testing](test.md): writing or reviewing Go tests, fixtures, and test design.

Read multiple additional rules when a change crosses multiple boundaries. For example, an HTTP
handler and its tests require the API and transport and testing rules; a new service also requires
architecture. Validation still selects the checks required for the changed module, even when a
detail rule does not apply.

Use the consumer-declared command owner for all Go development operations. Where Make is selected,
use its targets and never bypass them. See the development rule for missing-capability handling.
Apply selected [Naming rules](../naming-rules.md) when creating or renaming Go source files, package
directories, or surrounding repository paths.

This file is the Go routing entry point. It adds no separate policy or instruction precedence.
