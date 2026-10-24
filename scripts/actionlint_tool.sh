#!/bin/sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
framework_root=$(CDPATH= cd -- "$script_dir/.." && pwd -P)
version=1.7.12
archive_sha=8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8
binary_sha=c872d6db8c6bf83a8eaa704fc93999f027d55dffbc63b8a6abdccb47df5f4cd4
owned_binary="$framework_root/.tools/actionlint/$version/actionlint"

check_binary() {
    [ -x "$1" ] || { printf '%s\n' 'actionlint 1.7.12 unavailable; run explicit actionlint-setup.' >&2; exit 1; }
    actual_sha=$(sha256sum "$1")
    [ "${actual_sha%% *}" = "$binary_sha" ] || {
        printf '%s\n' 'actionlint binary checksum differs from the reviewed release.' >&2
        exit 1
    }
    actual_version=$("$1" -version)
    first_line=$(printf '%s\n' "$actual_version" | sed -n '1p')
    [ "$first_line" = "$version" ] || {
        printf '%s\n' 'actionlint 1.7.12 required.' >&2
        exit 1
    }
}

[ "$#" -ge 1 ] || { printf '%s\n' 'usage: actionlint_tool.sh setup|check [absolute-binary] [workflow-directory]' >&2; exit 2; }
case "$1" in
    setup)
        [ "$#" -eq 1 ] || exit 2
        [ "$(uname -s)" = Linux ] && [ "$(uname -m)" = x86_64 ] || {
            printf '%s\n' 'actionlint setup is verified only for Linux amd64.' >&2
            exit 1
        }
        if [ -f "$owned_binary" ]; then
            check_binary "$owned_binary"
            exit 0
        fi
        mkdir -p "$(dirname "$owned_binary")"
        scratch=$(mktemp -d "$framework_root/.tools/actionlint/$version/.setup.XXXXXX")
        trap 'rm -rf -- "$scratch"' EXIT
        trap 'exit 129' HUP
        trap 'exit 130' INT
        trap 'exit 143' TERM
        curl --fail --location --silent --show-error --connect-timeout 10 --max-time 120 --retry 2 \
            "https://github.com/rhysd/actionlint/releases/download/v$version/actionlint_${version}_linux_amd64.tar.gz" \
            --output "$scratch/actionlint.tar.gz"
        archive_result=$(sha256sum "$scratch/actionlint.tar.gz")
        [ "${archive_result%% *}" = "$archive_sha" ] || {
            printf '%s\n' 'actionlint archive checksum differs from the reviewed release.' >&2
            exit 1
        }
        tar -xzf "$scratch/actionlint.tar.gz" -C "$scratch" actionlint
        check_binary "$scratch/actionlint"
        install -m 0755 "$scratch/actionlint" "$scratch/actionlint.installed"
        mv "$scratch/actionlint.installed" "$owned_binary"
        check_binary "$owned_binary"
        ;;
    check)
        [ "$#" -ge 2 ] && [ "$#" -le 3 ] || exit 2
        binary=$2
        workflow_dir=${3:-"$framework_root/.github/workflows"}
        case "$binary" in /*) ;; *) printf '%s\n' 'Select an absolute actionlint executable.' >&2; exit 2;; esac
        [ -d "$workflow_dir" ] || { printf '%s\n' 'Workflow directory is missing.' >&2; exit 1; }
        check_binary "$binary"
        if [ "$#" -eq 3 ]; then shift 3; else shift 2; fi
        for workflow in "$workflow_dir"/*.yml "$workflow_dir"/*.yaml; do
            [ -f "$workflow" ] || continue
            set -- "$@" "$workflow"
        done
        [ "$#" -gt 0 ] || { printf '%s\n' 'No workflow files selected.' >&2; exit 1; }
        "$binary" -shellcheck= -pyflakes= "$@"
        ;;
    *)
        printf '%s\n' 'usage: actionlint_tool.sh setup|check [absolute-binary] [workflow-directory]' >&2
        exit 2
        ;;
esac
