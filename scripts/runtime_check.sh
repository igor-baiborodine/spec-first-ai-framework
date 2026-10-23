#!/bin/sh
set -eu
[ "$#" -eq 1 ] || { printf '%s\n' 'usage: runtime_check.sh <absolute-python>' >&2; exit 2; }
case "$1" in /*) ;; *) printf '%s\n' 'Select an absolute CPython 3.14.8 executable.' >&2; exit 1;; esac
[ -x "$1" ] || { printf '%s\n' 'Selected Python unavailable; run explicit setup. No installation attempted.' >&2; exit 1; }
PYTHONDONTWRITEBYTECODE=1 "$1" -I -c 'import platform,sys; sys.exit(0 if (platform.python_implementation(),platform.python_version()) == ("CPython","3.14.8") else "CPython 3.14.8 required; no fallback")'
