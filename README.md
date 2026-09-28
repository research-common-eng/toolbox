# Toolbox

- [codex/](codex): Contains a commented Codex configuration reference and an `AGENTS.md` file with working agreements, permission rules, and quality expectations.
- [runpod/](runpod): Provides startup scripts that install development tools such as Codex CLI, uv, and Zsh on Runpod instances. Includes a standalone GitHub App authentication utility for manual repository access.
- [zsh/](zsh): Sets up Zsh with Homebrew packages, aliases, history and completion settings, and a Starship prompt. Includes fzf, zoxide, autosuggestions, and syntax highlighting.

## Development checks

Ruff formats and lints Python, shfmt formats Bash, and ShellCheck checks Bash for common mistakes. Zsh configuration files are checked separately with `zsh -n`.

Install the tools on macOS:

```sh
uv tool install ruff==0.16.6
uv tool install pre-commit==4.6.2
brew install shfmt shellcheck
export PATH="$HOME/.local/bin:$PATH"
```

From the repository root, enable the pre-commit and commit-message hooks and run all file checks:

```sh
pre-commit install
pre-commit run --all-files
```

The hooks install pinned versions of Ruff, shfmt, and ShellCheck in isolated environments. Bash and Zsh must be available on `PATH`. Formatting hooks may edit files; review and stage those changes before committing.

The shared root configuration also checks commit messages with a pinned Conventional
Commits validator at the `commit-msg` stage. Use a message such as
`fix(setup): preserve existing links`. Strict mode requires merge and fixup messages
to follow the format too. These hooks apply to every directory, including `mts-1000x/`.

To format manually:

```sh
ruff check --fix .
ruff format .
shfmt -w runpod/startup.sh zsh/set_up_zsh.sh
```

To check without editing:

```sh
ruff check .
ruff format --check .
shfmt -d runpod/startup.sh zsh/set_up_zsh.sh
shellcheck runpod/startup.sh zsh/set_up_zsh.sh
```

Run the tests separately:

```sh
python3 -m unittest discover -s runpod -p 'test_*.py'
python3 -m unittest discover -s zsh -p 'test_*.py'
```
