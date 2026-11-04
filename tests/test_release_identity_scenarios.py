"""Independent executable expectations for the release identity policy scenarios."""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = json.loads((ROOT / "checks/release-identity-scenarios.json").read_text())
BUILD_VERSION = re.compile(r"git-[0-9a-f]{12}\Z")
FULL_REVISION = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")
IMAGE_DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")


def identity_contract_is_valid(case):
    if case["kind"] == "vendor":
        return all(case.get(field) for field in ("release_version", "owner", "verification_source"))

    revision = case.get("source_revision", "")
    build_version = case.get("build_version", "")
    if not FULL_REVISION.fullmatch(revision) or not BUILD_VERSION.fullmatch(build_version):
        return False
    if build_version == "git-000000000000" or build_version != f"git-{revision[:12]}":
        return False
    if case.get("oci_revision") != revision:
        return False
    if any(
        case.get(field) != build_version
        for field in ("oci_version", "kubernetes_version", "service_version")
    ):
        return False
    return bool(IMAGE_DIGEST.fullmatch(case.get("image_digest", "")))


@pytest.mark.parametrize("case", SCENARIOS, ids=[case["id"] for case in SCENARIOS])
def test_release_identity_scenario(case):
    assert identity_contract_is_valid(case) is (case["expected"] == "accept")


def test_fixture_covers_required_policy_boundaries():
    assert {case["id"] for case in SCENARIOS} == {
        "first-party-valid",
        "vendor-valid",
        "wrong-format",
        "revision-mismatch",
        "cross-surface-mismatch",
        "placeholder-deployed",
        "tag-only-image",
    }
