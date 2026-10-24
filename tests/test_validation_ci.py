"""Guard the PR/main validation boundary against silent trigger or check loss."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_validation_workflow_covers_every_pr_and_main_push_with_read_only_permission():
    # given
    workflow = yaml.load(
        (ROOT / ".github/workflows/validation.yml").read_text(), Loader=yaml.BaseLoader
    )

    # when / then
    events = workflow["on"]
    assert {"pull_request", "push"} <= set(events)
    assert events["pull_request"] == {"types": ["opened", "synchronize", "reopened", "edited"]}
    assert events["push"] == {"branches": ["main"]}
    assert workflow["permissions"] == {"contents": "read"}
    assert "validate" in workflow["jobs"]
    job = workflow["jobs"]["validate"]
    assert job["name"] == "Validate framework"
    assert "permissions" not in job
    assert "if" not in job


def test_validation_workflow_runs_pinned_setup_and_required_owners():
    # given
    workflow = yaml.load(
        (ROOT / ".github/workflows/validation.yml").read_text(), Loader=yaml.BaseLoader
    )
    steps = workflow["jobs"]["validate"]["steps"]
    actions = {step["uses"] for step in steps if "uses" in step}
    runs = [step["run"] for step in steps if "run" in step]

    # when / then
    assert actions == {
        "actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803",
        "astral-sh/setup-uv@07a047e608db84b3d8c06cd9a7c7dcc9c355c18e",
        "actions/setup-node@249970729cb0ef3589644e2896645e5dc5ba9c38",
    }
    checkout = next(step for step in steps if step.get("uses", "").startswith("actions/checkout@"))
    assert checkout["with"] == {"fetch-depth": "0", "persist-credentials": "false"}
    assert any(
        "make setup" in run and "make markdown-setup" in run and "make actionlint-setup" in run
        for run in runs
    )
    assert "make check test-collect" in runs
    pr_validation = next(
        step for step in steps if step.get("name") == "Validate pull request squash-message inputs"
    )
    assert pr_validation["if"] == "github.event_name == 'pull_request'"
    assert (
        pr_validation["run"]
        == 'node tools/release-calculation.mjs validate-pr --event-file "$GITHUB_EVENT_PATH"'
    )
    assert any(
        "git ls-files -z -- '*.md'" in run
        and './scripts/markdown.sh check "${markdown_files[@]}"' in run
        for run in runs
    )


def test_root_check_requires_workflow_lint_and_existing_owners():
    # given
    makefile = (ROOT / "Makefile").read_text()

    # when / then
    check_line = next(line for line in makefile.splitlines() if line.startswith("check:"))
    assert {
        "format-check",
        "lint",
        "test-fast",
        "test-integration",
        "source-check",
        "workflow-test",
        "release-test",
    } <= set(check_line.split("##", 1)[0].split()[1:])
    assert "workflow-test: workflow-check" in makefile
