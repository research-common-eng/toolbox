---
name: qa
description: "Systematically test application flows, capture reproducible evidence, compare baselines, and optionally fix and regression-test defects within the requested scope."
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

# QA: Test → Fix → Verify

Test like a real user and connect each defect to reproducible evidence. Use the source when investigating a demonstrated failure or selecting diff-aware coverage. Explicit invocation defaults to test → fix → verify with atomic fix commits. A report-only/no-fix/no-commit request overrides the corresponding default.

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

## Setup and mode resolution

| Parameter | Default | Override |
| --- | --- | --- |
| Target | Known app/preview from project context | Explicit URL |
| Scope | Changed flows when diff-aware; otherwise requested app area | Specific route or feature |
| Depth | Standard | Quick or exhaustive |
| Action | Fix for explicit QA workflow invocation | Report-only for testing-only/no-fix requests |
| Baseline | Fresh run | Prior report/baseline for regression |
| Output | `.mts-1000x/qa-reports/` | User-specified directory |

Quick prioritizes critical/high issues and core smoke coverage. Standard adds medium issues and relevant error/persistence states. Exhaustive adds lower-severity visual polish and broader edge cases within scope. Depth changes severity coverage, not target scope; action mode determines whether fixes are allowed.

Check `git status --porcelain`. For commit-enabled QA, require a clean starting tree: if dirty, present commit-existing-work / stash-and-restore / abort options. Execute only the chosen, authorized action. Do not automatically sweep user work into a QA commit. Report-only or explicitly no-commit QA may run against a dirty tree while recording its baseline. Never confuse pre-existing changes with QA fixes.

Discover the available browser connection or existing project browser-test runner and read its actual API. Reuse the requested tab/browser. Do not install a bundled browser, copy cookies, or assume a particular session. If no browser is available, perform applicable existing tests and report missing interactive coverage.

Use authorized disposable fixtures for actions that create or modify data. Avoid live purchases, destructive production actions, or account changes beyond the task's authorization. Existing authorization carries through the run.

## Test framework

Read [test-bootstrap](sections/test-bootstrap.md) when applying this part of the workflow.

Read the bootstrap section before choosing a runner. Reuse documented test commands; offer setup only if no framework is established. A report-only request does not authorize installing packages.

## Project learnings

Read relevant entries from `$STATE_DIR/learnings.jsonl` and any existing project notes.
Search by component, affected files, and problem type. After naming a concrete hypothesis
or selecting a fix, repeat the search with that specific failure/component keyword.
Missing history is normal. Validate old advice against current code before using it.

When a past learning informs a finding or decision, report: "Prior learning applied:
[key] (confidence N/10, from [date])". Complete the Capture Learnings step at the
end of the workflow for new discoveries. Current user instructions override historical notes.

## Phases 1–6: Baseline

Read and execute the applicable testing mode and phases in the section below. Use supplied acceptance criteria or a prior test plan before guessing from changed file names.

Read [qa-patterns](sections/qa-patterns.md) when applying this part of the workflow.

Complete the baseline before applying fixes so evidence can show what changed.

## Phase 7: Triage

Sort by severity and affected primary flows. Identify reproducibility, confidence, source ownership, and whether the chosen depth includes the issue.

- Report-only: record all observed issues and stop before code mutation.
- Requested fixes: work on issues within scope, in severity order.
- Third-party/infrastructure issues without accessible source: document the owner and verification needed.
- Lower-priority issues outside depth: defer explicitly rather than silently drop them.

A repeated symptom on several pages may be one defect. Preserve each affected path in the same issue. Keep functional and visual consequences distinct in evidence.

## Phase 8: Fix and regression loop

For each issue:

1. **Locate:** Trace the route, component, handler, and data transformation responsible. Search the exact error and relevant names; read callers and existing tests.
2. **Explain:** Establish the cause with the failing state and path. A CSS symptom may originate in missing data; a console error may be a consequence of an earlier failed request.
3. **Fix:** Apply the smallest supported correction. Avoid unrelated refactors and CI edits. Do not alter existing tests to hide a failure; add dedicated regression tests using the project conventions.
4. **Replay:** Repeat the exact original flow. Capture after evidence with the same viewport/data/role, and compare available console/network diagnostics.
5. **Classify:** Verified, best-effort/unverified, reverted, or deferred. Revert a regressing QA fix commit with `git revert <that-fix-sha>`; if working without commits, undo only your own patch. Never revert unrelated user work.
6. **Protect:** Add a regression test when it covers a meaningful behavioral failure, following the guidance below.

### Atomic fix commits

In default commit-enabled QA, commit each focused fix before replaying it. Stage only its changed files and use `fix(qa): ISSUE-NNN — description`. Record the SHA and before/after evidence. A regression is reverted by that exact commit, then marked deferred. Never commit another person's work or combine unrelated fixes. Honor explicit no-commit mode and host permissions.

After a verified behavioral fix, create a separate regression-test commit with `test(qa): regression test for ISSUE-NNN — description` when that commit flow is authorized. Pure CSS changes can use visual replay rather than artificial logic tests.

### Meaningful regression coverage

Read two or three nearby tests to match naming, fixtures, assertion style, setup/cleanup, and runner conventions. Trace the bug's exact precondition, action, and expected result before writing a test.

| Defect | Useful test boundary |
| --- | --- |
| Logic error/exception | Unit test of failing inputs and output |
| Form/API/data flow | Integration test of request, authorization, persistence, and response |
| Interactive component | Component/browser test of action and resulting state |
| Pure CSS/layout | Screenshot/visual replay at affected viewport; no artificial logic test |

Use controlled dependencies where isolation requires them, but do not mock away the failing integration boundary. Tests should fail without the fix where feasible and pass with it. Run the new test file first. If the generated test fails, allow one focused correction; if still failing, defer it and retain the failing output/reproduction in the report. Remove only an unusable test you just generated, never an existing test or evidence of a real regression. If framework exploration exceeds two minutes, defer and record the missing regression coverage. Test commits do not count toward the fix-loop risk heuristic.

For the new test, reproduce the exact precondition/action/result and nearby edge cases. Choose isolated unit tests for logic failures and integration/component tests for their corresponding boundaries. Use incrementing regression filenames if the project uses that convention. Include issue ID, discovery date, and report path in a short regression comment.

### Self-regulation checkpoints

Every five fixes, or after any revert, compute the source workflow's stopping heuristic:
- Each revert: +15 percentage points.
- Each fix touching more than three files: +5.
- After fix 15: +1 per additional fix.
- All remaining issues are low severity: +10.
- Touching unrelated files: +20.

This is a heuristic score, not a measured probability. Above 20, stop the fix loop, show completed work and the remaining issues, and request a continuation decision unless already supplied. Hard cap: 50 fixes per run. Repeated regressions warrant reassessing the cause even below the threshold. A stop does not erase deferred issues or their evidence.

## Phase 9: Final QA

Replay fixed flows and neighboring behavior after the final edit. Run applicable project tests. Recompute observed scores only over comparable coverage. A worse result requires explaining the regression and addressing it within scope.

## Phase 10: Report

Use [the report template](templates/qa-report-template.md), omitting unobserved metrics and unused sections. Include:
- Revision, URL, mode, depth, roles, viewports, routes, and test data.
- Per-issue reproduction and before/after evidence.
- Verified fixes, unverified patches, deferred issues, and files changed.
- Regression test commands/results and missing coverage.
- Baseline comparison with fixed/persistent/new/not-retested issues.
- Readiness assessment based on critical flows and unresolved defects, not score alone.

A useful PR summary: “Tested [flows]; found N issues, verified M fixes; [remaining blocker/coverage gap].” Do not claim a browser test from unit-test evidence.

Save the local report and baseline under `.mts-1000x/qa-reports/` and a project-scoped outcome in `$STATE_DIR/test-outcomes/`, unless persistence is declined. Include verified/best-effort/reverted/deferred counts, files, SHAs, evidence, tests, and before/after scores. Preserve old baselines.

If `TODOS.md` exists, add newly deferred bugs with severity/category/reproduction and annotate fixed matching entries with branch/date. Deduplicate existing items. A report-only request may write report artifacts but must not edit source or TODOs if the user prohibited repository edits. Never post external comments without explicit authorization.

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
