"""Independent executable expectations for the release identity policy scenarios."""

import json
import re
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = json.loads((ROOT / "checks/release-identity-scenarios.json").read_text())
BUILD_VERSION = re.compile(r"git-[0-9a-f]{12}\Z")
FULL_REVISION = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")
IMAGE_DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
VENDOR_FIELDS = (
    "component",
    "release_version",
    "owner",
    "exception_reason",
    "version_source",
    "verification_method",
)


def identity_contract_is_valid(case):
    if case["kind"] == "vendor":
        return all(case.get(field) for field in VENDOR_FIELDS)

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
    image_reference = case.get("image_reference", "")
    image_repository, reference_separator, image_tag = image_reference.rpartition(":")
    image_identity = case.get("image_identity", "")
    identity_repository, identity_separator, identity_digest = image_identity.rpartition("@")
    image_digest = case.get("image_digest", "")
    return bool(
        image_repository
        and reference_separator
        and image_tag
        and image_repository == identity_repository
        and identity_separator
        and IMAGE_DIGEST.fullmatch(image_digest)
        and identity_digest == image_digest
    )


@pytest.mark.parametrize("case", SCENARIOS, ids=[case["id"] for case in SCENARIOS])
def test_release_identity_scenario(case):
    assert identity_contract_is_valid(case) is (case["expected"] == "accept")


def test_first_party_evidence_requires_qualified_identity_for_the_tagged_repository():
    valid = deepcopy(next(case for case in SCENARIOS if case["id"] == "first-party-valid"))
    bare_digest_only = deepcopy(valid)
    bare_digest_only.pop("image_identity")
    wrong_repository = deepcopy(valid)
    wrong_repository["image_identity"] = valid["image_identity"].replace(
        "registry.example.invalid/app@", "registry.example.invalid/other@"
    )

    assert not identity_contract_is_valid(bare_digest_only)
    assert not identity_contract_is_valid(wrong_repository)


@pytest.mark.parametrize("missing", VENDOR_FIELDS)
def test_vendor_exception_requires_complete_scoped_evidence(missing):
    case = deepcopy(next(case for case in SCENARIOS if case["id"] == "vendor-valid"))
    case.pop(missing)

    assert not identity_contract_is_valid(case)


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
