#!/usr/bin/env python3
"""Create a small Git repository with an API change for demos."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


BASE_SOURCE = """def list_orders(limit: int) -> dict:
    return {\"items\": [], \"limit\": limit}
"""

CHANGED_SOURCE = """def list_orders(limit: int) -> dict:
    if not 1 <= limit <= 100:
        raise ValueError(\"limit must be between 1 and 100\")
    return {\"items\": [], \"limit\": limit}
"""


def run_git(repository: Path, arguments: list[str]) -> None:
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), *arguments],
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            text=True,
        )
    except FileNotFoundError:
        print("Git is not installed or is not available on PATH.", file=sys.stderr)
        raise SystemExit(1)
    if result.returncode != 0:
        print(result.stderr.strip() or result.stdout.strip(), file=sys.stderr)
        raise SystemExit(result.returncode)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a reproducible demo Git repository.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("demo-repository"),
        help="New demo repository directory (default: demo-repository).",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    output = arguments.output
    if output.exists():
        print(f"Refusing to overwrite existing path: {output}", file=sys.stderr)
        return 1

    source = output / "src" / "routes" / "orders.py"
    source.parent.mkdir(parents=True)
    source.write_text(BASE_SOURCE, encoding="utf-8")
    run_git(output, ["init", "-b", "main"])
    run_git(output, ["add", "."])
    run_git(
        output,
        [
            "-c",
            "user.name=Demo User",
            "-c",
            "user.email=demo@example.invalid",
            "commit",
            "-m",
            "Create orders endpoint",
        ],
    )
    source.write_text(CHANGED_SOURCE, encoding="utf-8")
    print(f"Demo repository created at {output}")
    print("The API validation change is intentionally left unstaged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
