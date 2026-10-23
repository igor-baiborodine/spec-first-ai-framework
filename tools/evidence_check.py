"""Capture/check versioned input identity without changing historical evidence records."""

from __future__ import annotations

import argparse
import json
import signal
import sys
from datetime import UTC, datetime
from pathlib import Path

from git_helpers import artifact_path, atomic_write, repository, revision

from framework_check import CheckError, Git, Interrupted, digest, inside, interrupted


def identity(root: Path, base: str, inputs: list[str]) -> dict:
    git = Git(30)
    repository(git, root)
    if not inputs or len(inputs) != len(set(inputs)):
        raise CheckError("declare distinct relevant specification/profile/adapter/source inputs")
    return {
        "version": 1,
        "base_ref": base,
        "base": revision(git, root, base),
        "head": revision(git, root, "HEAD"),
        "status": git.run(root, "status", "--porcelain=v1", "--untracked-files=all"),
        "index": git.run(root, "ls-files", "--stage", "--", *inputs),
        "inputs": {path: digest(inside(root, path).read_bytes()) for path in inputs},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("capture", "check"))
    parser.add_argument("--consumer-root", type=Path, required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--input", dest="inputs", action="append", required=True)
    parser.add_argument("--artifact-root", default="ai/artifacts")
    args = parser.parse_args()
    try:
        root = args.consumer_root.resolve(strict=True)
        current = identity(root, args.base, args.inputs)
        record = artifact_path(Git(5), root, args.record, args.artifact_root)
        if args.mode == "capture":
            current["observed_utc"] = datetime.now(UTC).isoformat()
            atomic_write(record, json.dumps(current, indent=2) + "\n")
        else:
            previous = json.loads(record.read_text())
            if previous.get("version") != 1:
                raise CheckError(
                    "unsupported or historical evidence schema; preserve old record and capture a new identity"
                )
            if any(previous.get(key) != value for key, value in current.items()):
                raise CheckError(
                    "stale evidence identity; rerun affected checks and record new results"
                )
        print(
            json.dumps({"mode": args.mode, "identity": "current", "behavior_result": "unverified"})
        )
        return 0
    except Interrupted as error:
        return 128 + int(error.args[0])
    except (CheckError, OSError, ValueError, TypeError) as error:
        print(
            str(error) if isinstance(error, CheckError) else "evidence input unavailable",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    raise SystemExit(main())
