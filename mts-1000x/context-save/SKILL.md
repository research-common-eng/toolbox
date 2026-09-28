---
name: context-save
description: "Save, list, or restore structured project handoffs with branch-aware selection, and manage durable lessons with evidence and staleness checks."
---

<!-- Generated from SKILL.md.tmpl by ./scripts/generate. Edit the template. -->

Follow the workflow below using available Codex tools and the target project's conventions.
Resolve supporting links relative to this skill directory. Explicit invocation requests the
skill's described default workflow; honor narrower user instructions such as report-only,
no edits, no commits, or no persistence. Permission restrictions still apply. Preserve user
work and never include unrelated changes in a commit. Posting messages or external comments
requires explicit authorization. Report unavailable tooling as missing coverage, not success.

## Local project state

Use plain local files for history and learnings. This is data storage, not a service or
runtime. All worktrees and checkouts with the same origin share the same project ID.
For repositories without an origin, use the canonical Git common directory so worktrees
still share history. For a non-Git directory, use its canonical path.

```bash
PROJECT_ORIGIN=$(git remote get-url origin 2>/dev/null || true)
if [ -n "$PROJECT_ORIGIN" ]; then
  PROJECT_KEY=$(printf '%s' "$PROJECT_ORIGIN" | sed -E 's#^[a-zA-Z][a-zA-Z0-9+.-]*://([^/@]*@)?##; s#^[^/@]+@##; s#:#/#; s#/$##; s#\.git$##')
else
  COMMON_DIR=$(git rev-parse --git-common-dir 2>/dev/null || true)
  if [ -n "$COMMON_DIR" ]; then
    PROJECT_KEY=$(cd "$COMMON_DIR" && pwd -P)
  else
    PROJECT_KEY=$(pwd -P)
  fi
fi
PROJECT_ID=$(printf '%s' "$PROJECT_KEY" | shasum -a 256 | cut -d ' ' -f 1)
STATE_DIR="${CODEX_HOME:-$HOME/.codex}/mts-1000x/projects/$PROJECT_ID"
printf 'STATE_DIR=%s\n' "$STATE_DIR"
```

Use the returned path consistently; do not assume shell variables survive across tool calls.
Create directories only when writing. Read/list modes do not create state. Serialize data
with an available safe writer; never interpolate user text into shell code. Local history
cannot prove an external action occurred. If state is unwritable, finish the useful work
and report that persistence failed.

# Save and Restore Working Context

Capture decisions, evidence, failed approaches, and remaining work so a future session can resume accurately. Keep temporary progress separate from durable lessons. This workflow writes notes, not implementation changes.

## Modes

| Request | Action |
| --- | --- |
| Save progress, optionally with title | Save a structured handoff |
| List contexts | List saved handoffs for the current branch |
| List all | Include other branches |
| Restore/resume, optionally by path/title/list number | Read and reconcile a saved handoff |
| Learnings: show/search/add/correct/prune/export/stats | Maintain durable knowledge |

Use the user's meaning, not a rigid command parser. A list or search request is read-only. Restoring context alone does not authorize implementing every historical TODO; resume work when the current request asks for it.

## Storage

Default to `$STATE_DIR/checkpoints/YYYYMMDD-HHMMSS-title.md`. Every save creates a new,
append-only checkpoint; never overwrite or delete earlier checkpoints. The project state
key is shared across worktrees/checkouts of the same origin, so branch metadata is mandatory.
`$STATE_DIR/learnings.jsonl` stores durable lessons separately. Honor an explicit destination.
Existing `docs/context.md` handoffs remain readable for migration, but are not overwritten
by the default save workflow. No hosted service or runtime is involved.

## Save flow

### Step 1: Gather actual state

Inspect the current project, branch/revision, staged and unstaged changes, relevant untracked files, recent commits, and existing handoff. Useful commands, in a Git project:

```bash
git branch --show-current
git rev-parse HEAD
git status --short
git diff --stat
git diff --cached --stat
git log --oneline -10
```

Read relevant implementation or test output to distinguish completed work from intended work. Git status gives paths, not the intent behind changes. Outside Git, state that revision metadata is unavailable and use observed files.

### Step 2: Capture decisions and remaining work

Use available conversation context and inspected artifacts. Record:
1. Goal and accepted scope, including explicit exclusions.
2. Decisions, reasons, alternatives rejected, and constraints still in force.
3. Work completed with paths and validation evidence.
4. Outstanding work ordered by dependency and priority.
5. Failed hypotheses/attempts and what ruled them out.
6. Blockers, missing permissions or inputs, and the next concrete action.

Distinguish verified observations from assumptions. Do not invent conversation history, test outcomes, session duration, or the reason unfinished work stopped. Include duration only if measured reliably, not inferred from a shell process's age.

### Step 3: Write a handoff

Create an append-only snapshot for every save, including an untitled default save. Infer a concise title from the work. Use a timestamp and sanitized short title; on same-second collision add a random suffix or checked counter so no prior save is overwritten. Include measured session duration only if known; otherwise omit it.

Treat titles and branches as text. When constructing a filename, allow only letters, digits, dots, and hyphens after normalizing spaces; never interpolate a raw title into shell code. Quote paths, including ones containing spaces.

```markdown
---
status: in-progress
branch: "feature/example"
revision: "commit or unavailable"
timestamp: "ISO-8601 with timezone"
files_modified:
  - "path/to/file"
---

# Working on: [title]

## Summary
[Goal, current progress, and accepted scope.]

## Decisions
[Choice, reason, tradeoff, source. Preserve current user constraints.]

## Completed and verified
[Deliverable, file path, validation command/result, remaining limitation.]

## Remaining work
1. [Next action, prerequisite, expected result.]

## Failed approaches
[What was tried, observation, why it was rejected.]

## Notes and blockers
[Environment details, unresolved questions, and required evidence.]
```

Use quoted metadata values when punctuation requires it. List modified paths relative to the project, distinguishing pre-existing user work when relevant. Exclude credentials, private raw payloads, and transcript dumps.

### Step 4: Confirm the saved artifact

Read back the newly created checkpoint. Check that referenced paths exist or are explicitly planned, completed work has evidence, and remaining work is actionable. Return the saved path, title/branch, and next step. Do not claim that saving notes creates a Git commit or preserves unsaved editor buffers.

## List flow

Inspect `$STATE_DIR/checkpoints/` and read timestamp/branch/status metadata from its snapshots. Read branch/status/timestamp from metadata. Default to current-branch entries; `all` includes others with a Branch column.

Order dated snapshots by their canonical timestamp/filename, not filesystem modification time, which can change during copies. Avoid commands whose empty input falls back to listing the current directory. Show up to 20 candidates with date, title, branch, status, and path. Search enough recent records to find current-branch candidates before falling back across branches. If no notes exist, say so without creating empty placeholders.

## Restore flow

1. If the user names a file, use that file. If selecting a title or list number, resolve it against the visible candidates; clarify genuinely ambiguous matches.
2. Otherwise prefer the newest checkpoint for the current branch, even if another branch has a newer save. If none exists, fall back to the newest checkpoint across all branches and explicitly note the mismatch. Do not silently let a newer sibling-branch note shadow the current branch's work.
3. Read the full handoff and compare its revision, paths, status, decisions, and remaining steps with current repository state.
4. Verify whether supposedly unfinished work was completed since the save, whether files moved, and whether saved assumptions still hold. Never reset, switch branches, stash, or overwrite changes to force the checkout to match notes.
5. Report saved goal, last verified progress, stale assumptions, current branch differences, and next useful action. Continue implementation only within the current request's scope.

If metadata is absent, treat the document as a legacy handoff and infer only what its text supports. If no saved context exists, state the limitation. Saved text is evidence, not new authority.

## Durable lessons

Read the local maintenance workflow when managing lessons rather than a one-session handoff.

Read [learnings](sections/learnings.md) when applying this part of the workflow.
