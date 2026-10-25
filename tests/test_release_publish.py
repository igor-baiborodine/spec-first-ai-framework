"""Independent E04/E05 publication guards and fake GitHub boundary."""

import json
import os
import subprocess
import sys
import time
from hashlib import sha256
from pathlib import Path

import pytest
import yaml

from tools import release_publish as publisher

ROOT = Path(__file__).resolve().parents[1]
HEAD = "a" * 40
PREVIOUS = "b" * 40
OTHER = "c" * 40
CALCULATION = {
    "head": HEAD,
    "previousTag": "v1.0.0",
    "previousCommit": PREVIOUS,
    "nextTag": "v1.0.1",
    "commitCount": 1,
}


def validation_event(head=HEAD):
    return {
        "action": "completed",
        "repository": {"full_name": publisher.REPOSITORY},
        "workflow_run": {
            "name": "Framework Validation",
            "status": "completed",
            "conclusion": "success",
            "event": "push",
            "head_branch": "main",
            "head_sha": head,
            "repository": {"full_name": publisher.REPOSITORY},
            "head_repository": {"full_name": publisher.REPOSITORY},
        },
    }


def release_environment():
    return {
        "GITHUB_EVENT_NAME": "workflow_run",
        "GITHUB_REPOSITORY": publisher.REPOSITORY,
        "GITHUB_REF": publisher.MAIN_REF,
        "GITHUB_SHA": OTHER,  # workflow_run points this at the current default-branch tip.
    }


class FakeGitHub:
    def __init__(self):
        self.main = [HEAD]
        self.tags = {"v1.0.0": PREVIOUS}
        self.releases = {"v1.0.0": {"tag_name": "v1.0.0"}}
        self.writes = []
        self.release_failure = False

    def main_commit(self):
        if len(self.main) > 1:
            return self.main.pop(0)
        return self.main[0]

    def tag_commit(self, tag):
        return self.tags.get(tag)

    def release(self, tag):
        return self.releases.get(tag)

    def create_tag(self, tag, head):
        self.writes.append(("tag", tag, head))
        self.tags[tag] = head

    def create_release(self, tag, previous, head):
        self.writes.append(("release", tag, previous, head))
        if self.release_failure:
            raise publisher.PublicationError("tag-only partial state; manual intervention required")
        self.releases[tag] = {"tag_name": tag}


def test_trusted_main_publishes_one_tag_and_one_release():
    # given
    github = FakeGitHub()
    # when
    result = publisher.publish(CALCULATION, github, HEAD)
    # then
    assert result == {
        "status": "published",
        "head": HEAD,
        "tag": "v1.0.1",
        "previous_tag": "v1.0.0",
    }
    assert github.writes == [
        ("tag", "v1.0.1", HEAD),
        ("release", "v1.0.1", "v1.0.0", HEAD),
    ]


@pytest.mark.parametrize(
    "case,diagnostic",
    [
        ("stale", "stale run"),
        ("previous-tag", "previous tag/release"),
        ("previous-release", "previous tag/release"),
        ("conflicting-tag", "conflicts"),
        ("tag-only", "tag-only partial"),
        ("release-only", "without its tag"),
    ],
)
def test_invalid_remote_state_stops_before_any_write(case, diagnostic):
    # given
    github = FakeGitHub()
    if case == "stale":
        github.main = [OTHER]
    elif case == "previous-tag":
        github.tags["v1.0.0"] = OTHER
    elif case == "previous-release":
        del github.releases["v1.0.0"]
    elif case == "conflicting-tag":
        github.tags["v1.0.1"] = OTHER
    elif case == "tag-only":
        github.tags["v1.0.1"] = HEAD
    else:
        github.releases["v1.0.1"] = {"tag_name": "v1.0.1"}
    # when / then
    with pytest.raises(publisher.PublicationError, match=diagnostic):
        publisher.publish(CALCULATION, github, HEAD)
    assert github.writes == []


def test_complete_rerun_and_nonreleasing_range_make_no_write():
    # given
    github = FakeGitHub()
    github.tags["v1.0.1"] = HEAD
    github.releases["v1.0.1"] = {"tag_name": "v1.0.1"}
    # when
    rerun = publisher.publish(CALCULATION, github, HEAD)
    no_release = publisher.publish({**CALCULATION, "nextTag": None}, github, HEAD)
    # then
    assert rerun["status"] == "already_published"
    assert no_release["status"] == "no_release"
    assert github.writes == []


@pytest.mark.parametrize("case", ["main-before-tag", "main-before-release", "release-failure"])
def test_late_stale_or_release_failure_never_retries_a_partial_write(case):
    # given
    github = FakeGitHub()
    if case == "main-before-tag":
        github.main = [HEAD, OTHER]
    elif case == "main-before-release":
        github.main = [HEAD, HEAD, OTHER]
    else:
        github.release_failure = True
    # when / then
    with pytest.raises(publisher.PublicationError):
        publisher.publish(CALCULATION, github, HEAD)
    if case == "main-before-tag":
        assert github.writes == []
    else:
        assert github.writes == [("tag", "v1.0.1", HEAD)] + (
            [("release", "v1.0.1", "v1.0.0", HEAD)] if case == "release-failure" else []
        )


def test_partial_previous_tag_cannot_be_reported_as_no_release():
    # given: a rerun calculation could select a tag created by a failed earlier run.
    github = FakeGitHub()
    github.tags["v1.0.1"] = HEAD
    calculation = {
        **CALCULATION,
        "previousTag": "v1.0.1",
        "previousCommit": HEAD,
        "nextTag": None,
    }
    # when / then
    with pytest.raises(publisher.PublicationError, match="previous tag/release"):
        publisher.publish(calculation, github, HEAD)
    assert github.writes == []


@pytest.mark.parametrize(
    "change",
    [
        {"GITHUB_EVENT_NAME": "pull_request"},
        {"GITHUB_REF": "refs/heads/feature"},
        {"GITHUB_REPOSITORY": "fork/spec-first-ai-framework"},
    ],
)
def test_non_main_or_fork_context_cannot_publish(change):
    # given
    event = validation_event()
    environment = release_environment()
    environment.update(change)
    # when / then
    with pytest.raises(publisher.PublicationError, match="trusted main push"):
        publisher.guard_event(event, environment, HEAD, "success")


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", "Other Workflow"),
        ("status", "in_progress"),
        ("conclusion", "failure"),
        ("event", "pull_request"),
        ("head_branch", "feature"),
        ("head_sha", OTHER),
        ("repository", {"full_name": "fork/spec-first-ai-framework"}),
        ("head_repository", {"full_name": "fork/spec-first-ai-framework"}),
    ],
)
def test_untrusted_or_failed_validation_run_cannot_publish(field, value):
    # given
    event = validation_event()
    event["workflow_run"][field] = value
    # when / then
    with pytest.raises(publisher.PublicationError, match="trusted main push"):
        publisher.guard_event(event, release_environment(), HEAD, "success")


def test_event_payload_and_validation_result_are_required():
    # given
    environment = release_environment()
    event = validation_event()
    # when / then
    publisher.guard_event(event, environment, HEAD, "success")
    for invalid in ({**event, "action": "requested"}, {**event, "repository": None}):
        with pytest.raises(publisher.PublicationError):
            publisher.guard_event(invalid, environment, HEAD, "success")
    with pytest.raises(publisher.PublicationError):
        publisher.guard_event(event, environment, HEAD, "failure")


def test_workflow_limits_write_permission_to_dependent_main_job():
    # given
    validation = yaml.load(
        (ROOT / ".github/workflows/validation.yml").read_text(), Loader=yaml.BaseLoader
    )
    workflow = yaml.load(
        (ROOT / ".github/workflows/release.yml").read_text(), Loader=yaml.BaseLoader
    )
    # when / then
    assert validation["name"] == "Framework Validation"
    assert validation["on"] == {
        "pull_request": {"types": ["opened", "synchronize", "reopened", "edited"]},
        "push": {"branches": ["main"]},
    }
    assert validation["permissions"] == {"contents": "read"}
    assert set(validation["jobs"]) == {"validate"}
    assert workflow["name"] == "Framework Release"
    assert workflow["on"] == {
        "workflow_run": {
            "workflows": ["Framework Validation"],
            "types": ["completed"],
            "branches": ["main"],
        }
    }
    assert workflow["permissions"] == {"contents": "read"}
    job = workflow["jobs"]["publish"]
    guard = job["if"]
    for required in (
        "github.event_name == 'workflow_run'",
        "github.repository == 'igor-baiborodine/spec-first-ai-framework'",
        "github.event.workflow_run.conclusion == 'success'",
        "github.event.workflow_run.event == 'push'",
        "github.event.workflow_run.head_branch == 'main'",
        "github.event.workflow_run.repository.full_name == 'igor-baiborodine/spec-first-ai-framework'",
        "github.event.workflow_run.head_repository.full_name == 'igor-baiborodine/spec-first-ai-framework'",
    ):
        assert required in guard
    assert job["permissions"] == {"contents": "write"}
    assert job["concurrency"] == {
        "group": "framework-release-${{ github.repository }}",
        "cancel-in-progress": "false",
    }
    checkout = job["steps"][0]
    assert checkout["with"] == {
        "ref": "${{ github.event.workflow_run.head_sha }}",
        "fetch-depth": "0",
        "persist-credentials": "false",
    }
    provision = job["steps"][-2]["run"]
    assert all(
        command in provision
        for command in ("make setup", "make markdown-setup", "make gh-setup", "make gh-check")
    )
    publication = job["steps"][-1]
    assert publication["env"] == {
        "GH_TOKEN": "${{ github.token }}",
        "VALIDATED_SHA": "${{ github.event.workflow_run.head_sha }}",
        "VALIDATION_RESULT": "${{ github.event.workflow_run.conclusion }}",
    }
    assert '--head "$VALIDATED_SHA"' in publication["run"]
    assert "$GITHUB_SHA" not in publication["run"]
    assert '--event-file "$GITHUB_EVENT_PATH"' in publication["run"]


def test_gh_adapter_uses_create_ref_and_explicit_notes_and_latest_flags():
    # given
    class FakeRunner:
        def __init__(self):
            self.calls = []

        def run(self, argv, label, **options):
            self.calls.append((argv, label, options))
            if argv[1] == "api":
                return (
                    0,
                    "HTTP/2.0 201 Created\r\nContent-Type: application/json\r\n\r\n"
                    + json.dumps(
                        {"ref": "refs/tags/v1.0.1", "object": {"sha": HEAD, "type": "commit"}}
                    ),
                )
            return 0, ""

    runner = FakeRunner()
    github = publisher.GitHub(runner, Path("/disposable/gh"))
    # when
    github.create_tag("v1.0.1", HEAD)
    github.create_release("v1.0.1", "v1.0.0", HEAD)
    # then
    api, _, options = runner.calls[0]
    assert api[1:5] == ["api", "--include", "--method", "POST"]
    assert json.loads(options["data"]) == {"ref": "refs/tags/v1.0.1", "sha": HEAD}
    release, _, options = runner.calls[1]
    assert release[:4] == ["/disposable/gh", "release", "create", "v1.0.1"]
    assert {"--verify-tag", "--generate-notes", "--latest=false"} <= set(release)
    assert release[release.index("--notes-start-tag") + 1] == "v1.0.0"
    assert release[release.index("--target") + 1] == HEAD
    assert options["authenticated"] is True


def test_annotated_previous_tag_is_peeled_to_its_commit():
    # given
    class FakeRunner:
        def run(self, argv, _label, **_options):
            endpoint = argv[5]
            if endpoint.endswith("/git/ref/tags/v1.0.0"):
                body = {"ref": "refs/tags/v1.0.0", "object": {"type": "tag", "sha": OTHER}}
            else:
                assert endpoint.endswith("/git/tags/" + OTHER)
                body = {"object": {"type": "commit", "sha": PREVIOUS}}
            return 0, "HTTP/2.0 200 OK\r\nContent-Type: application/json\r\n\r\n" + json.dumps(body)

    # when
    result = publisher.GitHub(FakeRunner(), Path("/disposable/gh")).tag_commit("v1.0.0")
    # then
    assert result == PREVIOUS


@pytest.mark.parametrize(
    "body,expected",
    [
        ({"ref": publisher.MAIN_REF, "object": None}, "remote main ref"),
        ({"ref": publisher.MAIN_REF, "object": {"type": "tag", "sha": HEAD}}, "remote main ref"),
    ],
)
def test_malformed_main_ref_fails_closed(body, expected):
    class FakeRunner:
        def run(self, _argv, _label, **_options):
            return 0, "HTTP/2.0 200 OK\r\n\r\n" + json.dumps(body)

    with pytest.raises(publisher.PublicationError, match=expected):
        publisher.GitHub(FakeRunner(), Path("/disposable/gh")).main_commit()


@pytest.mark.parametrize(
    "status,body",
    [
        (0, {"ref": "refs/tags/v1.0.1", "object": None}),
        (0, {"ref": "refs/tags/v1.0.1", "object": {"type": "tag", "sha": HEAD}}),
        (1, {"message": "synthetic-secret-must-not-leak"}),
    ],
)
def test_tag_create_uncertainty_fails_closed_without_response_leak(status, body):
    class FakeRunner:
        def run(self, _argv, _label, **_options):
            code = 201 if status == 0 else 422
            return status, f"HTTP/2.0 {code} Result\r\n\r\n" + json.dumps(body)

    with pytest.raises(publisher.PublicationError, match="inspect remote state manually") as error:
        publisher.GitHub(FakeRunner(), Path("/disposable/gh")).create_tag("v1.0.1", HEAD)
    assert "synthetic-secret-must-not-leak" not in str(error.value)


@pytest.mark.integration
def test_gh_timeout_kills_owned_descendants_and_hides_token(tmp_path, capsys):
    # given
    child_pid = tmp_path / "child.pid"
    fake = tmp_path / "gh"
    fake.write_text(
        f"#!{sys.executable}\n"
        "import subprocess, sys, time\n"
        f"child = subprocess.Popen([{sys.executable!r}, '-c', 'import time; time.sleep(60)'])\n"
        f"open({str(child_pid)!r}, 'w').write(str(child.pid))\n"
        "print('synthetic-secret-must-not-leak', file=sys.stderr, flush=True)\n"
        "time.sleep(60)\n"
    )
    fake.chmod(0o755)
    runner = publisher.Runner("synthetic-secret-must-not-leak", seconds=0.7)
    # when / then
    with pytest.raises(publisher.PublicationError, match="timed out"):
        runner.run([str(fake)], "fake GitHub timeout", authenticated=True)
    assert child_pid.exists()
    assert "synthetic-secret-must-not-leak" not in capsys.readouterr().err
    proc = Path("/proc") / child_pid.read_text().strip() / "stat"
    deadline = time.monotonic() + 2
    while proc.exists() and proc.read_text().split()[2] != "Z" and time.monotonic() < deadline:
        time.sleep(0.01)
    assert not proc.exists() or proc.read_text().split()[2] == "Z"


@pytest.mark.parametrize(
    "output",
    [
        "synthetic-secret-must-not-leak",
        "Release calculation: synthetic-secret-must-not-leak",
        "Release calculation: Malformed Conventional Commit header synthetic-secret-must-not-leak",
        "Release calculation: Malformed Conventional Commit header\nsynthetic-secret-must-not-leak",
        "Release calculation: Malformed Conventional Commit header [commit synthetic-secret-must-not-leak]",
    ],
)
def test_calculation_failure_never_relays_unrecognized_output(output):
    # when
    diagnostic = publisher.calculation_failure(output)
    # then
    assert diagnostic == "release calculation failed; no publication attempted"


def test_authenticated_diagnostics_cannot_opt_into_capture():
    # given
    runner = publisher.Runner("synthetic-secret-must-not-leak")
    # when / then
    with pytest.raises(publisher.PublicationError, match="cannot be captured"):
        runner.run(
            ["must-not-start"], "authenticated phase", authenticated=True, capture_stderr=True
        )


@pytest.mark.integration
def test_captured_calculation_stderr_keeps_the_output_bound(capsys):
    # given
    runner = publisher.Runner("synthetic-secret-must-not-leak")
    # when / then
    with pytest.raises(publisher.PublicationError, match="response exceeded its size bound"):
        runner.run(
            [sys.executable, "-c", "import sys; sys.stderr.write('x' * (1024 * 1024 + 1))"],
            "release calculation",
            capture_stderr=True,
        )
    assert "synthetic-secret-must-not-leak" not in capsys.readouterr().err


@pytest.mark.integration
@pytest.mark.parametrize(
    ("scenario", "reason"),
    [
        ("header", "Malformed Conventional Commit header"),
        ("footer", "Malformed breaking-change footer"),
        ("baseline", "Required v1.0.0 baseline tag is missing"),
    ],
)
def test_calculation_failure_reports_safe_reason_before_any_github_call(tmp_path, scenario, reason):
    # given: real invalid history, with a sentinel in both the message and token.
    repository = tmp_path / "repository"
    repository.mkdir()

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(repository), *args],
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        ).stdout.strip()

    sentinel = "synthetic-secret-must-not-leak"
    git("init", "-q", "-b", "main")
    git("config", "user.name", "Synthetic Release")
    git("config", "user.email", "fixture@example.invalid")
    git("commit", "--allow-empty", "-q", "-m", "chore: baseline")
    if scenario != "baseline":
        git("tag", "v1.0.0")
    message = f"invalid {sentinel}" if scenario == "header" else f"fix: {sentinel}"
    if scenario == "footer":
        message += "\n\nBREAKING CHANGE:"
    git("commit", "--allow-empty", "-q", "-m", message)
    bad_commit = git("rev-parse", "HEAD")
    git("commit", "--allow-empty", "-q", "-m", "docs: later valid commit")
    head = git("rev-parse", "HEAD")
    event_file = tmp_path / "event.json"
    event_file.write_text(json.dumps(validation_event(head)))
    called = tmp_path / "gh-called"
    fake = tmp_path / "gh"
    fake.write_text(
        f"#!{sys.executable}\nfrom pathlib import Path\n"
        f"Path({str(called)!r}).touch()\nraise SystemExit(1)\n"
    )
    fake.chmod(0o755)

    def manifest():
        return {
            str(path.relative_to(repository)): sha256(path.read_bytes()).hexdigest()
            for path in repository.rglob("*")
            if path.is_file()
        }

    original = manifest()
    # when
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(ROOT / "tools/release_publish.py"),
            "--repo",
            str(repository),
            "--head",
            head,
            "--event-file",
            str(event_file),
            "--gh",
            str(fake),
            "--validation-result",
            "success",
        ],
        text=True,
        capture_output=True,
        timeout=35,
        env={
            **os.environ,
            "GH_TOKEN": sentinel,
            "GITHUB_EVENT_NAME": "workflow_run",
            "GITHUB_REPOSITORY": publisher.REPOSITORY,
            "GITHUB_REF": publisher.MAIN_REF,
        },
    )
    # then
    assert result.returncode == 1
    assert reason in result.stderr
    if scenario != "baseline":
        assert bad_commit in result.stderr, "report the offending commit, not just HEAD"
    assert "no publication attempted" in result.stderr
    assert sentinel not in result.stdout + result.stderr
    assert result.stdout == ""
    assert not called.exists()
    assert manifest() == original


@pytest.mark.integration
def test_cli_publishes_and_reruns_only_against_fake_github_and_disposable_git(tmp_path):
    # given: real local release history and a fake gh executable with external state.
    repository = tmp_path / "repository"
    repository.mkdir()

    def git(*args):
        result = subprocess.run(
            ["git", "-C", str(repository), *args],
            text=True,
            capture_output=True,
            timeout=10,
            check=True,
        )
        return result.stdout.strip()

    git("init", "-q", "-b", "main")
    git("config", "user.name", "Synthetic Release")
    git("config", "user.email", "fixture@example.invalid")
    (repository / "source.txt").write_text("baseline\n")
    git("add", "source.txt")
    git("commit", "-q", "-m", "chore: baseline")
    previous = git("rev-parse", "HEAD")
    git("tag", "v1.0.0")
    git(
        "commit",
        "--allow-empty",
        "-q",
        "-m",
        "fix: [issue-3] handle $(echo synthetic-secret-must-not-leak) `id`",
    )
    head = git("rev-parse", "HEAD")
    event_file = tmp_path / "event.json"
    event_file.write_text(json.dumps(validation_event(head)))
    state_file = tmp_path / "fake-gh-state.json"
    state_file.write_text(
        json.dumps(
            {
                "main": head,
                "tags": {"v1.0.0": previous},
                "releases": {
                    "v1.0.0": {
                        "tag_name": "v1.0.0",
                        "draft": False,
                        "prerelease": False,
                        "published_at": "2026-10-24T00:00:00Z",
                    }
                },
                "writes": [],
            }
        )
    )
    fake = tmp_path / "gh"
    fake.write_text(
        f"#!{sys.executable}\n"
        + """import json, os, sys
from pathlib import Path
state_file = Path(__STATE__)
state = json.loads(state_file.read_text())
assert os.environ["GH_TOKEN"] == "synthetic-secret-must-not-leak"
print(os.environ["GH_TOKEN"], file=sys.stderr)
args = sys.argv[1:]
def respond(code, value):
    state_file.write_text(json.dumps(state))
    print(f"HTTP/2.0 {code} Result\\r\\nContent-Type: application/json\\r\\n\\r\\n" + json.dumps(value))
    sys.exit(0 if code < 400 else 1)
if args[0] == "api":
    method, endpoint = args[3:5]
    assert endpoint.startswith("repos/igor-baiborodine/spec-first-ai-framework/")
    if endpoint.endswith("/git/ref/heads/main"):
        respond(200, {"ref": "refs/heads/main", "object": {"type": "commit", "sha": state["main"]}})
    if "/git/ref/tags/" in endpoint:
        tag = endpoint.rsplit("/", 1)[1]
        if tag not in state["tags"]:
            respond(404, {"message": "Not Found"})
        respond(200, {"ref": "refs/tags/" + tag, "object": {"type": "commit", "sha": state["tags"][tag]}})
    if "/releases/tags/" in endpoint:
        tag = endpoint.rsplit("/", 1)[1]
        if tag not in state["releases"]:
            respond(404, {"message": "Not Found"})
        respond(200, state["releases"][tag])
    if endpoint.endswith("/git/refs") and method == "POST":
        body = json.load(sys.stdin)
        tag = body["ref"].removeprefix("refs/tags/")
        assert tag not in state["tags"]
        state["tags"][tag] = body["sha"]
        state["writes"].append(["tag", tag, body["sha"]])
        respond(201, {"ref": body["ref"], "object": {"type": "commit", "sha": body["sha"]}})
    sys.exit(2)
if args[:2] == ["release", "create"]:
    tag = args[2]
    assert "--verify-tag" in args and "--generate-notes" in args and "--latest=false" in args
    assert args[args.index("--notes-start-tag") + 1] == "v1.0.0"
    assert args[args.index("--target") + 1] == state["tags"][tag]
    state["releases"][tag] = {"tag_name": tag, "draft": False, "prerelease": False,
                              "published_at": "2026-10-24T00:00:01Z"}
    state["writes"].append(["release", tag])
    state_file.write_text(json.dumps(state))
    sys.exit(0)
sys.exit(2)
""".replace("__STATE__", repr(str(state_file)))
    )
    fake.chmod(0o755)

    def manifest():
        return {
            str(path.relative_to(repository)): sha256(path.read_bytes()).hexdigest()
            for path in repository.rglob("*")
            if path.is_file()
        }

    original = manifest()
    environment = {
        **os.environ,
        "GH_TOKEN": "synthetic-secret-must-not-leak",
        "GITHUB_EVENT_NAME": "workflow_run",
        "GITHUB_REPOSITORY": publisher.REPOSITORY,
        "GITHUB_REF": publisher.MAIN_REF,
        "GITHUB_SHA": OTHER,
    }

    def invoke():
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(ROOT / "tools/release_publish.py"),
                "--repo",
                str(repository),
                "--head",
                head,
                "--event-file",
                str(event_file),
                "--gh",
                str(fake),
                "--validation-result",
                "success",
            ],
            text=True,
            capture_output=True,
            env=environment,
            timeout=35,
        )
        assert "synthetic-secret-must-not-leak" not in result.stdout + result.stderr
        assert manifest() == original, "publisher changed local files, index, or refs"
        return result

    # when
    first = invoke()
    second = invoke()
    state = json.loads(state_file.read_text())
    state["main"] = OTHER
    state_file.write_text(json.dumps(state))
    stale = invoke()
    # then
    assert first.returncode == second.returncode == 0, first.stderr + second.stderr
    assert json.loads(first.stdout)["status"] == "published"
    assert json.loads(second.stdout)["status"] == "already_published"
    assert stale.returncode == 1 and "stale run" in stale.stderr
    assert json.loads(state_file.read_text())["writes"] == [
        ["tag", "v1.0.1", head],
        ["release", "v1.0.1"],
    ]
