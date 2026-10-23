#!/usr/bin/env python3
"""Verify that the current branch exactly matches its fetched remote upstream."""

from __future__ import annotations

import argparse
import signal
import sys
from pathlib import Path

from framework_check import CheckError, Git, Interrupted, interrupted


class BranchSyncError(RuntimeError):
    """The repository branch cannot be shown to match its upstream."""


def check_sync(repository: Path) -> str:
    runner = Git(30)

    def git(root: Path, *args: str, check: bool = True) -> str:
        try:
            return runner.run(root, *args, allowed=(0,) if check else (0, 1, 128))
        except CheckError as error:
            raise BranchSyncError(str(error)) from error

    try:
        root = Path(git(repository, "rev-parse", "--show-toplevel")).resolve(strict=True)
    except (BranchSyncError, OSError) as error:
        raise BranchSyncError(f"'{repository}' is not inside a Git repository") from error
    branch = git(root, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
    if not branch:
        raise BranchSyncError("detached HEAD has no branch to compare with a remote upstream")
    remote = git(root, "config", "--get", f"branch.{branch}.remote", check=False)
    if not remote or remote == ".":
        raise BranchSyncError(f"branch '{branch}' has no remote upstream")
    merge_ref = git(root, "config", "--get", f"branch.{branch}.merge", check=False)
    if not merge_ref:
        raise BranchSyncError(f"branch '{branch}' has no upstream merge ref")
    if remote.startswith("-") or not merge_ref.startswith("refs/heads/"):
        raise BranchSyncError("invalid remote upstream")
    git(root, "check-ref-format", merge_ref)
    upstream = f"{remote}/{merge_ref.removeprefix('refs/heads/')}"
    from git_helpers import safe_remote

    try:
        safe_remote(runner, root, remote)
    except CheckError as error:
        raise BranchSyncError(str(error)) from error
    try:
        git(root, "fetch", "--quiet", "--no-tags", "--", remote, merge_ref)
    except BranchSyncError as error:
        raise BranchSyncError(f"could not fetch upstream '{upstream}'") from error
    local_commit = git(root, "rev-parse", "HEAD")
    remote_commit = git(root, "rev-parse", "FETCH_HEAD")
    counts = git(root, "rev-list", "--left-right", "--count", f"{local_commit}...{remote_commit}")
    ahead, behind = counts.split()
    if local_commit != remote_commit:
        raise BranchSyncError(
            f"branch '{branch}' is not synchronized with '{upstream}'\n"
            f"branch-sync: local={local_commit} fetched={remote_commit} "
            f"ahead={ahead} behind={behind}"
        )
    return (
        f"branch-sync: branch='{branch}' upstream='{upstream}' commit='{local_commit}' "
        "ahead=0 behind=0"
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="check-upstream-sync.sh")
    result.add_argument("repository", nargs="?", type=Path, default=Path("."))
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    print(check_sync(arguments.repository))
    return 0


if __name__ == "__main__":
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    try:
        raise SystemExit(main())
    except Interrupted as error:
        raise SystemExit(128 + int(error.args[0])) from None
    except BranchSyncError as error:
        print(f"branch-sync: {error}", file=sys.stderr)
        raise SystemExit(1) from None
