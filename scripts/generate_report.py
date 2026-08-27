#!/usr/bin/env python3
"""Generate local code-delivery reports from Git context."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

from collect_git_context import GitContextError, collect_context


MODE_TITLES = {
    "pr": "Pull Request Delivery Report",
    "release": "Release Delivery Report",
    "review": "Change Review Report",
}

CONFIG_MARKERS = ("config", "settings", ".env", "docker", "helm", "yaml", "yml", "toml")
DEPENDENCY_FILES = ("package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "requirements", "poetry.lock", "pyproject.toml")
API_MARKERS = ("api", "route", "router", "controller", "endpoint", "handler")
MIGRATION_MARKERS = ("migration", "migrate", "schema", "database", "db/")
TEST_MARKERS = ("test", "spec", "__tests__")
FRONTEND_MARKERS = ("component", "components", "ui", "page", "pages", "view", "views")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Markdown delivery report from local Git changes."
    )
    parser.add_argument("--repo", default=".", help="Repository directory to inspect.")
    parser.add_argument("--mode", choices=sorted(MODE_TITLES), default="pr")
    parser.add_argument("--staged", action="store_true", help="Analyze staged changes only.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("release_report.md"),
        help="Markdown report path (default: release_report.md).",
    )
    parser.add_argument(
        "--max-diff-chars",
        type=int,
        default=80_000,
        help="Maximum diff characters to inspect (default: 80000).",
    )
    return parser.parse_args()


def file_paths(changed_files: Iterable[str], status: Iterable[dict[str, str]]) -> list[str]:
    paths: list[str] = []
    for entry in changed_files:
        parts = entry.split("\t", maxsplit=1)
        paths.append(parts[-1])
    for entry in status:
        path = entry["path"]
        if path not in paths:
            paths.append(path)
    return paths


def contains_marker(paths: Iterable[str], markers: Iterable[str]) -> bool:
    return any(marker in path.lower() for path in paths for marker in markers)


def changed_file_lines(paths: list[str]) -> list[str]:
    if not paths:
        return ["- No changed files were found in the selected Git scope."]
    visible_paths = paths[:12]
    lines = [f"- `{path}`" for path in visible_paths]
    if len(paths) > len(visible_paths):
        lines.append(f"- ... and {len(paths) - len(visible_paths)} more file(s).")
    return lines


def behavior_lines(paths: list[str]) -> list[str]:
    lines: list[str] = []
    if contains_marker(paths, API_MARKERS):
        lines.append("- API or request-handling files changed; confirm request and response compatibility.")
    if contains_marker(paths, CONFIG_MARKERS):
        lines.append("- Configuration-related files changed; confirm environment-specific values and deployment defaults.")
    if contains_marker(paths, DEPENDENCY_FILES):
        lines.append("- Dependency metadata changed; confirm lockfile consistency and runtime compatibility.")
    if contains_marker(paths, MIGRATION_MARKERS):
        lines.append("- Data or schema-related files changed; confirm migration order, backup, and rollback feasibility.")
    if contains_marker(paths, FRONTEND_MARKERS):
        lines.append("- Frontend interaction files changed; confirm loading, disabled, error, keyboard, and accessibility states.")
    if not lines:
        lines.append("- No high-confidence behavior category was inferred from file paths; review the diff before describing user-facing changes.")
    return lines


def risk_lines(paths: list[str], diff_truncated: bool) -> list[str]:
    lines: list[str] = []
    if contains_marker(paths, API_MARKERS):
        lines.append("- **P1 - Compatibility:** API changes can affect existing clients. Check versioning, validation, and error responses.")
    if contains_marker(paths, CONFIG_MARKERS):
        lines.append("- **P1 - Deployment:** configuration changes can behave differently across environments.")
    if contains_marker(paths, DEPENDENCY_FILES):
        lines.append("- **P1 - Runtime:** dependency changes can introduce build, security, or compatibility regressions.")
    if contains_marker(paths, MIGRATION_MARKERS):
        lines.append("- **P0 - Data:** migration or schema changes need a tested backup and rollback path before release.")
    if contains_marker(paths, FRONTEND_MARKERS):
        lines.append("- **P2 - Interaction:** confirm that UI state changes do not block valid user actions or hide errors.")
    if diff_truncated:
        lines.append("- **P1 - Coverage:** the diff was truncated before analysis; inspect the full diff manually.")
    if not lines:
        lines.append("- **P2 - Review:** no path-based high-risk signal was found. This is not proof that the change is risk-free.")
    return lines


def test_lines(paths: list[str]) -> list[str]:
    lines = ["- Run the repository's existing formatter, linter, type checks, and test suite."]
    if contains_marker(paths, API_MARKERS):
        lines.append("- Exercise affected endpoints for success, validation failure, authorization, and backward-compatible responses.")
    if contains_marker(paths, CONFIG_MARKERS):
        lines.append("- Validate the changed configuration in a non-production environment with representative values.")
    if contains_marker(paths, DEPENDENCY_FILES):
        lines.append("- Reinstall dependencies from a clean environment and run the build or startup command.")
    if contains_marker(paths, MIGRATION_MARKERS):
        lines.append("- Test forward migration and rollback against a disposable copy of representative data.")
    if contains_marker(paths, FRONTEND_MARKERS):
        lines.append("- Verify default, loading, disabled, error, keyboard, and screen-reader behavior in the affected interface.")
    if not contains_marker(paths, TEST_MARKERS):
        lines.append("- No test-file change was detected; confirm whether existing coverage is sufficient or add targeted tests.")
    return lines


def rollback_lines(paths: list[str]) -> list[str]:
    lines = ["- Keep the release tied to a reversible Git commit or deployment artifact."]
    if contains_marker(paths, MIGRATION_MARKERS):
        lines.append("- Do not roll back database code alone; use the verified data rollback plan and confirm backup availability.")
    elif contains_marker(paths, CONFIG_MARKERS):
        lines.append("- Preserve the previous configuration revision so it can be restored with the application version.")
    else:
        lines.append("- If a regression appears, revert the delivery commit and redeploy the previous known-good artifact.")
    return lines


def summary_line(repository: dict[str, str], paths: list[str], mode: str) -> str:
    scope = "staged changes" if repository["scope"] == "staged" else "working-tree changes"
    return (
        f"This {mode} report covers {len(paths)} changed file(s) from {scope} "
        f"on branch `{repository['branch']}` in repository `{repository['name']}`."
    )


def pr_section(paths: list[str]) -> list[str]:
    summary = "Update " + ", ".join(f"`{path}`" for path in paths[:3]) if paths else "No changes detected"
    return [
        "## PR Description",
        "### Summary",
        f"- {summary}",
        "### Testing",
        "- [ ] Relevant checks completed",
        "- [ ] Manual verification completed where applicable",
        "### Reviewer Focus",
        "- Confirm the behavior, compatibility, and rollback assumptions listed above.",
    ]


def release_section(paths: list[str]) -> list[str]:
    changed = ", ".join(f"`{path}`" for path in paths[:5]) if paths else "No changes detected"
    return [
        "## Release Notes",
        f"- Changed: {changed}",
        "- User-visible impact: confirm from the reviewed diff before publishing.",
        "- Deployment note: release only after the recommended checks pass.",
    ]


def build_report(context: dict[str, object], mode: str) -> str:
    repository = context["repository"]
    status = context["status"]
    paths = file_paths(context["changed_files"], status)
    sections = [
        f"# {MODE_TITLES[mode]}",
        "",
        "## Change Summary",
        summary_line(repository, paths, mode),
        "",
        "## Changed Files",
        *changed_file_lines(paths),
        "",
        "## Behavior and Impact",
        *behavior_lines(paths),
        "",
        "## Risks and Attention Points",
        *risk_lines(paths, context["diff_truncated"]),
        "",
        "## Test Suggestions",
        *test_lines(paths),
        "",
        "## Rollback Plan",
        *rollback_lines(paths),
    ]
    if mode in {"pr", "review"}:
        sections.extend(["", *pr_section(paths)])
    if mode == "release":
        sections.extend(["", *release_section(paths)])
    sections.extend(
        [
            "",
            "## Open Questions",
            "- Which user-facing behavior is intentionally changing?",
            "- Which automated and manual checks have been completed?",
            "- Does this change require a coordinated deployment, feature flag, or migration window?",
            "",
            "## Analysis Notes",
            "- This report is generated from local Git metadata and file paths. Confirm all conclusions against the full diff and product context.",
        ]
    )
    return "\n".join(sections) + "\n"


def main() -> int:
    arguments = parse_arguments()
    if arguments.max_diff_chars < 1:
        print("--max-diff-chars must be greater than zero.", file=sys.stderr)
        return 2
    try:
        context = collect_context(
            Path(arguments.repo), arguments.staged, arguments.max_diff_chars
        )
    except GitContextError as error:
        print(f"Unable to generate report: {error}", file=sys.stderr)
        return 1

    if not context["status"] and not context["changed_files"]:
        print("Unable to generate report: no changes found in the selected Git scope.", file=sys.stderr)
        return 1

    arguments.output.write_text(build_report(context, arguments.mode), encoding="utf-8")
    print(f"Report written to {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
