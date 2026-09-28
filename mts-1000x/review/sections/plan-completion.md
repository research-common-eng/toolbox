# Plan completion audit

Use the active plan from the conversation first, then relevant repository design docs,
issue/PR acceptance criteria, or an explicitly supplied plan. Verify project and feature
identity before using a discovered document. Commit messages are weaker intent evidence.

Extract actionable requirements: checkboxes, numbered implementation steps, imperative
statements, file specifications, tests, migrations, configuration, and documentation.
Exclude background, unanswered questions, and explicitly deferred work. For a large plan,
group requirements by deliverable; report any portion not inspected.

For each item choose its verification method:
- Code/test/migration in this repository: inspect implementation and relevant tests.
- Content shape: read the document and run an available relevant validator.
- Named deliverable elsewhere: inspect the actual artifact when it is within scope and accessible.
- External configuration/deployment: use an available authorized read-only source or mark unverified.

File existence proves existence only. It does not prove the content or behavior meets the requirement.

| Status | Evidence required |
| --- | --- |
| DONE | Actual requested behavior/deliverable verified |
| PARTIAL | Some required behavior exists; identify missing part |
| NOT DONE | Negative evidence after an applicable check |
| CHANGED | Different implementation demonstrably achieves the goal |
| UNVERIFIABLE | Name the unavailable evidence and check needed |

Example: a migration file can be DONE as a code deliverable while applying it to production
remains UNVERIFIABLE. A parser library does not prove the requested exported document exists.

For discrepancies, read relevant code and history to distinguish deliberate scope cuts,
reverted attempts, dependencies, and misunderstood requirements. Do not invent a reason
such as context exhaustion from missing code alone. Report the requirement, actual result,
evidence, impact, and next check. Record accepted scope changes explicitly.
