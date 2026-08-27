# Acceptance Checklist

Run each fixture through `scripts/generate_report.py` and confirm the report:

- names the changed file without an absolute filesystem path;
- includes a risk section and a test-suggestion section;
- gives API compatibility guidance for route changes;
- gives environment validation guidance for configuration changes;
- gives loading, disabled, keyboard, and accessibility guidance for frontend interaction changes;
- includes rollback guidance and open questions;
- marks truncated diffs as incomplete analysis.

The fixtures under `evals/fixtures/` are local test inputs only. Do not package their `.git` directories when publishing the Skill.
