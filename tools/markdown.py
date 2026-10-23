"""Explicit-file Markdown format/check; never download packages during a check."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

from framework_check import CheckError, Git, Interrupted, interrupted


def run_doctoc(files: list[Path], prefix: Path) -> None:
    package = prefix / "node_modules/doctoc"
    if json.loads((package / "package.json").read_text()).get("version") != "2.5.0":
        raise CheckError("doctoc 2.5.0 required; use explicit markdown-setup")
    node = shutil.which("node")
    if node is None:
        raise CheckError("Node unavailable; provision explicitly")
    argv = [
        node,
        str(package / "doctoc.js"),
        "--github",
        "--notitle",
        "--mintocitems",
        "1",
        *map(str, files),
    ]
    with tempfile.TemporaryFile() as output:
        process = subprocess.Popen(
            argv,
            stdin=subprocess.DEVNULL,
            stdout=output,
            stderr=output,
            start_new_session=True,
            env={k: os.environ[k] for k in ("PATH", "HOME") if k in os.environ},
        )
        try:
            if process.wait(timeout=30) != 0:
                raise CheckError("doctoc failed; no successful Markdown result")
        except subprocess.TimeoutExpired as error:
            raise CheckError("doctoc exceeded 30-second work deadline") from error
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=2)


def markdown(mode: str, root: Path, files: list[str], prefix: Path) -> None:
    root = root.resolve(strict=True)
    selected = []
    for name in files:
        path = Path(name)
        requested = path if path.is_absolute() else Path.cwd() / path
        canonical = requested.resolve(strict=True)
        if (
            not canonical.is_relative_to(root)
            or canonical.suffix != ".md"
            or not canonical.is_file()
        ):
            raise CheckError("Markdown selection must be files inside the declared root")
        if requested.is_symlink():
            raise CheckError("select the owned Markdown file directly, not a symlink")
        selected.append(canonical)
    if mode == "format":
        run_doctoc(selected, prefix)
    else:
        with tempfile.TemporaryDirectory(prefix="framework-markdown-") as directory:
            copies = []
            for index, path in enumerate(selected):
                copy = Path(directory) / f"{index}.md"
                copy.write_bytes(path.read_bytes())
                copies.append(copy)
            run_doctoc(copies, prefix)
            if any(a.read_bytes() != b.read_bytes() for a, b in zip(selected, copies, strict=True)):
                raise CheckError("Markdown TOC drift; run format on the selected files")
    print(f"Markdown {mode} passed: {len(selected)} file(s)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("format", "check"))
    parser.add_argument("files", nargs="+")
    parser.add_argument("--root", type=Path)
    parser.add_argument(
        "--doctoc-dir",
        type=Path,
        default=Path(os.environ.get("AI_DOCTOC_DIR", Path(__file__).resolve().parents[1])),
    )
    args = parser.parse_args()
    try:
        root = args.root or Path(Git(5).run(Path.cwd(), "rev-parse", "--show-toplevel"))
        markdown(args.mode, root, args.files, args.doctoc_dir.resolve())
        return 0
    except Interrupted as error:
        return 128 + int(error.args[0])
    except (CheckError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(
            str(error)
            if isinstance(error, CheckError)
            else "Markdown prerequisite unavailable; provision explicitly",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    raise SystemExit(main())
