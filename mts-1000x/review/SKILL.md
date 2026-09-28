---
name: review
description: "Review a diff for structural correctness, data safety, concurrency, trust boundaries, plan completion, and missing regression coverage."
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

# Pre-Landing Review

Analyze what can fail in the requested change, including structural problems tests may miss. Run a critical pass, relevant specialist passes, and an adversarial recheck. Keep the conclusion grounded in concrete triggers rather than a quota of findings.

## Establish the change boundary

Read `git status --short` and determine whether the request covers staged changes,
uncommitted work, a commit range, or a branch. Include relevant untracked files for
working-tree reviews; `git diff` alone does not include them. Being on the base branch
is not a reason to skip staged or unstaged changes.

For branch work, use the user-specified base or the PR's recorded base when available.
Otherwise inspect `git symbolic-ref refs/remotes/origin/HEAD` and local refs; do not
assume `main`. Compute `git merge-base <base-ref> HEAD`, then compare the requested
scope against that commit. A working-tree diff against the merge base includes local
tracked changes; a three-dot branch diff only covers committed changes.

Use local refs when offline and disclose freshness. Fetching a target project's base
may be useful for a current PR review, but no upstream skill repository is needed.
If the base cannot be identified, use an unambiguous local diff or request the missing
base. Report the exact boundary used and any files or systems outside coverage.

## Step 1: Understand intent and scope drift

Read the user request, PR description if supplied, relevant plan, and commit messages. State the intended behavior and compare it with the changed files. Distinguish unrelated additions, missing work, and deliberate changes of approach.

Read [plan-completion](sections/plan-completion.md) when applying this part of the workflow.

A plan mismatch is informational until it demonstrates a violated requirement. Do not infer that a feature is complete from a touched file, or that external deployment happened because deployment code exists.

## Step 2: Read the checklist and complete diff

Read [checklist.md](checklist.md) before judging the change. If this bundled reference is missing, report the packaging problem and the resulting coverage limit.

Read changed functions in context, their callers, tests, schemas, and configuration. For a new enum/status/tier, search sibling values across the repository and read every relevant consumer, including allowlists, serializers, switches, defaults, and UI options. A new value can work in the dropdown while being rejected or silently discarded by persistence.

## Project learnings

Read relevant entries from `$STATE_DIR/learnings.jsonl` and any existing project notes.
Search by component, affected files, and problem type. After naming a concrete hypothesis
or selecting a fix, repeat the search with that specific failure/component keyword.
Missing history is normal. Validate old advice against current code before using it.

When a past learning informs a finding or decision, report: "Prior learning applied:
[key] (confidence N/10, from [date])". Complete the Capture Learnings step at the
end of the workflow for new discoveries. Current user instructions override historical notes.

## Step 3: Critical pass

Apply the checklist's SQL/data safety, concurrency, model-output trust, command injection, and enum-completeness categories first.

For each candidate, trace the full path:
1. What input or concurrent event triggers it?
2. Which validation or authorization applies before this code?
3. What state changes, and can a failure leave partial effects?
4. What do the caller and user observe?
5. Is the behavior introduced by this diff or pre-existing?

Then apply the remaining categories: async blocking, schema field names, prompt/parser contracts, time windows, boundary coercion, frontend behavior, distribution, and CI. Assess severity from impact, not category membership.

When recommending a framework-specific correction, inspect the pinned version and existing project patterns. Consult official documentation if behavior is uncertain. Do not recommend an API merely because its name looks plausible.

### Optional project diagnostics

If the target project already defines a `slop:diff` or equivalent diff-quality check, run it against the selected base with its installed tools and include results as advisory. Do not install a scanner or treat its absence as a review failure. This is separate from the critical correctness checklist.

## Step 4: Focused specialist passes

Read [specialist dispatch](sections/review-army.md) and run its selection, independent dispatch, merge, and scoring workflow. The table below identifies the local checklists; no separately installed skills or agent CLI is required.

| Pass | When to apply | Reference |
| --- | --- | --- |
| Testing | Changed behavior and regression coverage | [testing](specialists/testing.md) |
| Maintainability | Error handling, state, duplication, dead paths | [maintainability](specialists/maintainability.md) |
| Security | Auth, untrusted inputs, sensitive data | [security](specialists/security.md) |
| Performance | Hot paths, queries, large collections, frontend bundles | [performance](specialists/performance.md) |
| Data migration | Schema changes, backfills, data transformations | [data migration](specialists/data-migration.md) |
| API contract | Public interfaces, payloads, compatibility | [API contract](specialists/api-contract.md) |
| Design | Frontend structure, accessibility states, design-system consistency | [design](design-checklist.md) |
| Simplification | New abstractions or unused flexibility | [simplification](specialists/simplification.md) |
| Red team | Failure-prone boundaries or a requested deep review | [red team](specialists/red-team.md) |

For specialist findings, retain severity, confidence, path, line, category, summary, concrete fix, and evidence. A proposed regression test should establish the failing precondition, perform the action, and assert the intended result.

Dispatch selected specialists independently using available Codex subagent tools when the host permits delegation. If unavailable, apply their checklists locally and report the lost independence. Do not require an extra user request for independent review; it is part of this workflow. Never launch nested agent CLIs.

## Step 5: Adversarial recheck and deduplication

After the specialist merge, run [the adversarial pass](sections/adversarial.md).

Revisit the strongest assumptions with an attacker/chaos-engineering lens: retries, duplicate delivery, cancellation, partial failure, stale cache, resource cleanup, permission changes, empty inputs, and boundary values. Find a counterexample rather than repeating the happy path.

Challenge each candidate with the strongest benign explanation. Read the actual guard or caller that would disprove it. Merge findings with the same root cause across passes; do not report the same missing check as separate security, API, and testing bugs. Preserve distinct downstream impacts in one finding.

## Evidence and confidence

Separate severity (impact) from confidence (strength of evidence). For each finding,
identify the trigger, reachable path, consequence, and code or test evidence. Re-read
callers and existing guards before concluding a defect exists. A pattern match is a
candidate, not a finding. Do not turn missing tooling or untested assumptions into a
clean result. Distinguish verified findings, plausible issues needing confirmation,
and harmless patterns excluded after investigation. Agreement between review passes
is corroboration, not proof; a single demonstrated counterexample is sufficient.

## Step 6: Existing comments, TODOs, and docs

Read [Greptile triage](greptile-triage.md). Fetch line-level and top-level bot comments if the target project has an accessible PR. Apply its suppressions, classifications, escalation detection, and reply templates. This is optional: absence of the integration does not block review. Posting replies requires explicit authorization; otherwise prepare the reply text locally.

Cross-reference existing TODOs and documentation with changed behavior. A code change alone does not prove docs are stale: name the statement that became wrong. Route requested documentation fixes through the same repository conventions.

## Step 7: Fix-first disposition

Default explicit invocation is fix-first, as in the source workflow. If the user instead requests a read-only review, report the same findings and proposed actions without applying them.

Read the Fix-First Heuristic in [checklist.md](checklist.md). Classify every finding:
- AUTO-FIX: mechanical, unambiguous correction within scope.
- ASK: security-sensitive changes, races, product/design decisions, large fixes, enum behavior, functionality removal, or otherwise ambiguous user-visible behavior.
- Advisory simplification and findings with `test_stub` are ASK regardless of other classification.

Apply authorized AUTO-FIX items and report `[AUTO-FIXED] file:line — problem → correction`. Present remaining decisions together, each with severity, concrete trigger, proposed fix, and Fix/Skip choices. Show proposed regression code and path for test-stub items. Respect prior authorization; do not ask again for a decision already made. Apply approved fixes and regression tests, then verify the final diff.

Before output, prove claims: cite the actual safety guard, name the test providing coverage, and give validation command outcomes. Do not call unverified work safe or tested.

## Step 8: Persist the completed review

Append to `$STATE_DIR/review-log.jsonl` after an actual review, unless persistence was declined. Store timestamp, skill, commit, diff boundary, status (`clean` or `issues_found`), unresolved counts, quality score, per-specialist dispatch/finding counts, and per-finding fingerprint/severity/action (`auto-fixed`, `fixed`, `skipped`). Do not record a skipped or failed review as clean.

Use prior records for cross-review deduplication only when the same issue, code context, and disposition still apply; a matching path alone is insufficient. Retain specialist advisory counts for adaptive statistics even though advisories do not reduce quality score.

Output findings/actions, specialist and adversarial results, quality score, plan/TODO/doc gaps, checks run, and missing coverage. This local record replaces upstream review logging; it does not invoke a shipping workflow.

## Capture Learnings

If you discovered a non-obvious pattern, pitfall, or architectural insight during
this session, log it for future sessions in `$STATE_DIR/learnings.jsonl`, unless
the user requested no persistence. This is a completion step, separate from reading
prior learnings. If the workflow exits before meaningful work (for example, a
review with no diff), do not write an entry for work that did not happen.

**Types:** `pattern` (reusable approach), `pitfall` (what NOT to do), `preference`
(user stated), `architecture` (structural decision), `tool` (library/framework insight),
`operational` (project environment/CLI/workflow knowledge). Investigation-specific
root-cause records may additionally use `investigation`.

**Sources:** `observed` (you found this in the code), `user-stated` (user told you),
`inferred` (AI deduction), `cross-model` (independent models agree). Use `cross-model`
only when independent models actually verified the insight; multiple agents using
the same model do not establish cross-model agreement.

**Confidence:** 1–10. Be honest. An observed pattern verified in the code is 8–9.
An uncertain inference is 4–5. An explicitly stated user preference is 10.

**files:** Include specific repository-relative file paths referenced by the learning.
This enables staleness detection if those files are later deleted or changed.

Append one properly serialized JSON object per line. Use the current skill's
frontmatter name for `skill`; record UTC `ts`, `type`, a stable short `key`, concrete
`insight`, numeric `confidence`, `source`, current Git `branch` and `commit` when
available (otherwise null), and `files` as an array. Include evidence and conditions
in the insight so future sessions can assess applicability. Create the state directory
only when writing. Preserve existing records; the latest record with the same
key/type supersedes earlier records at read time. Never interpolate insight text
as shell code, store secrets, or claim a write succeeded without checking it.

**Only log genuine discoveries.** Don't log obvious things or things the user
already knows. Ask: would this insight save time in a future session? If yes, log it.
Do not manufacture a lesson just to complete this step.
