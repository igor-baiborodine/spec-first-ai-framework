<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [CI Workflow Rules](#ci-workflow-rules)
  - [Scope And Ownership](#scope-and-ownership)
  - [Names And Structure](#names-and-structure)
  - [Actions And Reusable Dependencies](#actions-and-reusable-dependencies)
  - [Permissions And Untrusted Input](#permissions-and-untrusted-input)
  - [Triggers, Reliability And Reuse](#triggers-reliability-and-reuse)
  - [Duration, Resources And Provider Cost](#duration-resources-and-provider-cost)
  - [Validation And Evidence](#validation-and-evidence)
  - [References](#references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# CI Workflow Rules

## Scope And Ownership

Apply these rules when creating, reviewing or changing continuous-integration workflows, including
GitHub Actions and paid third-party providers. The consumer owns provider selection, workflow and
required-check identities, runner classes, credentials, cache backends, usage limits and accepted
duration or cost budgets. Preserve those local contracts unless the ticket explicitly changes
them. CI validation does not authorize a deployment, release, write-capable credential or live
environment mutation.

Prefer the consumer's existing Make targets and module-owned commands as workflow entry points.
Keep provider YAML focused on orchestration so the same validation can run locally where its
dependencies are available. Do not hide a provider-only behavior behind a claimed portable command.

## Names And Structure

- Give every workflow a concise top-level `name:` that states its scope and purpose. Use
  `run-name:` when event metadata or manual inputs are needed to distinguish runs in the provider UI.
- Give every job and every step a human-readable `name:`. Keep job IDs stable, concise and suitable
  for expressions and required-check wiring; display names explain the work to reviewers and
  operators.
- Name steps after the observable action or check, such as `Run Go unit tests` or `Upload coverage
  report`. Avoid labels such as `Run commands`, `Build`, or `Step 3` when a more specific name exists.
- Keep a workflow centered on one trigger and validation or delivery purpose. Split unrelated
  privileges, schedules or release effects when separation makes their authority and failures
  easier to assess.

## Actions And Reusable Dependencies

- For every new or changed remote action, reusable workflow, plugin or CI image, use the latest
  stable compatible release available at implementation time. Verify the release through the
  owner's canonical repository or registry. Do not select a floating default branch or an
  unreviewed prerelease.
- Pin GitHub Actions and cross-repository reusable workflows to an immutable full-length commit SHA.
  Put the verified release tag on the same line as a comment, for example
  `owner/action@<full-sha> # v4.2.1`, so reviewers and update tooling can identify the release.
- Record why an older stable release is required, the compatibility or security constraint, and
  the condition for revisiting it. An unexplained stale major or SHA is not an accepted pin.
- Enable or preserve an owning update mechanism such as Dependabot where the consumer supports it.
  Review release notes and rerun affected checks; automated version discovery does not authorize an
  update or prove compatibility.
- Treat third-party actions, reusable workflows, plugins and images as executable dependencies.
  Review their source, publisher, permissions, inputs, network effects and release provenance in
  proportion to their authority. Prefer a small trusted dependency set over convenience wrappers.

## Permissions And Untrusted Input

- Declare the minimum `GITHUB_TOKEN` or provider permission set at workflow or job scope. Put
  write permissions on only the job that needs them, and preserve read-only defaults elsewhere.
- Keep checkout credentials disabled after checkout unless a reviewed step requires them. Never
  expose a write token or secret to untrusted pull-request code, action output, cache contents or
  expression-expanded shell text.
- Treat branch names, commit messages, issue and pull-request fields, matrix values, action outputs,
  downloaded artifacts and cache contents as untrusted data. Pass values through environment
  variables or structured inputs and quote them in shell commands; do not interpolate untrusted
  expressions directly into executable scripts.
- Review `pull_request_target`, privileged follow-up workflows and self-hosted runner use as trust
  boundary changes. Never check out or execute an untrusted head revision with privileged secrets.
- Pin runner images or declared tool versions where reproducibility matters. Do not rely on an
  undeclared tool that happens to exist in the current hosted image.

## Triggers, Reliability And Reuse

- Select only the events, activity types, branches and paths needed for the workflow. Before adding
  path filters, verify that required checks will still report a terminal result for excluded changes.
- Avoid duplicate validation for the same revision through overlapping push and pull-request
  triggers unless the two runs prove different contracts. Use concurrency groups to cancel
  superseded branch or pull-request validation when safe; do not cancel release, deployment or
  stateful work that must finish or be recovered.
- Run independent jobs in parallel and use `needs` only for real data or ordering dependencies.
  Choose matrix `fail-fast` behavior deliberately so a fast failure does not discard required
  compatibility evidence.
- Set a bounded `timeout-minutes` for every job and for individual steps that can block on a
  network, service, polling loop or external tool. Cleanup and artifact capture must still run on
  the relevant failure and cancellation paths without masking the primary result.
- Use caches only for reproducible inputs that can be safely regenerated. Treat restored cache
  contents as untrusted, use keys that include the governing lock/configuration inputs, and keep a
  correct cache-miss path. Use artifacts for retained outputs rather than as a substitute for a
  dependency cache.
- Use reusable workflows, composite actions, scripts or Make targets when they remove meaningful
  duplication while preserving explicit inputs, permissions, versions, failure propagation and
  understandable logs. Do not create a shared abstraction for one short sequence.

## Duration, Resources And Provider Cost

For a new workflow or a material change, define or preserve budgets for both feedback latency and
total resource consumption on each frequent trigger. Measure the representative baseline before
claiming an improvement. Record at least:

- end-to-end wall-clock duration and critical-path jobs
- total runner execution time or provider credits across all parallel jobs
- queue, provisioning, dependency download, cache and artifact-transfer time when material
- runner class, CPU/memory allocation, matrix size, retry policy and expected trigger frequency
- the provider's actual billing unit and plan constraints

Do not assume that a lower wall-clock duration costs less. Parallel jobs can shorten feedback while
increasing total billed runner time or credits; a larger runner can have the opposite tradeoff.
Assess both dimensions against the consumer's accepted budget. For paid third-party systems such as
Harness CI, use that provider's current credit/resource and concurrency model rather than converting
GitHub-hosted runner minutes by name.

Before adding a matrix axis, repeated setup, cross-provider handoff or paid integration, justify the
coverage or delivery value against its expected duration and resource cost. Prefer safe trigger
selection, cancellation of superseded validation, dependency caching, reusable prepared images and
test partitioning when measurements show a net benefit. Preserve independent coverage, clean-build
paths, cache-miss correctness and useful failure diagnostics; cost reduction does not justify
skipping required checks.

## Validation And Evidence

- Run the repository-owned workflow syntax/lint command and its negative fixture where available.
  Run the commands invoked by changed jobs through their owning local interfaces when prerequisites
  exist.
- Verify that every remote dependency pin maps to the recorded stable release and that referenced
  reusable workflows, secrets, variables, environments and outputs exist at the selected revision.
- Exercise important trigger, condition, matrix, failure, cancellation and timeout behavior with a
  safe fixture or provider run when static validation cannot prove it.
- Record hosted evidence before claiming actual permissions, runner availability, cache behavior,
  duration, billed usage, credits or required-check integration. A local lint pass proves none of
  those provider-side properties.
- Compare observed duration and resource usage with the accepted baseline and budgets after a
  material workflow change. Document regressions, measurement limits and the next action rather
  than calling an unmeasured workflow faster or cheaper.

## References

- [GitHub Actions workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [GitHub secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
- [Keeping actions up to date with Dependabot](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/auto-update-actions)
- [GitHub dependency caching](https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching)
- [GitHub Actions metrics](https://docs.github.com/en/actions/concepts/metrics)
- [Harness CI pipeline components and optimization](https://developer.harness.io/docs/continuous-integration/use-ci/prep-ci-pipeline-components/)
