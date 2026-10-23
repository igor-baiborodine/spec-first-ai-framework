"""Non-installing development environment identity check."""

import argparse
import importlib.metadata
import platform
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--development", action="store_true")
    args = parser.parse_args()
    if (platform.python_implementation(), platform.python_version()) != ("CPython", "3.14.8"):
        print("CPython 3.14.8 required; run explicit setup", file=sys.stderr)
        return 1
    if args.development:
        for name, expected in {"pytest": "9.1.1", "ruff": "0.17.1", "PyYAML": "6.0.3"}.items():
            try:
                actual = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                actual = "missing"
            if actual != expected:
                print(f"{name} {expected} required; run explicit setup", file=sys.stderr)
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
