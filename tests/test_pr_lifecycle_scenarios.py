"""Independent executable expectations for the pull request lifecycle scenarios."""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = json.loads((ROOT / "checks/pr-lifecycle-scenarios.json").read_text())


def observed_outcome(case):
    if case["kind"] == "merge-gate":
        required = (
            case["merge_authorized"],
            case["squash_enabled"],
            case["review_present"],
            case["review_current"],
            case["checks_pass"],
        )
        dispositions = all(finding["maintainer_disposition"] for finding in case["findings"])
        return "ready" if all(required) and dispositions else "blocked"

    if case["kind"] == "merge-result":
        exact = (
            case["merge_succeeded"]
            and case["subject_matches_title_and_pr"]
            and case["commit_list_matches"]
        )
        return "complete" if exact else "failed"

    if case["kind"] == "branch-cleanup":
        if not case["merge_succeeded"] or not case["message_verified"]:
            return "not-started"
        if not case["handoff_complete"]:
            return "blocked"
        if case["head_state"] == "absent":
            return "complete" if case["branch_absent"] else "incomplete"
        if case["head_state"] != "matching":
            return "blocked"
        complete = case["delete_succeeded"] and case["branch_absent"]
        return "complete" if complete else "incomplete"

    if not case["merge_succeeded"]:
        return "not-started"
    if not case["successor_exists"]:
        return "no-successor"
    complete = (
        case["retarget_succeeded"]
        and case["base_main"]
        and case["parent_diff_absent"]
        and case["checks_inspected"]
    )
    return "complete" if complete else "incomplete"


@pytest.mark.parametrize("case", SCENARIOS, ids=[case["id"] for case in SCENARIOS])
def test_pr_lifecycle_scenario(case):
    assert observed_outcome(case) == case["expected"]


def test_fixture_covers_required_lifecycle_boundaries():
    ids = {case["id"] for case in SCENARIOS}
    assert {
        "high-pending",
        "medium-pending",
        "low-agent-fixed-without-disposition",
        "stale-review",
        "squash-disabled",
        "message-pr-suffix",
        "message-commit-list",
        "branch-cleanup-complete",
        "branch-cleanup-already-absent",
        "branch-cleanup-merge-failed",
        "branch-cleanup-handoff-incomplete",
        "branch-cleanup-head-advanced",
        "branch-cleanup-delete-failed",
        "branch-cleanup-readback-failed",
        "failed-merge-no-retarget",
        "retarget-failed",
        "parent-diff-duplicated",
        "no-successor",
    } <= ids
