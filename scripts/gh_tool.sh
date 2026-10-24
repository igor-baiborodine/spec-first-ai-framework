#!/bin/sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
framework_root=$(CDPATH= cd -- "$script_dir/.." && pwd -P)
version=2.103.0
archive_sha=fdd768eb70f6409f80fcfa9f3a1c0adf0fc98d827ab3ce0bed2ac22762c5d786
binary_sha=011adf6809c50c89a70f2e367f2658a2fd7c2fcf7dfc705bfe8049e6e4c731b2
owned_binary="$framework_root/.tools/gh/$version/gh"

check_binary() {
    [ -x "$1" ] || { printf '%s\n' 'gh 2.103.0 unavailable; run explicit gh-setup.' >&2; exit 1; }
    actual_sha=$(sha256sum "$1")
    [ "${actual_sha%% *}" = "$binary_sha" ] || {
        printf '%s\n' 'gh binary checksum differs from the reviewed release.' >&2
        exit 1
    }
    actual_version=$("$1" --version)
    first_line=$(printf '%s\n' "$actual_version" | sed -n '1p')
    [ "$first_line" = "gh version $version (2026-10-21)" ] || {
        printf '%s\n' 'gh 2.103.0 required.' >&2
        exit 1
    }
}

[ "$#" -ge 1 ] || { printf '%s\n' 'usage: gh_tool.sh setup|check [absolute-binary]' >&2; exit 2; }
case "$1" in
    setup)
        [ "$#" -eq 1 ] || exit 2
        [ "$(uname -s)" = Linux ] && [ "$(uname -m)" = x86_64 ] || {
            printf '%s\n' 'gh setup is verified only for Linux amd64.' >&2
            exit 1
        }
        if [ -f "$owned_binary" ]; then
            check_binary "$owned_binary"
            exit 0
        fi
        mkdir -p "$(dirname "$owned_binary")"
        scratch=$(mktemp -d "$framework_root/.tools/gh/$version/.setup.XXXXXX")
        trap 'rm -rf -- "$scratch"' EXIT
        trap 'exit 129' HUP
        trap 'exit 130' INT
        trap 'exit 143' TERM
        curl --fail --location --silent --show-error --connect-timeout 10 --max-time 120 --retry 2 \
            "https://github.com/cli/cli/releases/download/v$version/gh_${version}_linux_amd64.tar.gz" \
            --output "$scratch/gh.tar.gz"
        archive_result=$(sha256sum "$scratch/gh.tar.gz")
        [ "${archive_result%% *}" = "$archive_sha" ] || {
            printf '%s\n' 'gh archive checksum differs from the reviewed release.' >&2
            exit 1
        }
        tar -xzf "$scratch/gh.tar.gz" -C "$scratch" "gh_${version}_linux_amd64/bin/gh"
        check_binary "$scratch/gh_${version}_linux_amd64/bin/gh"
        install -m 0755 "$scratch/gh_${version}_linux_amd64/bin/gh" "$scratch/gh.installed"
        mv "$scratch/gh.installed" "$owned_binary"
        check_binary "$owned_binary"
        ;;
    check)
        [ "$#" -eq 2 ] || exit 2
        case "$2" in /*) ;; *) printf '%s\n' 'gh check requires an absolute binary path.' >&2; exit 2;; esac
        check_binary "$2"
        ;;
    *) printf '%s\n' 'usage: gh_tool.sh setup|check [absolute-binary]' >&2; exit 2 ;;
esac
