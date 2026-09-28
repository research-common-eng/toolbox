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
