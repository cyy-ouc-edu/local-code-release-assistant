#!/usr/bin/env python3
"""Collect local Git context for the Local Code Release Assistant."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Sequence


DEFAULT_MAX_DIFF_CHARS = 80_000


class GitContextError(RuntimeError):
    """Raised when Git context cannot be collected from the requested path."""


def run_git(repository: Path, arguments: Sequence[str]) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), *arguments],
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            text=True,
        )
    except FileNotFoundError as error:
        raise GitContextError("Git is not installed or is not available on PATH.") from error

    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Git command failed."
        raise GitContextError(message)

    return result.stdout


def current_branch(repository: Path) -> str:
    try:
        return run_git(repository, ["symbolic-ref", "--quiet", "--short", "HEAD"]).strip()
    except GitContextError:
        return "DETACHED_HEAD"


def recent_commits(repository: Path) -> list[str]:
    try:
        output = run_git(repository, ["log", "-5", "--oneline"])
    except GitContextError:
        return []
    return [line for line in output.splitlines() if line]


def parse_status(status_output: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for line in status_output.splitlines():
        if len(line) < 4:
            continue
        entries.append(
            {
                "index_status": line[0],
                "worktree_status": line[1],
                "path": line[3:],
            }
        )
    return entries


def collect_context(repository: Path, staged: bool, max_diff_chars: int) -> dict[str, object]:
    root = Path(run_git(repository, ["rev-parse", "--show-toplevel"]).strip())
    diff_arguments = ["diff", "--no-ext-diff"]
    stat_arguments = ["diff", "--stat", "--no-ext-diff"]
    names_arguments = ["diff", "--name-status", "--no-ext-diff"]
    if staged:
        diff_arguments.append("--cached")
        stat_arguments.append("--cached")
        names_arguments.append("--cached")

    diff_output = run_git(root, diff_arguments)
    diff_truncated = len(diff_output) > max_diff_chars
    if diff_truncated:
        diff_output = diff_output[:max_diff_chars]

    status_output = run_git(root, ["status", "--short"])
    name_status = run_git(root, names_arguments)
    return {
        "schema_version": 1,
        "repository": {
            "name": root.name,
            "branch": current_branch(root),
            "scope": "staged" if staged else "working_tree",
        },
        "status": parse_status(status_output),
        "changed_files": [line for line in name_status.splitlines() if line],
        "diff_stat": run_git(root, stat_arguments).strip(),
        "diff": diff_output,
        "diff_truncated": diff_truncated,
        "diff_max_chars": max_diff_chars,
        "recent_commits": recent_commits(root),
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect local Git changes without uploading repository content."
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository directory to inspect (default: current directory).",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Collect only staged changes.",
    )
    parser.add_argument(
        "--max-diff-chars",
        type=int,
        default=DEFAULT_MAX_DIFF_CHARS,
        help=f"Maximum diff characters in the JSON output (default: {DEFAULT_MAX_DIFF_CHARS}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write JSON to this file instead of standard output.",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    if arguments.max_diff_chars < 1:
        print("--max-diff-chars must be greater than zero.", file=sys.stderr)
        return 2

    try:
        context = collect_context(Path(arguments.repo), arguments.staged, arguments.max_diff_chars)
    except GitContextError as error:
        print(f"Unable to collect Git context: {error}", file=sys.stderr)
        return 1

    output = json.dumps(context, ensure_ascii=False, indent=2) + "\n"
    if arguments.output:
        arguments.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
