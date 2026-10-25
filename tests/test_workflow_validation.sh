#!/bin/sh
set -eu

[ "$#" -eq 1 ] || { printf '%s\n' 'usage: test_workflow_validation.sh <absolute-actionlint>' >&2; exit 2; }
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
framework_root=$(CDPATH= cd -- "$script_dir/.." && pwd -P)
scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

cat > "$scratch/valid.yml" <<'YAML'
name: Validation fixture
on: push
jobs:
  validate:
    runs-on: ubuntu-24.04
    steps:
      - run: echo valid
YAML
"$framework_root/scripts/actionlint_tool.sh" check "$1" "$scratch"

cat > "$scratch/invalid.yml" <<'YAML'
name: Invalid expression fixture
on: push
jobs:
  validate:
    runs-on: ubuntu-24.04
    steps:
      - run: echo "${{ github.not_a_real_context }}"
YAML
if "$framework_root/scripts/actionlint_tool.sh" check "$1" "$scratch" > "$scratch/output" 2>&1; then
    printf '%s\n' 'Invalid workflow expression unexpectedly passed.' >&2
    exit 1
fi
if ! grep -q 'not_a_real_context' "$scratch/output"; then
    printf '%s\n' 'Invalid workflow did not fail for its expression.' >&2
    exit 1
fi
rm "$scratch/invalid.yml"
"$framework_root/scripts/actionlint_tool.sh" check "$1" "$scratch"
printf '%s\n' 'Workflow validation fixture passed.'
