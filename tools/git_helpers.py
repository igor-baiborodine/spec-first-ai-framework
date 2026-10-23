"""Bounded snapshot and published-revision helpers with explicit consumer roots."""

from __future__ import annotations

import argparse
import re
import signal
import sys
import tempfile
from pathlib import Path

from framework_check import CheckError, Git, Interrupted, inside, interrupted, object_id


def repository(git: Git, root: Path) -> Path:
    root = root.resolve(strict=True)
    if Path(git.run(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise CheckError("explicit consumer root must be the checkout root")
    return root


def revision(git: Git, root: Path, ref: str) -> str:
    if ref.startswith("-") or "\n" in ref or "\r" in ref:
        raise CheckError("invalid revision argument")
    try:
        return object_id(
            git.run(root, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}")
        )
    except CheckError as error:
        raise CheckError("Cannot resolve intended base/head ref") from error


def artifact_path(git: Git, root: Path, output: Path, artifact_root: str = "ai/artifacts") -> Path:
    """Validate the caller's local artifact boundary; never create an exclusion."""
    artifacts = inside(root, artifact_root, exists=False)
    requested = output if output.is_absolute() else root / output
    path = requested.resolve()
    if requested.is_symlink() or not path.is_relative_to(artifacts) or path == artifacts:
        raise CheckError("output must remain inside the consumer artifact root")
    exclude = Path(git.run(root, "rev-parse", "--git-path", "info/exclude"))
    if not exclude.is_absolute():
        exclude = root / exclude
    if f"/{artifact_root.rstrip('/')}/" not in exclude.read_text().splitlines():
        raise CheckError(
            "required checkout-local artifact exclusion is missing; no repair attempted"
        )
    relative = path.relative_to(root).as_posix()
    if git.run(root, "ls-files", "--", artifact_root):
        raise CheckError("indexed artifact paths block artifact writes")
    git.run(root, "check-ignore", "--", relative)
    if not path.parent.is_dir():
        raise CheckError("artifact output directory must already exist")
    return path


def atomic_write(path: Path, data: str) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", dir=path.parent, prefix=".framework-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def snapshot(root: Path, base: str, head: str, output: Path, artifact_root: str) -> None:
    git = Git(30)
    root = repository(git, root)
    base_sha, head_sha = revision(git, root, base), revision(git, root, head)
    merge = object_id(git.run(root, "merge-base", base_sha, head_sha))
    target = artifact_path(git, root, output, artifact_root)
    patch = git.run(
        root,
        "diff",
        "--no-ext-diff",
        "--no-textconv",
        f"{base_sha}...{head_sha}",
        max_bytes=16 * 1024 * 1024,
        trim=False,
    )
    header = (
        f"# Committed PR patch\n# Intended base ref: {base}\n# Base SHA: {base_sha}\n"
        f"# Head ref: {head}\n# Head SHA: {head_sha}\n# Merge-base SHA: {merge}\n"
        "# Comparison: git diff <base>...<head>\n"
        "# Staged, unstaged, and untracked work is excluded; inspect it separately.\n\n"
    )
    atomic_write(target, header + patch)
    print(f"Snapshot: base={base_sha} head={head_sha} merge-base={merge}")


def safe_remote(git: Git, root: Path, remote: str) -> None:
    if remote.startswith("-") or re.search(r"[\r\n?#]|://[^/]*@", remote):
        raise CheckError("remote must be explicit and credential-free")
    overrides = git.run(
        root,
        "config",
        "--local",
        "--get-regexp",
        r"^(url\..*\.(insteadof|pushinsteadof)|include\..*|includeif\..*|core\.sshcommand|remote\..*\.uploadpack|http\..*|credential\..*)$",
        allowed=(0, 1),
    )
    if overrides:
        raise CheckError("unsupported local transport override")
    url = git.run(root, "config", "--local", "--get", f"remote.{remote}.url", allowed=(0, 1))
    if url and re.search(r"[\r\n?#]|://[^/]*@", url):
        raise CheckError("configured remote must be credential-free")


def published(root: Path, values: list[str]) -> None:
    git = Git(30)
    root = repository(git, root)
    triples = [values[:3], values[3:]]
    for remote, ref, expected in triples:
        object_id(expected)
        if not ref.startswith("refs/"):
            raise CheckError("Published PR refs must be valid, fully qualified refs/* names")
        try:
            git.run(root, "check-ref-format", ref)
        except CheckError as error:
            raise CheckError(
                "Published PR refs must be valid, fully qualified refs/* names"
            ) from error
        safe_remote(git, root, remote)
    verified = []
    for label, (remote, ref, expected) in zip(("base", "head"), triples, strict=True):
        try:
            git.run(root, "fetch", "--quiet", "--no-tags", "--", remote, ref)
            actual = revision(git, root, "FETCH_HEAD")
        except CheckError as error:
            raise CheckError(f"Cannot fetch published PR {label} ref") from error
        if actual != expected:
            raise CheckError(f"Published PR {label} revision mismatch")
        verified.append(actual)
    # Recheck both remote refs after the fetches; caller must also recheck host metadata.
    for label, (remote, ref, expected) in zip(("base", "head"), triples, strict=True):
        rows = git.run(root, "ls-remote", "--exit-code", "--refs", "--", remote, ref).splitlines()
        if len(rows) != 1 or rows[0].split() != [expected, ref]:
            raise CheckError(f"Published PR {label} moved during verification")
    merge = object_id(git.run(root, "merge-base", *verified))
    print(f"published-pr: base={verified[0]} head={verified[1]} merge-base={merge}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    snap = commands.add_parser("snapshot")
    snap.add_argument("root", type=Path)
    snap.add_argument("base")
    snap.add_argument("head")
    snap.add_argument("output", type=Path)
    snap.add_argument("--artifact-root", default="ai/artifacts")
    pub = commands.add_parser("published")
    pub.add_argument("root", type=Path)
    pub.add_argument("revisions", nargs=6)
    args = parser.parse_args(argv)
    try:
        if args.mode == "snapshot":
            snapshot(args.root, args.base, args.head, args.output, args.artifact_root)
        else:
            published(args.root, args.revisions)
        return 0
    except Interrupted as error:
        return 128 + int(error.args[0])
    except (CheckError, OSError, ValueError) as error:
        print(
            str(error) if isinstance(error, CheckError) else "helper input unavailable",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    raise SystemExit(main())
