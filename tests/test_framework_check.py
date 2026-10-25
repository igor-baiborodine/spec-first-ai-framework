"""Independent contract expectations for E04/E05/E09/E10/E15-E17."""

import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

from tools import framework_check as checker

CANDIDATE = Path(__file__).resolve().parents[1]


def git(root, *args, input=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        input=input,
        text=True,
        capture_output=True,
        env=env,
        timeout=10,
        check=True,
    )
    return result.stdout.strip()


def initialize(root):
    root.mkdir()
    git(root, "init", "-b", "main")
    git(root, "config", "user.name", "Synthetic Fixture")
    git(root, "config", "user.email", "fixture@example.invalid")


def commit(root, message):
    git(root, "add", "--all")
    git(root, "commit", "-m", message)
    return git(root, "rev-parse", "HEAD")


def tree_manifest(root):
    """Files, modes and symlinks include indexes, refs, configs and ignored/untracked files."""
    entries = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            entries[str(path.relative_to(root))] = ("link", os.readlink(path))
        elif path.is_file():
            entries[str(path.relative_to(root))] = (
                path.stat().st_mode,
                hashlib.sha256(path.read_bytes()).hexdigest(),
            )
    return entries


@pytest.fixture
def consumer(tmp_path):
    remote = tmp_path / "upstream"
    initialize(remote)
    for name in (
        "consumer.md",
        "catalog.json",
        "rules",
        "skills",
        "templates",
        "provenance",
        "prompts",
        "adapters",
        "scripts",
        "checks",
        "examples",
    ):
        source = CANDIDATE / name
        if source.is_dir():
            shutil.copytree(source, remote / name)
        else:
            shutil.copy2(source, remote / name)
    first = commit(remote, "fixture baseline")
    root = tmp_path / "consumer"
    initialize(root)
    (root / "AGENTS.md").write_text("Synthetic local guide; no delegated permissions.\n")
    initial = commit(root, "consumer before adoption")
    git(root, "-c", "protocol.file.allow=always", "submodule", "add", str(remote), "ai/framework")
    git(root, "config", "--file", ".gitmodules", "submodule.ai/framework.branch", "refs/heads/main")
    profile = {
        "version": 1,
        "consumer": "synthetic",
        "framework_path": "ai/framework",
        "artifact_root": "ai/artifacts",
        "issue_sync": "consumer-local policy; ad hoc fixture exempt",
        "components": ["core", "go", "java", "python"],
        "guides": ["AGENTS.md"],
        "tool_sources": ["AGENTS.md"],
        "conflicts": "stop-and-report",
        "commands": {
            "unit": {
                "owner": "AGENTS.md",
                "cwd": ".",
                "argv": ["false"],
                "prerequisites": "synthetic",
                "effects": "none",
                "scope": "declaration only; never executed",
            }
        },
    }
    (root / "ai/profile.json").write_text(json.dumps(profile))
    adopted = commit(root, "consumer adoption")
    dependency = root / "ai/framework"
    git(dependency, "checkout", "--detach", first)
    return {
        "root": root,
        "remote": remote,
        "dep": dependency,
        "first": first,
        "initial": initial,
        "adopted": adopted,
    }


def invoke(state, mode="freshness", *extra):
    root = state["root"]
    before = tree_manifest(root)
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(CANDIDATE / "tools/framework_check.py"),
            mode,
            "--consumer-root",
            str(root),
            "--framework-root",
            str(state["dep"]),
            *extra,
        ],
        capture_output=True,
        text=True,
        timeout=35,
    )
    assert tree_manifest(root) == before, "check changed consumer/submodule files or Git metadata"
    return result


def advance(state):
    (state["remote"] / "revision.txt").write_text("second commit\n")
    return commit(state["remote"], "advance upstream")


def select_tag(state, ref="refs/tags/v1.2.3"):
    profile_path = state["root"] / "ai/profile.json"
    profile = json.loads(profile_path.read_text())
    profile.update(version=2, upstream_ref=ref)
    profile_path.write_text(json.dumps(profile))


@pytest.mark.integration
def test_detached_equality_and_offline_integrity_are_separate(consumer):
    # given
    expected = consumer["first"]
    # when
    online = invoke(consumer)
    offline = invoke(consumer, "integrity")
    # then
    assert online.returncode == offline.returncode == 0
    assert json.loads(online.stdout)["upstream"] == expected
    assert json.loads(offline.stdout)["freshness"] == "unverified"
    assert git(consumer["dep"], "rev-parse", "--abbrev-ref", "HEAD") == "HEAD"


@pytest.mark.integration
def test_shallow_equality_is_supported(consumer):
    # given
    dep = consumer["dep"]
    shutil.rmtree(dep)  # owned fixture only
    git(
        consumer["root"],
        "clone",
        "--depth",
        "1",
        "--no-checkout",
        consumer["remote"].as_uri(),
        str(dep),
    )
    git(dep, "config", "remote.origin.url", str(consumer["remote"]))
    git(dep, "checkout", "--detach", consumer["first"])
    assert git(dep, "rev-parse", "--is-shallow-repository") == "true"
    # when
    result = invoke(consumer)
    # then
    assert result.returncode == 0, result.stderr


@pytest.mark.integration
@pytest.mark.parametrize("change", ["advance", "rewrite", "ahead", "diverged"])
def test_remote_drift_never_passes_exact_equality(consumer, change):
    # given
    remote = consumer["remote"]
    if change in ("advance", "rewrite", "diverged"):
        advance(consumer)
    if change == "rewrite":
        git(remote, "checkout", "--orphan", "replacement")
        git(remote, "commit", "-m", "unrelated history")
        git(remote, "branch", "-f", "main", "HEAD")
    if change in ("ahead", "diverged"):
        dep = consumer["dep"]
        git(dep, "config", "user.name", "Synthetic")
        git(dep, "config", "user.email", "fixture@example.invalid")
        (dep / "local.txt").write_text("local candidate\n")
        commit(dep, "local ahead")
        git(consumer["root"], "add", "ai/framework")
    # when
    result = invoke(consumer)
    # then
    assert result.returncode == 1
    assert "upstream differs: pin=" in result.stderr
    assert "upstream=" in result.stderr


@pytest.mark.integration
@pytest.mark.parametrize("annotated", [False, True])
def test_selected_release_tag_survives_branch_advance(consumer, annotated):
    # given: the parent gitlink and clean dependency remain at A while main moves to B.
    first = consumer["first"]
    ref = "refs/tags/v1.2.4" if annotated else "refs/tags/v1.2.3"
    if annotated:
        git(consumer["remote"], "tag", "-a", "-m", "reviewed release", "v1.2.4", first)
    else:
        git(consumer["remote"], "tag", "v1.2.3", first)
    tag_object = git(consumer["remote"], "rev-parse", ref)
    assert (tag_object != first) is annotated
    select_tag(consumer, ref)
    advance(consumer)
    # when
    online = invoke(consumer)
    offline = invoke(consumer, "integrity")
    # then
    assert online.returncode == offline.returncode == 0, online.stderr
    data = json.loads(online.stdout)
    assert data["ref"] == ref and data["ref_kind"] == "tag"
    assert data["configured_branch"] == "refs/heads/main"
    assert data["pin"] == data["head"] == data["upstream"] == first
    assert data["tag_object"] == (tag_object if annotated else None)
    offline_data = json.loads(offline.stdout)
    assert offline_data["freshness"] == "unverified"
    assert "upstream" not in offline_data
    assert "tag_object" not in offline_data
    assert offline_data["ref"] == ref


@pytest.mark.integration
@pytest.mark.parametrize("defect", ["missing", "moved", "head", "source", "dirty"])
def test_selected_release_tag_rejects_mismatch_without_repair(consumer, defect):
    # given
    first = consumer["first"]
    second = advance(consumer)
    git(consumer["remote"], "tag", "v1.2.3", first)
    select_tag(consumer)
    if defect == "missing":
        select_tag(consumer, "refs/tags/v9.9.9")
    elif defect == "moved":
        git(consumer["remote"], "tag", "-f", "v1.2.3", second)
    elif defect == "head":
        git(consumer["dep"], "fetch", "origin")
        git(consumer["dep"], "checkout", "--detach", second)
    elif defect == "source":
        git(consumer["root"], "config", "submodule.ai/framework.url", "/unapproved")
    else:
        (consumer["dep"] / "unexpected.txt").write_text("dirty dependency\n")
    # when
    result = invoke(consumer)
    # then
    assert result.returncode == 1
    assert {
        "missing": "ls-remote failed",
        "moved": "upstream differs",
        "head": "HEAD/pin mismatch",
        "source": "override",
        "dirty": "changes",
    }[defect] in result.stderr


@pytest.mark.integration
def test_selected_tag_honors_index_and_explicit_parent_commit(consumer):
    # given: index pin B, committed pin A, selected release tag B.
    second = advance(consumer)
    git(consumer["remote"], "tag", "v1.2.3", second)
    git(consumer["dep"], "fetch", "origin")
    git(consumer["dep"], "checkout", "--detach", second)
    git(consumer["root"], "add", "ai/framework")
    select_tag(consumer)
    # when
    indexed = invoke(consumer)
    committed = invoke(consumer, "integrity", "--commit", consumer["adopted"])
    reviewed_parent = commit(consumer["root"], "reviewed tag adoption")
    selected_commit = invoke(consumer, "freshness", "--commit", reviewed_parent)
    # then
    assert indexed.returncode == 0, indexed.stderr
    data = json.loads(indexed.stdout)
    assert data["pin"] == second and data["committed_pin"] == consumer["first"]
    assert data["index_differs_from_committed"] is True
    assert committed.returncode == 1 and "HEAD/pin mismatch" in committed.stderr
    assert selected_commit.returncode == 0, selected_commit.stderr
    selected_data = json.loads(selected_commit.stdout)
    assert selected_data["selection"] == reviewed_parent
    assert selected_data["pin"] == selected_data["upstream"] == second


@pytest.mark.integration
@pytest.mark.parametrize(
    "ref",
    [None, "", "v1.2.3", "refs/heads/main", "refs/tags/v01.2.3", "refs/tags/v1.2.3^{}"],
)
def test_invalid_selected_ref_does_not_fall_back_to_branch(consumer, ref):
    # given: branch mode would pass, but an explicit invalid selection must fail.
    select_tag(consumer, ref)
    # when
    result = invoke(consumer, "integrity")
    # then
    assert result.returncode == 1 and "canonical release tag ref" in result.stderr


@pytest.mark.parametrize(
    "response",
    [
        "garbage",
        f"{'a' * 40}\trefs/tags/v1.2.3^{{}}",
        f"{'a' * 40}\trefs/tags/v1.2.3\n{'b' * 40}\trefs/tags/other",
        f"{'a' * 40}\trefs/tags/v1.2.3\n{'a' * 40}\trefs/tags/v1.2.3^{{}}",
    ],
)
def test_malformed_tag_response_is_rejected(response, tmp_path):
    # given: synthetic malformed remote output, independent of the parser under test.
    class FakeGit:
        def run(self, *_args):
            return response

    # when / then
    with pytest.raises(checker.CheckError):
        checker.remote_tag(FakeGit(), tmp_path, "/disposable/source", "refs/tags/v1.2.3")


@pytest.mark.integration
def test_version_one_rejects_tag_field_and_version_two_without_it_keeps_branch_mode(consumer):
    # given
    profile_path = consumer["root"] / "ai/profile.json"
    profile = json.loads(profile_path.read_text())
    profile["upstream_ref"] = "refs/tags/v1.2.3"
    profile_path.write_text(json.dumps(profile))
    # when
    incompatible = invoke(consumer, "integrity")
    profile["version"] = 2
    del profile["upstream_ref"]
    profile_path.write_text(json.dumps(profile))
    matching = invoke(consumer)
    advance(consumer)
    drifted = invoke(consumer)
    # then
    assert incompatible.returncode == 1 and "requires profile version 2" in incompatible.stderr
    assert matching.returncode == 0, matching.stderr
    assert "ref_kind" not in json.loads(matching.stdout)
    assert drifted.returncode == 1 and "upstream differs" in drifted.stderr


@pytest.mark.integration
def test_index_upgrade_and_explicit_commit_do_not_fall_back(consumer):
    # given
    second = advance(consumer)
    git(consumer["dep"], "fetch", "origin")
    git(consumer["dep"], "checkout", "--detach", second)
    git(consumer["root"], "add", "ai/framework")
    # when
    index = invoke(consumer)
    committed = invoke(consumer, "integrity", "--commit", consumer["adopted"])
    absent = invoke(consumer, "integrity", "--commit", consumer["initial"])
    invalid = invoke(consumer, "integrity", "--commit", "unknown-ref")
    # then
    assert index.returncode == 0
    data = json.loads(index.stdout)
    assert data["pin"] == second and data["committed_pin"] == consumer["first"]
    assert data["index_differs_from_committed"] is True
    assert committed.returncode == absent.returncode == invalid.returncode == 1
    assert "HEAD/pin mismatch" in committed.stderr
    assert "missing gitlink" in absent.stderr
    git(consumer["dep"], "checkout", "--detach", consumer["first"])
    explicit = invoke(consumer, "integrity", "--commit", consumer["adopted"])
    assert explicit.returncode == 0
    assert json.loads(explicit.stdout)["selection"] == consumer["adopted"]


@pytest.mark.integration
@pytest.mark.parametrize(
    "defect,diagnostic",
    [
        ("tracked", "changes"),
        ("untracked", "changes"),
        ("uninitialized", "uninitialized"),
        ("head-mismatch", "HEAD/pin mismatch"),
        ("unmerged", "unmerged"),
        ("missing-gitlink", "missing"),
        ("missing-ref", "failed"),
        ("source-override", "override"),
        ("branch-override", "override"),
        ("origin-override", "override"),
        ("rewrite-override", "override"),
        ("access-failure", "failed"),
        ("modules-drift", "differs"),
    ],
)
def test_invalid_dependency_fails_without_repair(consumer, defect, diagnostic):
    # given
    root, dep = consumer["root"], consumer["dep"]
    if defect == "tracked":
        (dep / "consumer.md").write_text("modified tracked guidance")
    elif defect == "untracked":
        (dep / "unexpected.txt").write_text("unexpected")
    elif defect == "uninitialized":
        (dep / ".git").unlink()
    elif defect == "head-mismatch":
        second = advance(consumer)
        git(dep, "fetch", "origin")
        git(dep, "checkout", second)
    elif defect == "unmerged":
        git(root, "update-index", "--force-remove", "ai/framework")
        git(
            root,
            "update-index",
            "--index-info",
            input="".join(
                f"160000 {consumer['first']} {stage}\tai/framework\n" for stage in (1, 2, 3)
            ),
        )
    elif defect == "missing-gitlink":
        git(root, "update-index", "--force-remove", "ai/framework")
    elif defect == "missing-ref":
        git(
            root,
            "config",
            "--file",
            ".gitmodules",
            "submodule.ai/framework.branch",
            "refs/heads/missing",
        )
        git(root, "add", ".gitmodules")
    elif defect in ("source-override", "branch-override"):
        key = "url" if defect == "source-override" else "branch"
        git(root, "config", f"submodule.ai/framework.{key}", "conflicting")
    elif defect == "origin-override":
        git(dep, "config", "remote.origin.url", "conflicting")
    elif defect == "rewrite-override":
        git(root, "config", "url./unexpected.insteadOf", str(consumer["remote"]))
    elif defect == "access-failure":
        consumer["remote"].rename(consumer["remote"].with_name("unavailable"))
    elif defect == "modules-drift":
        with (root / ".gitmodules").open("a") as stream:
            stream.write("\n# unstaged source configuration\n")
    # when
    result = invoke(consumer)
    # then
    assert result.returncode == 1
    assert diagnostic in result.stderr


@pytest.mark.integration
def test_missing_capability_and_selective_rules(consumer):
    # when
    missing = invoke(consumer, "compose", "--language", "java", "--require", "dependency-scan")
    go = invoke(consumer, "compose", "--language", "go", "--boundary", "api", "--require", "unit")
    java = invoke(
        consumer, "compose", "--language", "java", "--boundary", "api", "--boundary", "test"
    )
    # then
    assert missing.returncode == 1 and "missing required command" in missing.stderr
    assert go.returncode == java.returncode == 0
    go_paths = json.loads(go.stdout)["composition"]["read"]
    java_paths = json.loads(java.stdout)["composition"]["read"]
    assert not any("java" in path for path in go_paths)
    assert "rules/java/api-transport.md" in java_paths and "rules/java/test.md" in java_paths
    assert not json.loads(go.stdout)["composition"]["commands_executed"]


@pytest.mark.integration
def test_root_relocation_and_depth_do_not_change_selection(consumer, tmp_path):
    # given
    root = consumer["root"]
    git(root, "mv", "ai/framework", "ai/shared")
    git(root, "config", "--file", ".gitmodules", "submodule.ai/framework.path", "ai/shared")
    git(root, "add", ".gitmodules")
    profile_path = root / "ai/profile.json"
    profile = json.loads(profile_path.read_text())
    profile["framework_path"] = "ai/shared"
    profile_path.write_text(json.dumps(profile))
    nested = tmp_path / "deeper" / "consumer"
    nested.parent.mkdir()
    root.rename(nested)
    consumer.update(root=nested, dep=nested / "ai/shared")
    # when
    result = invoke(consumer, "compose", "--language", "java")
    # then
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("value", ["../outside", "/tmp/outside", "-option", "."])
def test_paths_cannot_escape_or_alias_owner(tmp_path, value):
    # when / then
    with pytest.raises(checker.CheckError):
        checker.inside(tmp_path, value, exists=False)


def test_symlink_escape_is_rejected(tmp_path):
    # given
    (tmp_path / "escape").symlink_to(tmp_path.parent)
    # when / then
    with pytest.raises(checker.CheckError):
        checker.inside(tmp_path, "escape")


@pytest.mark.parametrize("seconds", [0, -1, 31, float("nan"), float("inf")])
def test_invalid_budgets_rejected(seconds):
    # when / then
    with pytest.raises(checker.CheckError):
        checker.Git(seconds)


def test_source_defects_are_detected(tmp_path):
    # given: complete source; independently seeded missing path, link and metadata defects.
    from source_check import source_files

    for source in source_files(CANDIDATE, "*"):
        if source.is_file():
            target = tmp_path / source.relative_to(CANDIDATE)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    selected = tmp_path / "rules/core.md"
    original = selected.read_text()
    selected.unlink()
    # when / then
    with pytest.raises(checker.CheckError, match="missing binding"):
        checker.source_check(tmp_path)
    selected.write_text(original + "\n[bad](absent.md)\n")
    with pytest.raises(checker.CheckError, match="broken framework link"):
        checker.source_check(tmp_path)
    selected.write_text(original)
    skill = tmp_path / "skills/code-review/SKILL.md"
    skill.write_text(skill.read_text().replace("name: code-review", "name: wrong"))
    with pytest.raises(checker.CheckError, match="skill/catalog mismatch"):
        checker.source_check(tmp_path)


def test_import_has_no_process_or_filesystem_side_effects(tmp_path):
    # given
    before = tree_manifest(tmp_path)
    # when
    result = subprocess.run(
        [sys.executable, "-B", "-c", "from tools import framework_check"],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(CANDIDATE)},
        capture_output=True,
        timeout=3,
    )
    # then
    assert result.returncode == 0 and not result.stdout and not result.stderr
    assert tree_manifest(tmp_path) == before


@pytest.mark.integration
@pytest.mark.parametrize("termination", ["timeout", "sigint", "sigterm", "failure"])
def test_transport_cleanup_and_sanitized_failure(tmp_path, monkeypatch, termination):
    # given
    fake = tmp_path / "bin"
    fake.mkdir()
    sentinel = "synthetic-secret-must-not-leak"
    child_pid = tmp_path / "child.pid"
    wrapper = fake / "git"
    wrapper.write_text(
        f"#!{sys.executable}\nimport subprocess,sys,time\nchild=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'])\nopen({str(child_pid)!r},'w').write(str(child.pid))\nprint({sentinel!r},file=sys.stderr,flush=True)\n"
        + ("sys.exit(9)\n" if termination == "failure" else "time.sleep(60)\n")
    )
    wrapper.chmod(0o755)
    monkeypatch.setenv("PATH", str(fake) + os.pathsep + os.environ["PATH"])
    runner = tmp_path / "runner.py"
    runner.write_text(
        "from tools.framework_check import *\nimport signal\nsignal.signal(signal.SIGINT,interrupted)\nsignal.signal(signal.SIGTERM,interrupted)\ntry:\n Git(0.6).run(Path('.'),'ls-remote')\nexcept Interrupted as e:\n print('interrupted',file=sys.stderr); sys.exit(128+e.args[0])\nexcept CheckError as e:\n print(str(e),file=sys.stderr); sys.exit(1)\n"
    )
    # when
    process = subprocess.Popen(
        [sys.executable, "-B", str(runner)],
        env={**os.environ, "PYTHONPATH": str(CANDIDATE)},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        deadline = time.monotonic() + 3
        while not child_pid.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert child_pid.exists()
        if termination in ("sigint", "sigterm"):
            process.send_signal(signal.SIGINT if termination == "sigint" else signal.SIGTERM)
        stdout, stderr = process.communicate(timeout=4)
        # then
        assert process.returncode == {"sigint": 130, "sigterm": 143}.get(termination, 1)
        assert sentinel.encode() not in stdout + stderr
        proc = Path("/proc") / child_pid.read_text().strip() / "stat"
        deadline = time.monotonic() + 2
        while proc.exists() and proc.read_text().split()[2] != "Z" and time.monotonic() < deadline:
            time.sleep(0.01)
        assert not proc.exists() or proc.read_text().split()[2] == "Z", (
            "transport descendant survived"
        )
    finally:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=2)


@pytest.mark.integration
@pytest.mark.parametrize("flag", ["--assume-unchanged", "--skip-worktree"])
def test_hidden_worktree_changes_are_not_trusted(consumer, flag):
    # given
    git(consumer["dep"], "update-index", flag, "consumer.md")
    (consumer["dep"] / "consumer.md").write_text("hidden change")
    # when
    result = invoke(consumer, "integrity")
    # then
    assert result.returncode == 1 and "flags hide changes" in result.stderr


@pytest.mark.integration
@pytest.mark.parametrize(
    "field,value,diagnostic",
    [
        ("version", 3, "profile version"),
        ("components", ["core", "unknown"], "unknown selected"),
        ("guides", [], "missing profile"),
        ("conflicts", "silently-override", "stop and report"),
        ("artifact_root", "../elsewhere", "inside"),
    ],
)
def test_invalid_profiles_fail_closed(consumer, field, value, diagnostic):
    # given
    profile_path = consumer["root"] / "ai/profile.json"
    profile = json.loads(profile_path.read_text())
    profile[field] = value
    profile_path.write_text(json.dumps(profile))
    # when
    result = invoke(consumer, "compose")
    # then
    assert result.returncode == 1 and diagnostic in result.stderr


@pytest.mark.integration
@pytest.mark.parametrize("tag_mode", [False, True])
def test_full_freshness_timeout_is_non_mutating(consumer, tmp_path, monkeypatch, tag_mode):
    # given
    if tag_mode:
        select_tag(consumer)
    real_git = shutil.which("git")
    fake = tmp_path / "bin"
    fake.mkdir()
    wrapper = fake / "git"
    wrapper.write_text(
        f"#!{sys.executable}\nimport os,sys,time\nif 'ls-remote' in sys.argv:\n print('synthetic-secret-must-not-leak',file=sys.stderr,flush=True)\n time.sleep(60)\nos.execv({real_git!r},[{real_git!r},*sys.argv[1:]])\n"
    )
    wrapper.chmod(0o755)
    monkeypatch.setenv("PATH", str(fake) + os.pathsep + os.environ["PATH"])
    # when
    result = invoke(consumer, "freshness", "--timeout", "2")
    # then
    assert result.returncode == 1
    assert "deadline exceeded" in result.stderr
    assert "synthetic-secret" not in result.stdout + result.stderr


@pytest.mark.integration
def test_artifacts_cannot_target_shared_source(consumer):
    # given
    profile_path = consumer["root"] / "ai/profile.json"
    profile = json.loads(profile_path.read_text())
    profile["artifact_root"] = "ai/framework/artifacts"
    profile_path.write_text(json.dumps(profile))
    # when
    result = invoke(consumer, "compose")
    # then
    assert result.returncode == 1 and "artifact root overlaps" in result.stderr


@pytest.mark.integration
def test_source_include_cannot_hide_override(consumer, tmp_path):
    # given
    config = tmp_path / "override.config"
    config.write_text('[url "/unexpected"]\n insteadOf = /tmp/\n')
    git(consumer["root"], "config", "include.path", str(config))
    # when
    result = invoke(consumer)
    # then
    assert result.returncode == 1 and "override" in result.stderr
