"""Guarded GitHub release publication for one validated main-push revision.

The CLI reads a completed validation workflow event, validates the originating
push/repository/head SHA and the local checkout,
then consults GitHub before either write. GH_TOKEN is supplied only through the process
environment. Exit 0 reports no release, an existing complete release, or a new release;
exit 1 is a safe stop requiring inspection, 2 is CLI usage, and 130/143 are interruption.
The publication budget is 180 seconds, with 30-second subprocess phases and bounded teardown.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

if __package__:
    from .framework_runtime import CheckError, Interrupted, interrupted
else:
    from framework_runtime import CheckError, Interrupted, interrupted

REPOSITORY = "igor-baiborodine/spec-first-ai-framework"
MAIN_REF = "refs/heads/main"
SHA = re.compile(r"[0-9a-f]{40}")
TAG = re.compile(r"v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")


class PublicationError(CheckError):
    """Controlled, non-secret publication stop."""


def valid_sha(value: object) -> str:
    if not isinstance(value, str) or SHA.fullmatch(value) is None:
        raise PublicationError("invalid validated commit identity")
    return value


def valid_tag(value: object) -> str:
    if not isinstance(value, str) or TAG.fullmatch(value) is None:
        raise PublicationError("invalid release tag identity")
    return value


def guard_event(event: object, environment: dict[str, str], head: str, validation: str) -> None:
    """Check both runner context and event payload before any GitHub request."""
    run = event.get("workflow_run") if isinstance(event, dict) else None
    if (
        validation != "success"
        or environment.get("GITHUB_EVENT_NAME") != "workflow_run"
        or environment.get("GITHUB_REPOSITORY") != REPOSITORY
        or environment.get("GITHUB_REF") != MAIN_REF
        or not isinstance(event, dict)
        or not isinstance(event.get("repository"), dict)
        or event["repository"].get("full_name") != REPOSITORY
        or event.get("action") != "completed"
        or not isinstance(run, dict)
        or run.get("name") != "Framework Validation"
        or run.get("status") != "completed"
        or run.get("conclusion") != "success"
        or run.get("event") != "push"
        or run.get("head_branch") != "main"
        or run.get("head_sha") != head
        or not isinstance(run.get("repository"), dict)
        or run["repository"].get("full_name") != REPOSITORY
        or not isinstance(run.get("head_repository"), dict)
        or run["head_repository"].get("full_name") != REPOSITORY
    ):
        raise PublicationError(
            "publication requires a successful validation run for this trusted main push"
        )


def validate_calculation(value: object, head: str) -> dict:
    if not isinstance(value, dict) or value.get("head") != head:
        raise PublicationError("release calculation did not match the validated SHA")
    previous = valid_tag(value.get("previousTag"))
    valid_sha(value.get("previousCommit"))
    candidate = value.get("nextTag")
    if candidate is not None:
        valid_tag(candidate)
        if tuple(map(int, TAG.fullmatch(candidate).groups())) <= tuple(
            map(int, TAG.fullmatch(previous).groups())
        ):
            raise PublicationError("candidate release is not newer than the previous release")
        if type(value.get("commitCount")) is not int or value["commitCount"] < 1:
            raise PublicationError("candidate release has no validated commit range")
    return value


class Runner:
    """Bounded, sanitized subprocess owner with one overall deadline."""

    def __init__(self, token: str, seconds: float = 180):
        if not token or not 0 < seconds <= 300:
            raise PublicationError("publication token or deadline unavailable")
        self.token = token
        self.deadline = time.monotonic() + seconds

    def run(
        self, argv: list[str], label: str, *, authenticated: bool = False, data: bytes | None = None
    ) -> tuple[int, str]:
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise PublicationError("publication deadline exceeded; remote outcome unverified")
        environment = {key: os.environ[key] for key in ("PATH", "HOME") if key in os.environ}
        environment.update(
            LC_ALL="C",
            NO_COLOR="1",
            GH_PROMPT_DISABLED="1",
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CONFIG_GLOBAL=os.devnull,
            GIT_OPTIONAL_LOCKS="0",
            GIT_TERMINAL_PROMPT="0",
        )
        if authenticated:
            environment.update(GH_TOKEN=self.token, GH_HOST="github.com", GH_REPO=REPOSITORY)
        started = time.monotonic()
        limit = min(remaining, 30)
        next_heartbeat = started + 20
        print(f"release-publish: {label} started", file=sys.stderr, flush=True)
        with tempfile.TemporaryFile() as output:
            process = subprocess.Popen(
                argv,
                stdin=subprocess.PIPE if data is not None else subprocess.DEVNULL,
                stdout=output,
                stderr=subprocess.DEVNULL,
                env=environment,
                start_new_session=True,
            )
            try:
                if data is not None:
                    try:
                        process.stdin.write(data)
                    except BrokenPipeError:
                        pass
                    finally:
                        process.stdin.close()
                while True:
                    if os.fstat(output.fileno()).st_size > 1024 * 1024:
                        raise PublicationError(f"{label} response exceeded its size bound")
                    now = time.monotonic()
                    if now - started >= limit or now >= self.deadline:
                        raise PublicationError(f"{label} timed out; remote outcome unverified")
                    if now >= next_heartbeat:
                        print(
                            f"release-publish: {label} in progress ({int(now - started)}s)",
                            file=sys.stderr,
                            flush=True,
                        )
                        next_heartbeat += 20
                    try:
                        status = process.wait(timeout=min(0.1, limit - (now - started)))
                        break
                    except subprocess.TimeoutExpired:
                        continue
            finally:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait(timeout=2)
            output.seek(0)
            result = output.read(1024 * 1024 + 1)
            if len(result) > 1024 * 1024:
                raise PublicationError(f"{label} response exceeded its size bound")
        print(f"release-publish: {label} completed", file=sys.stderr, flush=True)
        return status, result.decode("utf-8", errors="strict")


class GitHub:
    """Pinned gh boundary; all mutations are single-attempt operations."""

    def __init__(self, runner: Runner, executable: Path):
        self.runner = runner
        self.executable = str(executable)

    def api(self, method: str, endpoint: str, payload: dict | None = None) -> dict | None:
        argv = [self.executable, "api", "--include", "--method", method, endpoint]
        data = None
        if payload is not None:
            argv.extend(("--input", "-"))
            data = json.dumps(payload, separators=(",", ":")).encode()
        status, response = self.runner.run(
            argv, f"GitHub {method} {endpoint.split('/')[-1]}", authenticated=True, data=data
        )
        match = re.match(r"HTTP/\S+ (\d{3})\b", response.splitlines()[0] if response else "")
        if match is None:
            raise PublicationError("GitHub response status unavailable; remote outcome unverified")
        code = int(match.group(1))
        if code == 404 and method == "GET":
            return None
        expected = 201 if method == "POST" else 200
        if status != 0 or code != expected:
            raise PublicationError("GitHub request failed; remote outcome unverified")
        separator = "\r\n\r\n" if "\r\n\r\n" in response else "\n\n"
        if separator not in response:
            raise PublicationError("GitHub response body unavailable; remote outcome unverified")
        body = json.loads(response.split(separator, 1)[1])
        if not isinstance(body, dict):
            raise PublicationError("GitHub response shape unavailable; remote outcome unverified")
        return body

    def main_commit(self) -> str:
        result = self.api("GET", f"repos/{REPOSITORY}/git/ref/heads/main")
        object_value = result.get("object") if result is not None else None
        if (
            result is None
            or result.get("ref") != MAIN_REF
            or not isinstance(object_value, dict)
            or object_value.get("type") != "commit"
        ):
            raise PublicationError("remote main ref is missing or malformed")
        return valid_sha(object_value.get("sha"))

    def tag_commit(self, tag: str) -> str | None:
        result = self.api("GET", f"repos/{REPOSITORY}/git/ref/tags/{valid_tag(tag)}")
        if result is None:
            return None
        if result.get("ref") != f"refs/tags/{tag}":
            raise PublicationError("remote tag ref is ambiguous")
        object_value = result.get("object")
        seen: set[str] = set()
        for _ in range(5):
            if not isinstance(object_value, dict):
                break
            identity = valid_sha(object_value.get("sha"))
            if identity in seen:
                break
            seen.add(identity)
            if object_value.get("type") == "commit":
                return identity
            if object_value.get("type") != "tag":
                break
            tag_data = self.api("GET", f"repos/{REPOSITORY}/git/tags/{identity}")
            if tag_data is None:
                break
            object_value = tag_data.get("object")
        raise PublicationError("remote tag does not resolve to a commit")

    def release(self, tag: str) -> dict | None:
        result = self.api("GET", f"repos/{REPOSITORY}/releases/tags/{valid_tag(tag)}")
        if result is None:
            return None
        if (
            result.get("tag_name") != tag
            or result.get("draft") is not False
            or result.get("prerelease") is not False
            or not isinstance(result.get("published_at"), str)
            or not result["published_at"]
        ):
            raise PublicationError("release state is unexpected; manual inspection required")
        return result

    def create_tag(self, tag: str, head: str) -> None:
        try:
            result = self.api(
                "POST", f"repos/{REPOSITORY}/git/refs", {"ref": f"refs/tags/{tag}", "sha": head}
            )
        except PublicationError as error:
            raise PublicationError(
                "tag creation outcome uncertain; inspect remote state manually"
            ) from error
        object_value = result.get("object") if result is not None else None
        if (
            result is None
            or result.get("ref") != f"refs/tags/{tag}"
            or not isinstance(object_value, dict)
            or object_value.get("type") != "commit"
            or object_value.get("sha") != head
        ):
            raise PublicationError("tag creation response uncertain; inspect remote state manually")

    def create_release(self, tag: str, previous: str, head: str) -> None:
        argv = [
            self.executable,
            "release",
            "create",
            tag,
            "--repo",
            REPOSITORY,
            "--verify-tag",
            "--generate-notes",
            "--notes-start-tag",
            previous,
            "--target",
            head,
            "--latest=false",
        ]
        status, _ = self.runner.run(argv, "release creation", authenticated=True)
        if status != 0:
            raise PublicationError(
                "tag-only partial state or uncertain release outcome; manual intervention required"
            )


def publish(calculation: dict, github: GitHub, head: str) -> dict:
    """Make one bounded publication decision from independent GitHub observations."""
    calculation = validate_calculation(calculation, head)

    def require_current_main() -> None:
        if github.main_commit() != head:
            raise PublicationError("main moved beyond the validated SHA; stale run stopped")

    require_current_main()
    previous = calculation["previousTag"]
    if (
        github.tag_commit(previous) != calculation["previousCommit"]
        or github.release(previous) is None
    ):
        raise PublicationError("previous tag/release is incomplete or differs from local history")
    candidate = calculation["nextTag"]
    if candidate is None:
        return {"status": "no_release", "head": head, "previous_tag": previous}
    tag_commit = github.tag_commit(candidate)
    release = github.release(candidate)
    if tag_commit is not None:
        if tag_commit != head:
            raise PublicationError("candidate tag conflicts with the validated SHA")
        if release is None:
            raise PublicationError("tag-only partial state; manual intervention required")
        return {"status": "already_published", "head": head, "tag": candidate}
    if release is not None:
        raise PublicationError("release exists without its tag; manual intervention required")
    require_current_main()
    github.create_tag(candidate, head)
    if github.tag_commit(candidate) != head:
        raise PublicationError(
            "created tag does not resolve to the validated SHA; manual intervention required"
        )
    if github.release(candidate) is not None:
        raise PublicationError("release appeared during publication; manual intervention required")
    require_current_main()
    github.create_release(candidate, previous, head)
    if github.tag_commit(candidate) != head or github.release(candidate) is None:
        raise PublicationError("release read-back incomplete; manual intervention required")
    return {"status": "published", "head": head, "tag": candidate, "previous_tag": previous}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo", required=True, type=Path, help="complete local framework checkout"
    )
    parser.add_argument("--head", required=True, help="full SHA validated by the dependent job")
    parser.add_argument(
        "--event-file", required=True, type=Path, help="GitHub validation workflow event JSON"
    )
    parser.add_argument("--gh", required=True, type=Path, help="checksum-verified gh executable")
    parser.add_argument(
        "--validation-result", required=True, help="dependent validation job result"
    )
    args = parser.parse_args(argv)
    try:
        head = valid_sha(args.head)
        repository = args.repo.resolve(strict=True)
        executable = args.gh.resolve(strict=True)
        if (
            not repository.is_dir()
            or not (repository / ".git").exists()
            or not os.access(executable, os.X_OK)
        ):
            raise PublicationError("framework checkout or pinned GitHub CLI unavailable")
        event = json.loads(args.event_file.read_text())
        guard_event(event, os.environ, head, args.validation_result)
        runner = Runner(os.environ.get("GH_TOKEN", ""))
        status, current = runner.run(
            ["git", "-C", str(repository), "rev-parse", "HEAD"], "checkout identity"
        )
        if status != 0 or current.strip() != head:
            raise PublicationError("checkout does not match the validated SHA")
        script = Path(__file__).with_name("release-calculation.mjs")
        status, output = runner.run(
            ["node", str(script), "calculate", "--repo", str(repository), "--head", head],
            "release calculation",
        )
        if status != 0:
            raise PublicationError("release calculation failed; no publication attempted")
        calculation = validate_calculation(json.loads(output), head)
        result = publish(calculation, GitHub(runner, executable), head)
        print(json.dumps(result, sort_keys=True))
        return 0
    except Interrupted as error:
        print("release-publish: interrupted; remote outcome requires inspection", file=sys.stderr)
        return 128 + int(error.args[0])
    except CheckError, OSError, ValueError, TypeError, subprocess.SubprocessError:
        error = sys.exception()
        message = str(error) if isinstance(error, CheckError) else "malformed or unavailable input"
        print(f"release-publish: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    raise SystemExit(main())
