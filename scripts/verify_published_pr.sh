#!/bin/sh
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
framework_root=$(CDPATH= cd -- "$script_dir/.." && pwd -P)
python=${PYTHON:-$framework_root/.venv/bin/python}
"$script_dir/runtime_check.sh" "$python"
exec "$python" -B "$framework_root/tools/git_helpers.py" published "$@"
