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
