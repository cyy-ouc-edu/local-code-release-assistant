---
name: local-code-release-assistant
description: Generate local Git change summaries, PR descriptions, release notes, risks, test suggestions, and rollback guidance for code delivery. Use when a developer asks to prepare a PR, review pending changes, or write release notes from a repository diff.
---

# Local Code Release Assistant

Prepare a structured delivery report from a local Git repository without uploading repository content.

## Workflow

1. Identify the target repository and whether to inspect all working-tree changes or staged changes only. Ask only when the user's intent cannot be inferred.
2. From this skill's directory, run `scripts/generate_report.py` and pass the target with `--repo`:

   ```bash
   python scripts/generate_report.py --repo /path/to/repository --mode pr --output pr_report.md
   ```

   Add `--staged` when the user asks about staged or commit-ready changes.
3. Select the mode that matches the requested deliverable:
   - `pr` for a pull-request description.
   - `release` for release notes and rollback guidance.
   - `review` for change-review risks and test suggestions.
4. Read the generated Markdown, preserve evidence-based findings, and adapt its wording to the user's requested language or repository conventions.
5. Tell the user where the report was written and call out unresolved questions or truncated analysis.

## Constraints

- Work only with local Git data by default; do not upload source code or credentials.
- Never include environment variables, credentials, or full absolute paths in reports.
- If no changes are found, explain that no report was generated and suggest checking the branch or staged scope.
- Prefer concrete observations from changed files and diff content over generic statements.
- Do not claim that tests passed, deployment succeeded, or rollback is safe unless there is direct evidence.
- If the script cannot run, use `git status --short`, `git diff --stat`, `git diff`, and `git log -5 --oneline` to prepare the same report sections manually.
