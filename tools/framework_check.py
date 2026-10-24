"""Read-only framework composition and Git dependency checks; standard library only."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

if __package__:
    from .framework_runtime import CheckError, Git, Interrupted, digest, inside, interrupted
else:
    from framework_runtime import CheckError, Git, Interrupted, digest, inside, interrupted


def object_id(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
        raise CheckError("invalid commit identity")
    return value


RELEASE_TAG = re.compile(r"refs/tags/v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")


def release_ref(profile: dict) -> str | None:
    if "upstream_ref" not in profile:
        return None
    ref = profile["upstream_ref"]
    if not isinstance(ref, str) or RELEASE_TAG.fullmatch(ref) is None:
        raise CheckError("upstream_ref must be a canonical release tag ref")
    return ref


def remote_tag(git: Git, root: Path, source: str, ref: str) -> tuple[str, str | None]:
    response = git.run(root, "ls-remote", "--exit-code", "--tags", "--", source, ref, f"{ref}^{{}}")
    rows = [line.split() for line in response.splitlines()]
    if len(rows) == 1 and len(rows[0]) == 2 and rows[0][1] == ref:
        return object_id(rows[0][0]), None
    if (
        len(rows) == 2
        and all(len(row) == 2 for row in rows)
        and rows[0][1] == ref
        and rows[1][1] == f"{ref}^{{}}"
    ):
        tag_object = object_id(rows[0][0])
        peeled = object_id(rows[1][0])
        if tag_object == peeled:
            raise CheckError("selected tag response is ambiguous")
        return peeled, tag_object
    raise CheckError("selected tag response is missing or ambiguous")


def pin(git: Git, root: Path, path: str, commit: str | None) -> str:
    if commit is None:
        lines = git.run(root, "ls-files", "--stage", "--", path).splitlines()
        if len(lines) != 1:
            raise CheckError("missing or unmerged index gitlink")
        metadata, actual = lines[0].split("\t", 1)
        mode, sha, stage = metadata.split()
        if mode != "160000" or stage != "0" or actual != path:
            raise CheckError("missing or unmerged index gitlink")
    else:
        lines = git.run(root, "ls-tree", commit, "--", path).splitlines()
        if len(lines) != 1:
            raise CheckError("missing gitlink in explicit consumer commit")
        metadata, actual = lines[0].split("\t", 1)
        mode, kind, sha = metadata.split()
        if mode != "160000" or kind != "commit" or actual != path:
            raise CheckError("missing gitlink in explicit consumer commit")
    return object_id(sha)


def config(git: Git, root: Path, key: str, *, file: Path | None = None) -> str:
    source = ["--file", str(file)] if file else ["--local"]
    values = git.run(root, "config", *source, "--get-all", key, allowed=(0, 1)).splitlines()
    if len(values) > 1:
        raise CheckError("duplicate configuration values")
    return values[0] if values else ""


def source_contract(
    git: Git, root: Path, dependency: Path, path: str, commit: str | None
) -> tuple[str, str]:
    modules = root / ".gitmodules"
    expected = git.run(root, "show", f"{commit or ''}:.gitmodules")
    if modules.is_symlink() or modules.read_text().strip() != expected:
        raise CheckError("working .gitmodules differs from selected index/commit configuration")
    entries = git.run(
        root, "config", "--file", str(modules), "--get-regexp", r"^submodule\..*\.path$"
    )
    names = [
        line.split()[0][10:-5] for line in entries.splitlines() if line.split(maxsplit=1)[1] == path
    ]
    if len(names) != 1:
        raise CheckError("dependency path must have exactly one .gitmodules owner")
    name = names[0]
    url = config(git, root, f"submodule.{name}.url", file=modules)
    branch = config(git, root, f"submodule.{name}.branch", file=modules)
    if (
        not url
        or url.startswith(("-", "../", "./"))
        or re.search(r"://[^/]*@", url)
        or "?" in url
        or "#" in url
    ):
        raise CheckError("source must be explicit and credential-free")
    if not (
        url.startswith(("https://", "ssh://", "file://", "/"))
        or re.fullmatch(r"git@[A-Za-z0-9.-]+:[A-Za-z0-9_./-]+", url)
    ):
        raise CheckError("unsupported source transport")
    if not branch.startswith("refs/heads/"):
        raise CheckError("configure an explicit refs/heads/ upstream target")
    git.run(root, "check-ref-format", branch)
    for key, expected_value in (("url", url), ("branch", branch)):
        override = config(git, root, f"submodule.{name}.{key}")
        if override and override != expected_value:
            raise CheckError("consumer source/ref override conflicts with .gitmodules")
    if config(git, dependency, "remote.origin.url") != url:
        raise CheckError("submodule origin override conflicts with .gitmodules")
    for owner in (root, dependency):
        overrides = git.run(
            owner,
            "config",
            "--local",
            "--get-regexp",
            r"^(url\..*\.(insteadof|pushinsteadof)|include\..*|includeif\..*|core\.sshcommand|remote\.origin\.uploadpack|http\..*|credential\..*)$",
            allowed=(0, 1),
        )
        if overrides:
            raise CheckError("local transport/source override is unsupported")
    return url, branch


def dependency_check(
    root: Path, dependency: Path, profile: dict, commit: str | None, online: bool, seconds: float
) -> dict:
    git = Git(seconds)
    if Path(git.run(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise CheckError("consumer root must be the checkout root")
    if not (dependency / ".git").exists():
        raise CheckError("dependency is uninitialized; use explicit preparation")
    if Path(git.run(dependency, "rev-parse", "--show-toplevel")).resolve() != dependency:
        raise CheckError("framework root is not an initialized checkout")
    selected = None
    if commit is not None:
        if commit.startswith("-"):
            raise CheckError("invalid explicit commit")
        selected = object_id(
            git.run(root, "rev-parse", "--verify", "--end-of-options", f"{commit}^{{commit}}")
        )
    path = profile["framework_path"]
    expected = pin(git, root, path, selected)
    head = object_id(git.run(dependency, "rev-parse", "HEAD"))
    if head != expected:
        raise CheckError(f"HEAD/pin mismatch: HEAD={head} pin={expected}")
    flags = git.run(dependency, "ls-files", "-v").splitlines()
    if any(line[:1].islower() or line.startswith("S ") for line in flags):
        raise CheckError("framework index flags hide changes; inspect skip/assume flags")
    if git.run(
        dependency, "status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=none"
    ):
        raise CheckError("framework has tracked or non-ignored untracked changes")
    source, branch = source_contract(git, root, dependency, path, selected)
    tag = release_ref(profile)
    ref = tag if tag is not None else branch
    try:
        committed = pin(git, root, path, "HEAD")
    except CheckError:
        committed = None
    result = {
        "mode": "freshness" if online else "integrity",
        "selection": selected or "index",
        "pin": expected,
        "head": head,
        "committed_pin": committed,
        "index_differs_from_committed": selected is None and expected != committed,
        "source_sha256": digest(source.encode()),
        "ref": ref,
        "freshness": "unverified",
    }
    if tag is not None:
        result.update(ref_kind="tag", configured_branch=branch)
    if online:
        if tag is not None:
            upstream, tag_object = remote_tag(git, root, source, ref)
            result["tag_object"] = tag_object
        else:
            response = git.run(root, "ls-remote", "--exit-code", "--refs", "--", source, ref)
            rows = [line.split() for line in response.splitlines()]
            if len(rows) != 1 or len(rows[0]) != 2 or rows[0][1] != ref:
                raise CheckError("upstream ref response is missing or ambiguous")
            upstream = object_id(rows[0][0])
        if upstream != expected:
            raise CheckError(
                f"upstream differs: pin={expected} upstream={upstream}; reviewed update required"
            )
        result.update(upstream=upstream, freshness="passed")
    result["observed_utc"] = datetime.now(UTC).isoformat()
    return result


def load_profile(root: Path, framework: Path, profile_path: str) -> dict:
    profile_file = inside(root, profile_path)
    profile = json.loads(profile_file.read_text())
    if (
        not isinstance(profile, dict)
        or type(profile.get("version")) is not int
        or profile["version"] not in (1, 2)
    ):
        raise CheckError("unsupported or missing profile version")
    if profile["version"] == 1 and "upstream_ref" in profile:
        raise CheckError("upstream_ref requires profile version 2")
    release_ref(profile)
    for key in ("consumer", "framework_path", "artifact_root", "issue_sync"):
        if not isinstance(profile.get(key), str) or not profile[key]:
            raise CheckError(f"missing profile binding: {key}")
    if inside(root, profile["framework_path"]) != framework:
        raise CheckError("explicit framework root differs from profile binding")
    artifact_root = inside(root, profile["artifact_root"], exists=False)
    if artifact_root.is_relative_to(framework) or framework.is_relative_to(artifact_root):
        raise CheckError("artifact root overlaps the framework checkout")
    for key in ("guides", "tool_sources", "components"):
        if (
            not isinstance(profile.get(key), list)
            or not profile[key]
            or not all(isinstance(v, str) for v in profile[key])
        ):
            raise CheckError(f"missing profile binding: {key}")
    for path in profile["guides"] + profile["tool_sources"]:
        bound = inside(root, path)
        if not bound.is_file() or bound.is_relative_to(artifact_root):
            raise CheckError("guide/tool source overlaps artifacts or is not a file")
    if "core" not in profile["components"]:
        raise CheckError("core safeguards are required")
    if __package__:
        from .source_check import validate_catalog
    else:
        from source_check import validate_catalog

    catalog = validate_catalog(framework)
    for name in profile["components"]:
        if name not in catalog["components"]:
            raise CheckError(f"unknown selected component: {name}")
        for path in catalog["components"][name]:
            inside(framework, path)
    if profile.get("conflicts") != "stop-and-report":
        raise CheckError("conflict handling must stop and report")
    commands = profile.get("commands")
    if not isinstance(commands, dict):
        raise CheckError("missing command bindings")
    for name, command in commands.items():
        if (
            not isinstance(command, dict)
            or not isinstance(command.get("argv"), list)
            or not command["argv"]
            or not all(isinstance(v, str) and v for v in command["argv"])
        ):
            raise CheckError(f"invalid command binding: {name}")
        for key in ("owner", "cwd", "prerequisites", "effects", "scope"):
            if not isinstance(command.get(key), str) or not command[key]:
                raise CheckError(f"missing command field: {name}.{key}")
        owner = inside(root, command["owner"])
        if owner.is_relative_to(artifact_root):
            raise CheckError("command source overlaps artifact root")
        if command["cwd"] != "." and not inside(root, command["cwd"]).is_dir():
            raise CheckError("command cwd must be a directory")
    styles = profile.get("styles", {})
    if not isinstance(styles, dict) or any(
        k != "java" or v not in ("google", "local") for k, v in styles.items()
    ):
        raise CheckError("unsupported style selection")
    if styles and "java" not in profile["components"]:
        raise CheckError("style selected without its language component")
    return profile


def installed_clients(
    root: Path,
    framework: Path,
    profile: dict,
    catalog: dict,
    clients: list[str],
    profile_path: str,
) -> dict:
    """Validate rendered routing files, without executing or claiming client discovery."""

    def rendered(client: str, template: str) -> str:
        return (
            inside(framework, f"adapters/{client}/{template}")
            .read_text()
            .replace("{{framework_path}}", profile["framework_path"])
            .strip()
        )

    checked = []
    for client in dict.fromkeys(clients):
        if client not in ("codex", "claude"):
            raise CheckError("unsupported installed client")

        entry = rendered(client, "AGENTS.md.in").replace("ai/profile.json", profile_path)
        if entry not in inside(root, "AGENTS.md").read_text():
            raise CheckError(f"installed {client} root routing missing: AGENTS.md")
        checked.append("AGENTS.md")
        if client == "claude":
            # Preserve local Claude guidance around the standalone import directive.
            if (
                rendered(client, "CLAUDE.md.in")
                not in inside(root, "CLAUDE.md").read_text().splitlines()
            ):
                raise CheckError("installed claude root import missing: CLAUDE.md")
            checked.append("CLAUDE.md")
        directory = ".agents" if client == "codex" else ".claude"
        for name, canonical in catalog["skills"].items():
            relative = f"{directory}/skills/{name}/SKILL.md"
            expected = rendered(client, f"skills/{name}/SKILL.md.in")
            target = f"{profile['framework_path']}/{canonical}"
            if f"Read {target} completely from that root," not in expected:
                raise CheckError(f"adapter template/catalog mismatch: {client}/{name}")
            if inside(root, relative).read_text().strip() != expected:
                raise CheckError(f"installed adapter differs from pinned template: {relative}")
            checked.append(relative)
    return {
        "status": "passed" if clients else "not_checked",
        "clients": list(dict.fromkeys(clients)),
        "files": list(dict.fromkeys(checked)),
    }


def composition(
    root: Path,
    framework: Path,
    profile: dict,
    language: str | None,
    boundaries: list[str],
    capabilities: list[str],
    clients: list[str] | None = None,
    profile_path: str = "ai/profile.json",
) -> dict:
    catalog = json.loads((framework / "catalog.json").read_text())
    selected = list(catalog["components"]["core"])
    for component in profile["components"]:
        if component != "core" and component not in catalog["routes"]:
            selected.extend(catalog["components"][component])
    if boundaries and not language:
        raise CheckError("boundaries require an explicit selected language")
    if language:
        if language not in profile["components"] or language not in catalog["routes"]:
            raise CheckError("requested language is not selected")
        route = catalog["routes"][language]
        selected.extend(route["implementation"])
        for boundary in boundaries:
            if boundary not in route:
                raise CheckError("unknown requested boundary")
            selected.extend(route[boundary])
    for capability in capabilities:
        if capability not in profile["commands"]:
            raise CheckError(f"missing required command capability: {capability}")
        command = profile["commands"][capability]
        executable = command["argv"][0]
        if executable.startswith("-"):
            raise CheckError(f"invalid executable for capability: {capability}")
        if "/" in executable:
            if Path(executable).is_absolute():
                executable_path = Path(executable)
            else:
                cwd = root if command["cwd"] == "." else inside(root, command["cwd"])
                executable_path = inside(root, str((cwd / executable).relative_to(root)))
            available = executable_path.is_file() and os.access(executable_path, os.X_OK)
        else:
            available = shutil.which(executable) is not None
        if not available:
            raise CheckError(
                f"required tool unavailable for capability: {capability}; provision explicitly"
            )
    for path in selected:
        inside(framework, path)
    return {
        "mode": "compose",
        "read": list(dict.fromkeys(selected)),
        "local_guides": profile["guides"],
        "capabilities": capabilities,
        "commands_executed": False,
        "styles": profile.get("styles", {}),
        "installation": installed_clients(
            root, framework, profile, catalog, clients or [], profile_path
        ),
    }


def source_check(framework: Path) -> dict:
    # Lazy development-only import keeps operational modes free of YAML/pytest/Ruff.
    if __package__:
        from .source_check import check
    else:
        from source_check import check

    return check(framework)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("integrity", "freshness", "compose", "source"))
    parser.add_argument("--framework-root", required=True, type=Path)
    parser.add_argument("--consumer-root", type=Path)
    parser.add_argument("--profile", default="ai/profile.json")
    parser.add_argument("--commit")
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--language", choices=("go", "java", "python"))
    parser.add_argument("--boundary", action="append", default=[])
    parser.add_argument("--require", action="append", default=[])
    parser.add_argument("--client", choices=("codex", "claude"), action="append", default=[])
    args = parser.parse_args(argv)
    if args.mode != "source" and args.consumer_root is None:
        parser.error("--consumer-root is required")
    if args.mode != "compose" and (args.language or args.boundary or args.require or args.client):
        parser.error("language/boundary/require/client are compose-only")
    if args.mode == "source" and (args.commit or args.consumer_root):
        parser.error("source mode does not accept consumer/commit selection")
    try:
        Git(args.timeout)  # Validate even modes without Git work.
        framework = args.framework_root.resolve()
        if not framework.is_dir():
            raise CheckError("framework checkout is missing/uninitialized; prepare it explicitly")
        if args.mode == "source":
            result = source_check(framework)
        else:
            root = args.consumer_root.resolve(strict=True)
            if not (framework / ".git").exists():
                raise CheckError("dependency is uninitialized; use explicit preparation")
            profile = load_profile(root, framework, args.profile)
            result = dependency_check(
                root, framework, profile, args.commit, args.mode == "freshness", args.timeout
            )
            if args.mode == "compose":
                result["composition"] = composition(
                    root,
                    framework,
                    profile,
                    args.language,
                    args.boundary,
                    args.require,
                    args.client,
                    args.profile,
                )
            result["profile_sha256"] = digest(inside(root, args.profile).read_bytes())
        print(json.dumps(result, sort_keys=True))
        return 0
    except Interrupted as error:
        print("framework-check: interrupted; no verified result", file=sys.stderr)
        return 128 + int(error.args[0])
    except CheckError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError:
        # Only controlled diagnostics may include context; never echo external output or data.
        error = sys.exception()
        message = str(error) if isinstance(error, CheckError) else "malformed or unavailable input"
        print(f"framework-check: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    raise SystemExit(main())
