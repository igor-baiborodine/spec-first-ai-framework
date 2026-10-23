"""Step 10 regressions derived from the accepted composition/evidence contracts."""

import json
import os
import shutil
import subprocess
import sys

import pytest
from test_framework_check import CANDIDATE, commit, git, invoke, tree_manifest
from test_framework_check import consumer as consumer

from tools import framework_check as checker
from tools.source_check import source_files


@pytest.fixture
def source_copy(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    for path in source_files(CANDIDATE, "*"):
        if path.is_file():
            target = root / path.relative_to(CANDIDATE)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    return root


@pytest.mark.parametrize(
    "defect", ["skill", "template", "route", "house", "anchor", "yaml", "adapter", "local-path"]
)
def test_source_gate_rejects_structural_defects(source_copy, defect):
    # given
    catalog_path = source_copy / "catalog.json"
    catalog = json.loads(catalog_path.read_text())
    if defect == "skill":
        del catalog["skills"]["code-review"]
    elif defect == "template":
        del catalog["templates"]["pr-review"]
    elif defect == "route":
        catalog["routes"]["go"]["api"] = ["rules/python/test.md"]
    elif defect == "house":
        catalog["components"]["house"] = []
    elif defect == "anchor":
        with (source_copy / "consumer.md").open("a") as stream:
            stream.write("\n[bad](rules/core.md#missing-anchor)\n")
    elif defect == "yaml":
        path = source_copy / "skills/code-review/SKILL.md"
        path.write_text(path.read_text().replace("description:", "description: [invalid:"))
    elif defect == "adapter":
        (source_copy / "adapters/codex/skills/code-review/SKILL.md.in").write_text(
            "invented procedure"
        )
    elif defect == "local-path":
        with (source_copy / "rules/core.md").open("a") as stream:
            stream.write("\nUse /home/someone/consumer/.venv/bin/python\n")
    catalog_path.write_text(json.dumps(catalog))
    # when / then
    with pytest.raises(checker.CheckError):
        checker.source_check(source_copy)


@pytest.mark.integration
def test_selected_house_operations_and_explicit_style_are_returned(consumer):
    # given
    path = consumer["root"] / "ai/profile.json"
    profile = json.loads(path.read_text())
    profile["components"] += ["house", "operations"]
    profile["styles"] = {"java": "local"}
    path.write_text(json.dumps(profile))
    # when
    result = invoke(consumer, "compose", "--language", "java")
    # then
    assert result.returncode == 0, result.stderr
    composed = json.loads(result.stdout)["composition"]
    assert "rules/naming-rules.md" in composed["read"]
    assert "rules/operations.md" in composed["read"]
    assert composed["styles"] == {"java": "local"}
    assert not any(path.startswith("rules/go/") for path in composed["read"])


@pytest.mark.integration
@pytest.mark.parametrize(
    "defect",
    [
        "missing-markdown",
        "missing-tool",
        "style",
        "source-overlap",
        "unknown-mode",
        "boundary-without-language",
    ],
)
def test_composition_failures_are_explicit_and_non_mutating(consumer, defect):
    # given
    path = consumer["root"] / "ai/profile.json"
    profile = json.loads(path.read_text())
    args = ["--require", "markdown-check"]
    if defect == "missing-tool":
        profile["commands"]["markdown-check"] = {
            **profile["commands"]["unit"],
            "argv": ["definitely-absent-framework-runtime"],
        }
    elif defect == "style":
        profile["styles"] = {"java": "invented-style"}
    elif defect == "source-overlap":
        profile["artifact_root"] = "AGENTS.md"
    elif defect == "unknown-mode":
        args = ["--boundary", "invented", "--language", "go"]
    elif defect == "boundary-without-language":
        args = ["--boundary", "api"]
    path.write_text(json.dumps(profile))
    # when
    result = invoke(consumer, "compose", *args)
    # then
    assert result.returncode == 1
    assert not result.stdout


@pytest.mark.integration
def test_upgrade_rollback_preserves_unrelated_work_and_historical_artifacts(consumer):
    # given
    root, dependency = consumer["root"], consumer["dep"]
    (root / ".git/info/exclude").write_text("/ai/artifacts/\n")
    artifacts = root / "ai/artifacts/old-ticket"
    artifacts.mkdir(parents=True)
    (artifacts / "old.md").write_text("Historical prose without identity fields\n")
    (root / "unrelated.txt").write_text("keep me\n")
    protected = tree_manifest(artifacts)
    (consumer["remote"] / "revision.txt").write_text("reviewed upgrade\n")
    second = commit(consumer["remote"], "reviewed fixture upgrade")
    # when: explicitly requested mutation is distinct from non-mutating integrity.
    git(dependency, "fetch", "origin")
    git(dependency, "checkout", "--detach", second)
    git(root, "add", "ai/framework")
    upgraded = invoke(consumer, "integrity")
    git(dependency, "checkout", "--detach", consumer["first"])
    git(root, "add", "ai/framework")
    rolled_back = invoke(consumer, "integrity")
    # then
    assert upgraded.returncode == rolled_back.returncode == 0
    assert json.loads(rolled_back.stdout)["pin"] == consumer["first"]
    assert tree_manifest(artifacts) == protected
    assert (root / "unrelated.txt").read_text() == "keep me\n"


@pytest.mark.integration
@pytest.mark.parametrize(
    "changed", ["spec", "profile", "adapter", "future-schema", "historical-schema"]
)
def test_stale_or_incompatible_evidence_is_rejected_without_rewriting(consumer, changed):
    # given
    root = consumer["root"]
    (root / ".git/info/exclude").write_text("/ai/artifacts/\n")
    directory = root / "ai/artifacts/ticket"
    directory.mkdir(parents=True)
    spec = directory / "ticket-content.md"
    spec.write_text("Expected behavior\n")
    record = directory / "identity.json"
    inputs = ["ai/artifacts/ticket/ticket-content.md", "ai/profile.json", "AGENTS.md"]
    common = ["--consumer-root", str(root), "--base", "main", "--record", str(record)]
    for value in inputs:
        common += ["--input", value]

    def run(mode):
        return subprocess.run(
            [sys.executable, "-B", str(CANDIDATE / "tools/evidence_check.py"), mode, *common],
            capture_output=True,
            text=True,
            timeout=35,
        )

    assert run("capture").returncode == 0
    assert run("check").returncode == 0
    if changed in ("spec", "profile", "adapter"):
        target = {"spec": spec, "profile": root / "ai/profile.json", "adapter": root / "AGENTS.md"}[
            changed
        ]
        with target.open("a") as stream:
            stream.write("\nchanged input\n")
    else:
        record.write_text(json.dumps({"version": 2}) if changed == "future-schema" else "{}")
    before = record.read_bytes()
    # when
    result = run("check")
    # then
    assert result.returncode == 1 and not result.stdout
    assert record.read_bytes() == before
    assert "stale" in result.stderr or "schema" in result.stderr


@pytest.mark.integration
@pytest.mark.parametrize("script", ["test_refresh_git_diff.sh", "test_verify_published_pr.sh"])
def test_preserved_shell_helper_fixtures(script):
    # given / when
    result = subprocess.run(
        ["bash", str(CANDIDATE / "tests" / script)],
        env={**os.environ, "PYTHON": sys.executable},
        capture_output=True,
        text=True,
        timeout=45,
    )
    # then
    assert result.returncode == 0, result.stdout + result.stderr
    assert "fixtures passed" in result.stdout


@pytest.mark.integration
def test_markdown_check_is_non_mutating_and_format_is_idempotent(tmp_path):
    # given
    path = tmp_path / "guide.md"
    path.write_text("# Guide\n\n## Setup\n\nInstructions.\n")
    command = [sys.executable, "-B", str(CANDIDATE / "tools/markdown.py")]
    common = [str(path), "--root", str(tmp_path)]
    before = path.read_bytes()
    # when
    drift = subprocess.run([*command, "check", *common], capture_output=True, timeout=35)
    # then
    assert drift.returncode == 1 and path.read_bytes() == before
    assert (
        subprocess.run([*command, "format", *common], capture_output=True, timeout=35).returncode
        == 0
    )
    formatted = path.read_bytes()
    assert (
        subprocess.run([*command, "format", *common], capture_output=True, timeout=35).returncode
        == 0
    )
    assert path.read_bytes() == formatted
    assert (
        subprocess.run([*command, "check", *common], capture_output=True, timeout=35).returncode
        == 0
    )


@pytest.mark.integration
def test_markdown_missing_tool_never_installs(tmp_path):
    # given
    path = tmp_path / "guide.md"
    path.write_text("# Guide\n")
    before = tree_manifest(tmp_path)
    # when
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(CANDIDATE / "tools/markdown.py"),
            "check",
            str(path),
            "--root",
            str(tmp_path),
            "--doctoc-dir",
            str(tmp_path / "missing"),
        ],
        capture_output=True,
        timeout=35,
    )
    # then
    assert result.returncode == 1
    assert tree_manifest(tmp_path) == before


@pytest.mark.integration
def test_make_owner_paths_overrides_and_safe_default(tmp_path):
    # given
    makefile = CANDIDATE / "Makefile"
    parent = tmp_path / "Makefile"
    parent.write_text(f'all:\n\t$(MAKE) -f "{makefile}" runtime-check PYTHON="{sys.executable}"\n')
    cases = [
        (["make", "runtime-check"], CANDIDATE),
        (["make", "-C", str(CANDIDATE), "runtime-check"], tmp_path),
        (["make", "-f", str(makefile), "runtime-check"], CANDIDATE / "tests"),
        (["make", "-f", str(parent)], tmp_path),
        (["make", "-f", str(makefile)], tmp_path),
    ]
    # when / then
    for argv, cwd in cases:
        result = subprocess.run(
            [*argv, f"PYTHON={sys.executable}"], cwd=cwd, capture_output=True, timeout=10
        )
        assert result.returncode == 0, result.stderr
    missing = subprocess.run(
        ["make", "-f", str(makefile), "runtime-check", "PYTHON=/absent/python"],
        cwd=tmp_path,
        capture_output=True,
        timeout=10,
    )
    assert missing.returncode != 0 and b"No installation" in missing.stderr


@pytest.mark.integration
def test_operational_modes_run_without_site_packages(consumer):
    # given
    command = [
        sys.executable,
        "-S",
        "-B",
        str(CANDIDATE / "tools/framework_check.py"),
        "compose",
        "--consumer-root",
        str(consumer["root"]),
        "--framework-root",
        str(consumer["dep"]),
        "--language",
        "go",
    ]
    before = tree_manifest(consumer["root"])
    # when
    result = subprocess.run(command, capture_output=True, text=True, timeout=35)
    # then
    assert result.returncode == 0, result.stderr
    assert tree_manifest(consumer["root"]) == before
    assert json.loads(result.stdout)["composition"]["commands_executed"] is False


@pytest.mark.integration
def test_snapshot_never_repairs_missing_exclusion_or_replaces_prior_record(consumer):
    # given
    root = consumer["root"]
    directory = root / "ai/artifacts/ticket"
    directory.mkdir(parents=True)
    record = directory / "patch.txt"
    record.write_text("previous evidence\n")
    before = tree_manifest(root)
    # when
    result = subprocess.run(
        [str(CANDIDATE / "scripts/refresh_git_diff.sh"), str(root), "main", "HEAD", str(record)],
        env={**os.environ, "PYTHON": sys.executable},
        capture_output=True,
        text=True,
        timeout=35,
    )
    # then
    assert result.returncode == 1 and "exclusion" in result.stderr
    assert tree_manifest(root) == before


@pytest.mark.integration
def test_non_compose_modes_reject_task_options_before_git_work(consumer):
    # when
    result = invoke(consumer, "integrity", "--require", "unit")
    # then
    assert result.returncode == 2
    assert "compose-only" in result.stderr


@pytest.mark.integration
def test_oversized_git_output_is_bounded_and_sanitized(tmp_path, monkeypatch):
    # given
    fake = tmp_path / "git"
    fake.write_text(f"#!{sys.executable}\nprint('synthetic-secret-' * 10000)\n")
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path))
    # when / then
    with pytest.raises(checker.CheckError, match="bounded output") as failure:
        checker.Git(3).run(tmp_path, "status")
    assert "synthetic-secret" not in str(failure.value)


@pytest.mark.parametrize("defect", ["family", "implementation", "architecture", "api", "test"])
def test_java_catalog_rejects_missing_required_coverage(source_copy, defect):
    # given
    path = source_copy / "catalog.json"
    catalog = json.loads(path.read_text())
    if defect == "family":
        catalog["components"]["java"].remove("rules/java/development.md")
    elif defect == "implementation":
        catalog["routes"]["java"][defect].remove("rules/java/validation.md")
    else:
        del catalog["routes"]["java"][defect]
    path.write_text(json.dumps(catalog))
    # when / then
    with pytest.raises(checker.CheckError, match="(Java route|java rule family)"):
        checker.source_check(source_copy)


@pytest.mark.integration
@pytest.mark.parametrize("style", ["google", "local"])
def test_real_java_routes_preserve_required_subsets_and_style(consumer, style):
    # given
    path = consumer["root"] / "ai/profile.json"
    profile = json.loads(path.read_text())
    profile["styles"] = {"java": style}
    path.write_text(json.dumps(profile))
    implementation = {
        "rules/java/README.md",
        "rules/java/development.md",
        "rules/java/formatting.md",
        "rules/java/validation.md",
    }
    # when
    basic = invoke(consumer, "compose", "--language", "java")
    combined = invoke(
        consumer,
        "compose",
        "--language",
        "java",
        "--boundary",
        "api",
        "--boundary",
        "test",
        "--boundary",
        "architecture",
    )
    # then
    assert basic.returncode == combined.returncode == 0, basic.stderr + combined.stderr
    basic_output = json.loads(basic.stdout)["composition"]
    combined_output = json.loads(combined.stdout)["composition"]
    assert {p for p in basic_output["read"] if p.startswith("rules/java/")} == implementation
    assert {p for p in combined_output["read"] if p.startswith("rules/java/")} == implementation | {
        "rules/java/api-transport.md",
        "rules/java/test.md",
        "rules/java/architecture.md",
    }
    assert combined_output["styles"] == {"java": style}
    assert not any(p.startswith(("rules/go/", "rules/python/")) for p in combined_output["read"])
    assert not combined_output["commands_executed"]


@pytest.mark.integration
def test_go_only_selection_does_not_remove_shared_java_support(consumer):
    # given
    path = consumer["root"] / "ai/profile.json"
    profile = json.loads(path.read_text())
    profile["components"] = ["core", "go"]
    path.write_text(json.dumps(profile))
    before = tree_manifest(consumer["dep"])
    # when
    go = invoke(consumer, "compose", "--language", "go")
    rejected = invoke(consumer, "compose", "--language", "java")
    java_profile = {**profile, "components": ["core", "java"], "styles": {"java": "google"}}
    other = consumer["root"] / "ai/java-profile.json"
    other.write_text(json.dumps(java_profile))
    java = invoke(consumer, "compose", "--profile", "ai/java-profile.json", "--language", "java")
    # then
    assert go.returncode == java.returncode == 0
    assert rejected.returncode == 1 and "not selected" in rejected.stderr
    assert not any("java" in p for p in json.loads(go.stdout)["composition"]["read"])
    assert "rules/java/development.md" in json.loads(java.stdout)["composition"]["read"]
    assert tree_manifest(consumer["dep"]) == before
