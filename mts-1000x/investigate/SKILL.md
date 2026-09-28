---
name: investigate
description: "Investigate bugs through root-cause tracing, pattern analysis, falsifiable hypotheses, focused implementation, and fresh regression verification."
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

# Systematic Debugging

## Iron law

**No fixes without root-cause investigation first.** A patch that merely hides a symptom can leave state corruption or move the failure elsewhere. Establish a testable explanation before changing behavior.

## Project learnings

Read relevant entries from `$STATE_DIR/learnings.jsonl` and any existing project notes.
Search by component, affected files, and problem type. After naming a concrete hypothesis
or selecting a fix, repeat the search with that specific failure/component keyword.
Missing history is normal. Validate old advice against current code before using it.

When a past learning informs a finding or decision, report: "Prior learning applied:
[key] (confidence N/10, from [date])". Complete the Capture Learnings step at the
end of the workflow for new discoveries. Current user instructions override historical notes.

## Phase 1: Root-cause investigation

1. Collect expected and observed behavior, error/stack trace, inputs, environment, and reproduction steps. Ask for missing evidence only when it prevents useful investigation.
2. Trace from the symptom back through callers, data transformations, shared state, and integration boundaries. Find the first incorrect value or violated invariant, not merely the line that throws.
3. Inspect recent changes with `git log --oneline -20 -- <affected-files>` and compare a known-working case. A regression may come from code, configuration, dependencies, data, or an external service; do not assume the code diff is the only source.
4. Reproduce using the actual trigger. If intermittent, record frequency, timing, correlation IDs, concurrency, environment differences, and what is not yet observable.
5. Search existing project lessons and history for the component and failure mode. Repeated bugs in one area can indicate a broken invariant or abstraction boundary.

Keep a compact evidence ledger:

| Observation | Source | What it supports or rules out |
| --- | --- | --- |
| Duplicate event IDs produce two writes | Local reproduction | Handler is not idempotent |
| Single delivery succeeds | Control case | Failure needs duplicate delivery |

State a specific hypothesis: “When X occurs, Y violates invariant Z, producing symptom W.” Label it as unconfirmed until tested.

## Scope discipline

Identify the narrowest affected module and its necessary callers/tests. Keep edits there unless new evidence requires widening scope. Explain why a broader change is necessary. This is an instruction-level scope boundary; there is no hook, freeze daemon, or enforced filesystem lock.

## Phase 2: Pattern analysis

| Pattern | Signature | Inspect |
| --- | --- | --- |
| Race condition | Intermittent, timing-dependent | Shared state, atomicity, uniqueness, retries |
| Null propagation | Missing method/type error | Optional values and validation boundaries |
| State corruption | Partial or contradictory updates | Transactions, callbacks, ordering |
| Integration failure | Timeout/unexpected response | Contract, retry, cancellation, partial success |
| Configuration drift | Works locally, fails elsewhere | Environment, flags, schema/data versions |
| Stale cache | Old data, cache clearing changes result | Cache keys, invalidation, TTL, replicas |

Compare failing and working paths field by field. Check what runs before and after the suspected operation. For distributed failures, locate the earliest boundary where observations diverge.

If a dependency behavior is unclear, use official documentation for the pinned version. Search generic errors and package/version details; strip credentials, customer identifiers, SQL, and internal hostnames from external queries. A reported upstream issue is a candidate explanation, not proof of this failure.

## Phase 3: Hypothesis testing

Before a fix, choose the smallest discriminating test. Vary one factor; hold others fixed. State the predicted outcome if the hypothesis is true and the observation that would disprove it.

Use a temporary assertion, targeted log, controlled fixture, debugger, or minimal reproduction. Keep instrumentation narrow and remove it after use unless it is intentionally part of the delivered fix.

| Hypothesis | Experiment | Prediction | Actual result | Decision |
| --- | --- | --- | --- | --- |
| Duplicate delivery bypasses a state check | Replay same event twice | Two writes before fix | Record observed writes | Confirm or reject |

If evidence contradicts the hypothesis, return to investigation. Do not layer a second speculative patch on the first.

**Three-strike rule:** After three failed hypotheses, stop patching and present the evidence and choices: continue with a specifically described new hypothesis, escalate for domain review, or instrument and wait for a reproduction. A continuation decision already provided by the user remains valid; do not repeat the same approval question. Three failed fixes also trigger an architecture reassessment.

Warning signs: “quick fix for now,” adding a guard without tracing data flow, changing unrelated files to make a test pass, or each patch causing a different failure.

## Phase 4: Implementation

Once evidence supports the cause:
1. Fix the invariant at the appropriate boundary with the smallest justified change.
2. Match existing architecture and error conventions; avoid adjacent refactors.
3. Add regression coverage when it protects the demonstrated failure. Use the exact precondition and assert the correct result, not merely absence of an exception.
4. Where feasible, demonstrate the regression test fails on the unfixed code and passes after the change, using an isolated copy or temporary reversal of only your patch.
5. Run the regression test and the full project test suite when available. If the suite is unavailable, too environment-dependent, or otherwise blocked, name the exact limit and use DONE_WITH_CONCERNS. Reuse fresh results in the report rather than running an unchanged suite twice.
6. Review the diff for leftover logs, accidental edits, weakened assertions, and altered error handling.

**Blast-radius gate:** If the proposed fix touches more than five files, explain why and present proceed/split/rethink options before widening the patch, unless that scope is already explicitly authorized. Track the narrowest affected module as an edit boundary for the investigation. Without host-level edit hooks, this boundary is instruction-enforced; do not claim a filesystem lock.

## Phase 5: Fresh verification and report

Replay the original scenario after the final edit. Check adjacent states that share the repaired path: duplicate requests, null/empty inputs, boundary values, retries, rollback, and cancellation as applicable.

If verification depends on staging or an intermittent event that cannot be reproduced, say exactly what was checked. Distinguish a supported but unverified patch from a confirmed resolution.

```text
DEBUG REPORT
Symptom: observed failure
Root cause: supported explanation and violated invariant
Fix: changed behavior with file:line references
Evidence: reproduction and test command outcomes
Regression coverage: test path, or reason unavailable
Related: prior bugs, accepted scope, architectural follow-up
Status: DONE | DONE_WITH_CONCERNS | BLOCKED
Next check: only if work remains
```

Never say “this should fix it” as evidence. A passed unrelated test is not proof. Append a type=investigation learning to `$STATE_DIR/learnings.jsonl` after the investigation, unless persistence was declined. Include affected files, root-cause key, confirmed insight, confidence, and evidence. DONE requires a confirmed cause, applied fix, regression coverage, and passing available checks; incomplete verification is DONE_WITH_CONCERNS.

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
