"""Shared bounded process and path primitives for command entry points."""

from __future__ import annotations

import hashlib
import math
import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path


class CheckError(Exception):
    """Sanitized operational failure."""


class Interrupted(Exception):
    """Handled process interruption."""


def interrupted(signum: int, _frame: object) -> None:
    raise Interrupted(signum)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inside(root: Path, value: str, *, exists: bool = True) -> Path:
    if not isinstance(value, str) or not value or value.startswith("-"):
        raise CheckError("invalid relative path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or ".git" in path.parts:
        raise CheckError("path must remain inside its declared owner")
    result = (root / path).resolve()
    if not result.is_relative_to(root) or result == root:
        raise CheckError("path escapes or aliases its declared owner")
    if exists and not result.exists():
        raise CheckError(f"missing binding path: {value}")
    return result


class Git:
    """One overall work budget; separately bounded process-group teardown."""

    def __init__(self, seconds: float):
        if not math.isfinite(seconds) or not 0 < seconds <= 30:
            raise CheckError("timeout must be finite and in (0, 30] seconds")
        self.deadline = time.monotonic() + seconds

    def run(
        self,
        root: Path,
        *args: str,
        allowed: tuple[int, ...] = (0,),
        max_bytes: int = 65536,
        trim: bool = True,
    ) -> str:
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise CheckError("Git check deadline exceeded")
        env = {key: os.environ[key] for key in ("PATH", "HOME") if key in os.environ}
        env.update(
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CONFIG_GLOBAL=os.devnull,
            GIT_TERMINAL_PROMPT="0",
            GIT_OPTIONAL_LOCKS="0",
            GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=5",
            LC_ALL="C",
        )
        if args and args[0] in ("ls-files", "ls-tree", "diff", "status"):
            env["GIT_LITERAL_PATHSPECS"] = "1"
        with tempfile.TemporaryFile() as output:
            try:
                process = subprocess.Popen(
                    [
                        "git",
                        "-c",
                        "core.fsmonitor=false",
                        "-c",
                        "core.hooksPath=/dev/null",
                        "-C",
                        str(root),
                        *args,
                    ],
                    env=env,
                    stdin=subprocess.DEVNULL,
                    stdout=output,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
            except OSError as error:
                raise CheckError("Git runtime unavailable") from error
            try:
                while True:
                    if os.fstat(output.fileno()).st_size > max_bytes:
                        raise CheckError("Git response exceeds bounded output contract")
                    remaining = self.deadline - time.monotonic()
                    if remaining <= 0:
                        raise subprocess.TimeoutExpired("git", 0)
                    try:
                        result = process.wait(timeout=min(remaining, 0.05))
                        break
                    except subprocess.TimeoutExpired:
                        continue
            except subprocess.TimeoutExpired as error:
                raise CheckError(
                    "Git check deadline exceeded; upstream unavailable/unverified"
                ) from error
            finally:
                # Kill descendants even when their immediate parent exited; never leave a transport.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait(timeout=2)
            if result not in allowed:
                raise CheckError(f"Git {args[0]} failed; dependency/configuration unavailable")
            output.seek(0)
            data = output.read(max_bytes + 1)
            if len(data) > max_bytes:
                raise CheckError("Git response exceeds bounded output contract")
            text = data.decode("utf-8", errors="strict")
            return text.strip() if trim else text
