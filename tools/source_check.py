"""Framework development-only YAML, catalog, adapter and Markdown validation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote

if __package__:
    from .framework_check import CheckError, inside
else:
    from framework_check import CheckError, inside

SKILLS = {
    "ticket-requirements-workflow",
    "ticket-specification-workflow",
    "ticket-implementation-workflow",
    "ticket-post-step-workflow",
    "code-review",
    "pr-description",
}
TEMPLATES = {"requirements", "ticket-content", "delivery-steps", "pr-review", "pr-description"}
IGNORED = {".git", ".venv", ".tools", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache"}


def source_files(root: Path, pattern: str) -> list[Path]:
    return [p for p in root.rglob(pattern) if not set(p.relative_to(root).parts) & IGNORED]


def anchors(body: str) -> set[str]:
    result, counts = set(), {}
    fence = False
    for line in body.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fence = not fence
        if fence:
            continue
        match = re.match(r"^#{1,6}\s+(.*)", line)
        if match:
            slug = re.sub(r"<br\s*/?>", "", match[1].strip().lower())
            slug = re.sub(r"[^\w\-\s]", "", slug).replace(" ", "-")
            count = counts.get(slug, 0)
            counts[slug] = count + 1
            result.add(slug + (f"-{count}" if count else ""))
    return result


def validate_catalog(root: Path) -> dict:
    catalog = json.loads(inside(root, "catalog.json").read_text())
    if (
        not isinstance(catalog, dict)
        or type(catalog.get("version")) is not int
        or catalog["version"] != 1
    ):
        raise CheckError("unsupported catalog version")
    if set(catalog.get("skills", {})) != SKILLS:
        raise CheckError("six-workflow catalog mismatch")
    if set(catalog.get("templates", {})) != TEMPLATES:
        raise CheckError("five-template catalog mismatch")
    components = catalog.get("components")
    routes = catalog.get("routes")
    if not isinstance(components, dict) or not isinstance(routes, dict):
        raise CheckError("invalid catalog components/routes")
    for name, paths in components.items():
        if not isinstance(paths, list) or not paths or len(paths) != len(set(paths)):
            raise CheckError(f"invalid component paths: {name}")
        for path in paths:
            if not inside(root, path).is_file():
                raise CheckError(f"component is not a file: {name}")
    families = {
        "go": {
            f"rules/go/{part}.md"
            for part in (
                "README",
                "development",
                "architecture",
                "api-transport",
                "test",
                "formatting",
                "validation",
            )
        },
        "python": {
            f"rules/python/{part}.md"
            for part in ("README", "development", "test", "formatting", "validation")
        },
    }
    families["java"] = {
        f"rules/java/{part}.md"
        for part in (
            "README",
            "development",
            "architecture",
            "api-transport",
            "test",
            "formatting",
            "validation",
        )
    }
    for name, expected in families.items():
        if set(components.get(name, [])) != expected:
            raise CheckError(f"incomplete {name} rule family")
    mandatory = {
        "consumer.md",
        "rules/core.md",
        "rules/evidence.md",
        "rules/commands.md",
        "rules/agent-security-rules.md",
        "rules/spec-first-rules.md",
        "rules/safety-rules.md",
        "rules/repo-rules.md",
    }
    if not mandatory <= set(components.get("core", [])):
        raise CheckError("missing mandatory core safeguard")
    if not {
        "rules/house.md",
        "rules/git-rules.md",
        "rules/naming-rules.md",
        "rules/makefile-rules.md",
    } <= set(components.get("house", [])):
        raise CheckError("incomplete selected house conventions")
    for name in ("core", "house", "operations"):
        if f"rules/{name}.md" not in components.get(name, []):
            raise CheckError(f"required {name} component missing")
    for language, boundaries in routes.items():
        if not isinstance(boundaries, dict) or not boundaries.get("implementation"):
            raise CheckError("missing implementation route")
        for paths in boundaries.values():
            if (
                not isinstance(paths, list)
                or not paths
                or not set(paths) <= set(components.get(language, []))
            ):
                raise CheckError("route outside selected language component")
    java_routes = {
        "implementation": {
            "rules/java/README.md",
            "rules/java/development.md",
            "rules/java/formatting.md",
            "rules/java/validation.md",
        },
        "architecture": {"rules/java/architecture.md"},
        "api": {"rules/java/api-transport.md"},
        "test": {"rules/java/test.md"},
    }
    for boundary, expected in java_routes.items():
        if set(routes.get("java", {}).get(boundary, [])) != expected:
            raise CheckError(f"incomplete Java route: {boundary}")
    for group in ("skills", "templates"):
        for path in catalog[group].values():
            if not inside(root, path).is_file():
                raise CheckError("missing catalog file")
    return catalog


def check(root: Path) -> dict:
    try:
        import yaml
    except ImportError as error:
        raise CheckError(
            "source mode requires declared PyYAML; run explicit development setup"
        ) from error
    catalog = validate_catalog(root)
    for name, relative in catalog["skills"].items():
        body = inside(root, relative).read_text()
        match = re.match(r"^---\n(.*?)\n---\n", body, re.S)
        try:
            metadata = yaml.safe_load(match[1]) if match else None
        except yaml.YAMLError as error:
            raise CheckError(f"invalid YAML frontmatter: {relative}") from error
        if (
            not isinstance(metadata, dict)
            or metadata.get("name") != name
            or not isinstance(metadata.get("description"), str)
            or not metadata["description"].strip()
        ):
            raise CheckError(f"skill/catalog mismatch: {name}")
    paths = source_files(root, "*.md")
    texts = {p.resolve(): p.read_text() for p in paths}
    count = 0
    for path, body in texts.items():
        if not path.is_relative_to(root):
            raise CheckError("source symlink escapes framework")
        if re.search(r"/home/|services/product-service|templates/go-service|Phase 4|Alloy", body):
            raise CheckError(f"consumer-specific mandate in {path.relative_to(root)}")
        prose = re.sub(r"```.*?```", "", body, flags=re.S)
        for link in re.findall(r"\[[^\]]+\]\(([^)\s]+)\)", prose):
            if re.match(r"^\w+://|^mailto:", link):
                continue
            file, _, anchor = unquote(link).partition("#")
            target = (path.parent / file).resolve() if file else path
            if not target.is_relative_to(root) or not target.exists():
                raise CheckError(f"broken framework link: {path.relative_to(root)}")
            if anchor and target in texts and anchor not in anchors(texts[target]):
                raise CheckError(f"broken framework anchor: {path.relative_to(root)}")
            count += 1
    for client in ("codex", "claude"):
        for name in SKILLS:
            adapter = inside(root, f"adapters/{client}/skills/{name}/SKILL.md.in").read_text()
            if f"name: {name}\n" not in adapter or f"/skills/{name}/SKILL.md" not in adapter:
                raise CheckError(f"adapter/catalog mismatch: {client}/{name}")
            if "{{framework_path}}" not in adapter or "consumer" not in adapter:
                raise CheckError("adapter lacks explicit root binding")
    return {
        "mode": "source",
        "skills": len(SKILLS),
        "templates": len(TEMPLATES),
        "markdown": len(paths),
        "links": count,
        "status": "passed",
    }
