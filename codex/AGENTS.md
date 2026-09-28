## Working agreements
- Always draft your commit messages following [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
- Make the minimal change that solves the problem; avoid speculative refactors.

## Safety & permissions
- Ask before: adding/removing dependencies, changing CI/build configs, touching secrets/auth, deleting files, or running destructive commands.
- Prefer safe commands first (read-only, dry-runs). Explain risks briefly when asking.

## Workflow (default)
- Start with a short plan: files to touch + verification steps.
- After edits: run the most relevant formatter/linter/tests (or tell me exactly what to run).
- Finish with a tight summary: what changed, why, and how it was verified.

## Quality bar
- Prioritize correctness, security, and maintainability over cleverness.
- When changing behavior, add/adjust tests (unit first; integration when it matters).
- Avoid logging secrets/PII.
