.DEFAULT_GOAL := help
FRAMEWORK_ROOT := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
PYTHON ?= $(FRAMEWORK_ROOT)/.venv/bin/python
UV ?= uv
ACTIONLINT ?= $(FRAMEWORK_ROOT)/.tools/actionlint/1.7.12/actionlint
GH_CLI ?= $(FRAMEWORK_ROOT)/.tools/gh/2.103.0/gh
NODE ?= node
PYTHON_ENV = $(abspath $(dir $(PYTHON))/..)
PYTHON_FILES ?= tools tests examples/python-testing
MARKDOWN_FILES ?=
export PYTHONDONTWRITEBYTECODE := 1
export RUFF_NO_CACHE := true

.PHONY: help setup markdown-setup actionlint-setup gh-setup gh-check runtime-check development-check format format-check lint test-collect test-fast test-integration check source-check markdown-format markdown-check workflow-check workflow-test release-test
help: ## Show supported interfaces without setup or mutation
	@printf '%s\n' 'setup: explicitly provision locked CPython development environment (network/cache writes)' 'markdown-setup: explicitly provision locked Node Markdown/release dependencies (network/node_modules writes)' 'actionlint-setup: explicitly provision checksum-verified actionlint 1.7.12 for Linux amd64' 'gh-setup: explicitly provision checksum-verified gh 2.103.0 for Linux amd64' 'gh-check: verify selected GH_CLI without installation' 'check test-collect: source, Python, workflow and release validation plus disposable tests' 'release-test: exercise version calculation in disposable Git repositories' 'format: selected Python mutation; override PYTHON_FILES for narrow scope' 'markdown-format / markdown-check: require explicit MARKDOWN_FILES selection' 'PYTHON overrides must identify CPython 3.14.8; checks never install'
setup: ## Explicitly provision the pinned environment and dependencies
	@cd "$(FRAMEWORK_ROOT)" && "$(UV)" sync --locked --python 3.14.8
markdown-setup: ## Explicitly provision locked Node Markdown and release dependencies
	@cd "$(FRAMEWORK_ROOT)" && npm ci --ignore-scripts --no-audit --no-fund
actionlint-setup: ## Explicitly provision checksum-verified actionlint for Linux amd64
	@"$(FRAMEWORK_ROOT)/scripts/actionlint_tool.sh" setup
gh-setup: ## Explicitly provision checksum-verified GitHub CLI 2.103.0 for Linux amd64
	@"$(FRAMEWORK_ROOT)/scripts/gh_tool.sh" setup
gh-check: ## Verify GH_CLI identity without installation or GitHub access
	@"$(FRAMEWORK_ROOT)/scripts/gh_tool.sh" check "$(GH_CLI)"
runtime-check: ## Verify the selected runtime without installation
	@"$(FRAMEWORK_ROOT)/scripts/runtime_check.sh" "$(PYTHON)"
development-check: runtime-check ## Verify locked development-package identities without installation
	@"$(PYTHON)" "$(FRAMEWORK_ROOT)/tools/runtime_check.py" --development
	@cd "$(FRAMEWORK_ROOT)" && UV_PROJECT_ENVIRONMENT="$(PYTHON_ENV)" "$(UV)" sync --locked --check --offline --python "$(PYTHON)"
format: development-check ## Format only selected handwritten Python
	@cd "$(FRAMEWORK_ROOT)" && "$(PYTHON)" -m ruff format $(PYTHON_FILES)
format-check: development-check ## Non-mutating Python format check
	@cd "$(FRAMEWORK_ROOT)" && "$(PYTHON)" -m ruff format --check $(PYTHON_FILES)
lint: development-check ## Non-mutating selected Python lint
	@cd "$(FRAMEWORK_ROOT)" && "$(PYTHON)" -m ruff check $(PYTHON_FILES)
test-collect: development-check ## No-path discovery excludes full acceptance
	@cd "$(FRAMEWORK_ROOT)" && "$(PYTHON)" -m pytest --collect-only -q
	@cd "$(FRAMEWORK_ROOT)" && "$(PYTHON)" -m pytest --collect-only -q examples/python-testing/integration
test-fast: development-check ## Pure/fake-boundary and preserved Python example tests
	@cd "$(FRAMEWORK_ROOT)" && "$(PYTHON)" -m pytest -q -m 'not integration and not acceptance' tests examples/python-testing/tests
test-integration: development-check ## Actual disposable Git, subprocess and example integration tests
	@cd "$(FRAMEWORK_ROOT)" && PYTHON_EXAMPLE_INTEGRATION=1 "$(PYTHON)" -m pytest -q -m integration tests examples/python-testing/integration
source-check: development-check ## YAML metadata, catalog, link and adapter validation
	@"$(PYTHON)" -B "$(FRAMEWORK_ROOT)/tools/framework_check.py" source --framework-root "$(FRAMEWORK_ROOT)"
workflow-check: ## Lint all framework workflows with the pinned, preinstalled actionlint
	@"$(FRAMEWORK_ROOT)/scripts/actionlint_tool.sh" check "$(ACTIONLINT)"
workflow-test: workflow-check ## Verify workflow lint failure propagation with disposable fixtures
	@"$(FRAMEWORK_ROOT)/tests/test_workflow_validation.sh" "$(ACTIONLINT)"
release-test: ## Validate release calculation and squash-message inputs without publication
	@cd "$(FRAMEWORK_ROOT)" && "$(NODE)" --test tests/test_release_calculation.mjs
markdown-format: runtime-check ## Format explicit Markdown files through owned doctoc
	@cd "$(FRAMEWORK_ROOT)" && "$(FRAMEWORK_ROOT)/scripts/markdown.sh" format $(MARKDOWN_FILES)
markdown-check: runtime-check ## Check explicit Markdown files using disposable copies
	@cd "$(FRAMEWORK_ROOT)" && "$(FRAMEWORK_ROOT)/scripts/markdown.sh" check $(MARKDOWN_FILES)
check: format-check lint test-fast test-integration source-check workflow-test release-test ## Local development gate; no final client/adoption claim
