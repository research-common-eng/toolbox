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
