# Baseline testing modes and phases

## Modes

- **Diff-aware:** Trace changed routes, controllers, views/components, model callers, styles, and API consumers. Use accepted test plans or PR criteria before inferring intent from file names. A backend change may affect several pages. Confirm the target app from project instructions or a known preview; do not assume the first responding port is the right app.
- **Full:** Explore reachable in-scope pages, prioritize primary user journeys, then error/empty/persistence states. Do not invent an issue quota or promise exhaustive coverage of an unbounded application.
- **Quick:** Smoke-test the main entry and highest-priority navigation targets, primary interaction, and available console/network diagnostics. State what deeper cases were skipped.
- **Regression:** Read a prior baseline before writing a new artifact. Replay its failing flows plus changed and adjacent flows. A prior issue absent from this run is untested until its reproduction is replayed successfully.

## Phase 1: Initialize

Read [the issue taxonomy](../references/issue-taxonomy.md) and [report template](../templates/qa-report-template.md). Record URL, revision, working-tree state, viewport, user role, test data, mode, and selected scope. Use a distinct run directory under the requested output path or `.mts-1000x/qa-reports/` so a new run cannot overwrite its baseline.

## Phase 2: Authentication

Reuse the requested browser/session or a project test account. Inspect authentication state rather than assuming it. When login needs human action, request it through the available handoff mechanism; do not ask for passwords in chat. Missing access to a role becomes a coverage gap. Do not sign out a personal session just to test a boundary.

## Phase 3: Orient

Navigate to the target and record a baseline screenshot and page state. Identify navigation, forms, primary actions, data displays, and visible loading/error states. Inspect available console/network logs. Establish what success looks like for the core journey before clicking.

Create a route/flow matrix:

| Route/flow | Role/data | Expected outcome | Cases to test | Result/evidence |
| --- | --- | --- | --- | --- |
| Signup | New disposable identity | Account created once | Valid, invalid, duplicate submit | Pending |
| Saved item | Existing test identity | Change survives reload | Edit, navigate back, reload | Pending |

Do not infer application functionality from a screenshot or an HTTP 200 alone.

## Phase 4: Explore

For each in-scope page:
1. Capture layout and inspect overlapping elements, clipping, broken assets, and long content.
2. Exercise links, controls, keyboard navigation, and client-side transitions. Verify destinations and state after action.
3. Test forms with valid data, empty input, invalid formats, boundary lengths, and duplicate submissions when safe.
4. Test loading, empty, error, populated, and overflow states that can be produced with authorized fixtures.
5. Check persistence after reload, back/forward, leaving and returning, and relevant multi-step transitions.
6. Inspect new console exceptions and failed requests. Separate existing background noise from errors caused by the interaction.
7. Inspect responsive layouts and focus/labels for relevant viewport and accessibility requirements.

Observe before acting and re-observe after navigation or significant state changes. Ground selectors in the current page/tool API. Do not paste commands for an unavailable browser library. Preserve stable evidence paths returned by the tool.

## Phase 5: Document reproducible issues

Replay a suspected issue once, when safe, to distinguish deterministic defects from transient infrastructure failures. Intermittent issues need their observed frequency and conditions. Do not discard a real intermittent failure simply because the immediate retry passes.

Each issue gets an ID, severity, category, exact URL/role/viewport, preconditions, ordered actions, expected and actual behavior, and evidence. Use screenshots for visual/state problems; logs, network responses, or reproduction output for nonvisual defects. Redact secrets and private user data.

Save evidence incrementally. For multi-step defects capture the decisive precondition/action/result, not dozens of unrelated screenshots. Consolidate repeated symptoms with the same cause and link affected routes.

## Phase 6: Baseline and regression comparison

Summarize tested routes/roles/states and the highest-impact issues. Use the rubric below for comparable observed categories. A baseline can be stored with this shape:

```json
{
  "schema": 1,
  "date": "ISO-8601",
  "url": "target",
  "revision": "commit",
  "scope": {"routes": [], "roles": [], "viewports": []},
  "observedCategories": [],
  "categoryScores": {},
  "healthScore": null,
  "issues": [{"id": "ISSUE-001", "title": "...", "severity": "high", "category": "functional", "url": "...", "repro": [], "evidence": []}],
  "coverageGaps": []
}
```

Compare old and new issues by route, behavior, and reproduction, not just run-local IDs. Classify fixed, persistent, new, and not retested. Preserve the earlier baseline; do not overwrite it before comparison.

## Health Score Rubric

This is a repeatable prioritization heuristic, not a probability of correctness or an objective product-quality metric. Score only observed categories. Missing console access is unknown, not zero errors. Deduplicate repeated manifestations of the same finding; record the counting rule.

Compute category scores (0-100), then the weighted average over observed categories. Report excluded categories and observed weight. Do not compare scores across different routes, roles, states, or available diagnostics. A broken critical flow blocks a readiness recommendation regardless of score.

### Console (weight: 15%)
- 0 errors → 100
- 1-3 errors → 70
- 4-10 errors → 40
- 11+ errors → 10

### Links (weight: 10%)
- 0 broken → 100
- Each broken link → -15 (minimum 0)

### Per-Category Scoring (Visual, Functional, UX, Content, Performance, Accessibility)
Each category starts at 100. Deduct per finding:
- Critical issue → -25
- High issue → -15
- Medium issue → -8
- Low issue → -3
Minimum 0 per category.

### Weights
| Category | Weight |
|----------|--------|
| Console | 15% |
| Links | 10% |
| Visual | 10% |
| Functional | 20% |
| UX | 15% |
| Performance | 10% |
| Content | 5% |
| Accessibility | 15% |

### Final Score
`score = Σ (category_score × weight)`

---

## Framework-Specific Guidance

### Next.js
- Check console for hydration errors (`Hydration failed`, `Text content did not match`)
- Monitor `_next/data` requests in network — 404s indicate broken data fetching
- Test client-side navigation (click links, don't just `goto`) — catches routing issues
- Check for CLS (Cumulative Layout Shift) on pages with dynamic content

### Rails
- Check for N+1 query warnings in console (if development mode)
- Verify CSRF token presence in forms
- Test Turbo/Stimulus integration — do page transitions work smoothly?
- Check for flash messages appearing and dismissing correctly

### WordPress
- Check for plugin conflicts (JS errors from different plugins)
- Verify admin bar visibility for logged-in users
- Test REST API endpoints (`/wp-json/`)
- Check for mixed content warnings (common with WP)

### General SPA (React, Vue, Angular)
- Inspect interactive page state and exercise client-side navigation; raw HTML links miss client-side routes
- Check for stale state (navigate away and back — does data refresh?)
- Test browser back/forward — does the app handle history correctly?
- Look for accumulating resources or degraded behavior over repeated navigation; console silence alone does not rule out memory leaks

---
