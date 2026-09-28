# Durable project lessons

Use `$STATE_DIR/learnings.jsonl` as the shared project store. Read existing `docs/learnings.md` for migration or additional context. Read before editing. Keep
patterns, pitfalls, preferences, architecture decisions, and tool behavior separate
from temporary session progress. Do not invent an automatic capture history.

## Show and search

Show the most recent 20 relevant entries grouped by type, or search up to 20 matches for the requested terms and
related component/file names. Give the evidence, date, and applicability. A lack of
matches is a normal result. Listing/searching does not change the file.

## Add

Infer fields already supplied by the user or evidence; ask only for a material omission.

```markdown
### [short-key] — [type] (display format)
- Date: YYYY-MM-DD
- Insight: One concrete reusable lesson.
- Evidence: User statement, observed failure, test, or source path.
- Applicability: Component, conditions, and related files.
- Confidence: Verified / supported / tentative, with reason.
- Exceptions: Where this rule does not apply.
- Supersedes: Earlier entry, if any.
```

Append records with `ts`, `type`, `key`, `insight`, numeric `confidence`, `source`, `skill`, `branch`, `commit`, and `files`; use proper JSON serialization. Latest timestamp wins for identical key/type when showing current entries. Display the structured fields using the Markdown format above.

A stated preference is a preference, not an empirical claim. A single incident is not
a universal rule. Never record credentials or raw conversation dumps.

## Correct and prune

Check referenced files for existence and inspect current behavior. Deleted files can
make an entry stale, but may also have been renamed; search before deleting it. Compare
entries with the same key/type for contradictory guidance. Newer does not automatically
mean correct: compare evidence and current applicability.

For stale or conflicting entries, present remove/keep/update choices unless already resolved by the user. Delete only approved entries; append corrections with the same key/type so the latest entry supersedes the earlier one. Preserve useful exceptions and record what changed. If the user must
choose between conflicting preferences, present the concrete conflict; do not silently
choose. Do not erase all historical evidence merely to make entries consistent.

## Export

Produce Markdown grouped as Patterns, Pitfalls, Preferences, Architecture, Tools, Operational, and Investigations.
Use the requested destination or return the text. Adding lessons to project-wide
instructions changes their reach: only do that when requested, and retain applicability
rather than turning every lesson into an unconditional command.

## Stats

Count current distinct entries by key/type, source, and confidence classification.
Separate active from superseded/stale entries. Report raw entry count, current distinct key/type count, counts by type/source, and mean numeric confidence for current entries. Do not divide by zero for an empty file or fabricate confidence for malformed entries. The count of lessons measures notes, not
team productivity or system correctness.
