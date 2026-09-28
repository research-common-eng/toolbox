# mts-1000x

Skills for 1000x Member of Technical Staff.

## Install

On macOS or Linux, download this repository, or clone it with Git, then run:

```bash
cd mts-1000x
./setup
```

Setup generates the skills from local templates, then links their folders into `${CODEX_HOME:-$HOME/.codex}/skills`.
Keep the checkout in place. Edit a template and rerun setup to refresh the installed instructions;
rerunning setup is safe. Existing unrelated files or links are never overwritten.
Codex supports ordinary Markdown skills and symlinked skill folders; see the
[official skill documentation](https://learn.chatgpt.com/docs/build-skills).
Restart Codex if the skills do not appear.

```text
$review review the current diff
$qa test http://localhost:3000
$context-save save our current progress
$galaxy-brain-mts investigate this training instability
```

Optional installation controls:

```bash
./setup --dry-run
./setup --project                    # this checkout's .agents/skills
./setup --target /path/to/skills      # custom destination
./setup --uninstall                  # remove this checkout's links only
```

Use the same destination option when uninstalling a project or custom installation.
Uninstall before moving the checkout. Rerunning setup removes obsolete skill links
owned by this checkout.
A conflicting installation is reported with its path; setup leaves it untouched.

## Included skills

| Work | Skills |
| --- | --- |
| Code quality and debugging | `review`, `investigate`, `cso` |
| Python code quality (scaffold) | `py-code-quality` |
| Testing | `qa` |
| Project handoffs and lessons | `context-save` |
| Core AI research and engineering | `galaxy-brain-mts` |

`py-code-quality` is a starter scaffold with no custom workflow yet. Fill in
`py-code-quality/SKILL.md.tmpl`, then run `./scripts/generate` to regenerate its
`SKILL.md`. Run `./setup` to link newly added skills into your installation.

Skills use their folder names directly, such as `$review` and `$qa`. Setup discovers root folders containing
`SKILL.md.tmpl`. These templates are the editable source. Generated `SKILL.md` files
are committed so the distributed instructions can be inspected without running setup.
Do not edit generated files directly: regeneration replaces them.

Rerun `./setup` to migrate this checkout’s old prefixed skill links to the short
names. Setup checks all destination names first and refuses to replace unrelated
entries. Uninstall recognizes both old and new links belonging to this checkout.

QA workflows use an available Codex browser connection or the project's test
runner. Setup installs instructions only. Review, debugging, and
memory workflows use the repository and tools already available to Codex.

`review` defaults to fix-first for explicit workflow invocation. `qa` defaults to
test/fix/verify with atomic commits. Explicit report-only, no-fix, or no-commit requests
override those defaults.
`context-save` creates append-only checkpoints and supports branch-aware restore,
listing, and durable lessons. Project state is stored in plain files under
`${CODEX_HOME:-$HOME/.codex}/mts-1000x/projects/<project-id>/`, shared across worktrees
with the same origin (or canonical Git common directory when no origin exists).
Setup does not create this state; workflows create it as they run.
QA and security reports default to `.mts-1000x/` in the target project.

Galaxy Brain MTS covers model architecture, training, post-training, optimization,
data, evaluations, inference, and research infrastructure. Its automatic scope
excludes ordinary applied-AI product integrations.

## Development

Commit messages must follow [Conventional Commits](https://www.conventionalcommits.org/),
for example `feat: add a skill`, `fix(setup): preserve existing links`, or
`feat!: change skill names`. Allowed types are `build`, `chore`, `ci`, `docs`,
`feat`, `fix`, `perf`, `refactor`, `revert`, `style`, and `test`; scope is optional.

Use the shared configuration and tool installation instructions in the
[repository development guide](../README.md#development-checks). From this
`mts-1000x/` directory, enable both hooks once per checkout:

```bash
(cd .. && pre-commit install)
```

The hook checks messages at the `commit-msg` stage. Strict mode also requires merge
and fixup commit messages to follow the format. This is a development tool only;
skill installation does not require it.

The installer and local generator require Bash, awk, and standard file utilities
(included on macOS and most Linux distributions).
No Python, Node, Bun, network access, upstream checkout, or package installation is
needed to install or regenerate skills. Python 3 is used for development tests and
the pre-commit tooling; initial hook setup downloads its validator dependencies.

```bash
./scripts/generate                 # refresh generated SKILL.md files
./scripts/generate --check         # fail if generated files are stale or missing
./scripts/generate --dry-run       # validate and preview without changing skill files
```

`./setup` runs generation before installing. `--dry-run` previews generation and links;
`--uninstall` removes owned links without regenerating. The generator validates every
template before replacing any generated file. It treats template content as text,
never as shell code.

Template syntax:

| Directive | Expansion |
| --- | --- |
| `{{SKILL_NAME}}` | Skill folder name |
| `{{PREAMBLE}}` | Existing local research-skill guidance |
| `{{WORKFLOW_PREAMBLE}}` | Default workflow behavior and user overrides |
| `{{PROJECT_STATE}}` | Local project state identity and paths |
| `{{WORKFLOW_LEARNINGS}}` | Prior lesson retrieval and attribution |
| `{{LEARNINGS_LOG}}` | Explicit Capture Learnings completion step and local record schema |
| `{{BASE_BRANCH_DETECT}}` | Change-boundary and local-ref guidance |
| `{{LEARNINGS_SEARCH}}` | Reading relevant local project evidence |
| `{{CONFIDENCE_CALIBRATION}}` | Evidence and severity/confidence rules |
| `{{SECTION:name}}` | Link to the skill's local `sections/name.md` |

Block directives occupy their own lines. Shared blocks live in `templates/`;
nested directives in shared blocks are not supported. Unknown directives or missing
section references fail generation. Supporting checklists, report templates, and
specialist references live alongside their owning skill and need no runtime.

Validation:

```bash
/bin/bash -n setup scripts/generate
./scripts/generate --check
python3 -m unittest discover -s tests -v
```

Setup supports macOS and Linux.

## Attribution

The selected workflows and supporting checklists are adapted from Garry Tan's
gstack. The development reference is gstack
1.81.0, revision `0530392821c277b95e5cd65aa9d9fda4248718b2`.
`LICENSE` contains the MIT license for this repository and preserves Garry Tan's
copyright notice for material adapted from gstack. There is no operational dependency on gstack and no synchronization or
updater.

The local adaptations preserve the substantive workflows while replacing host-specific
integration with Codex tools and plain project files:

| Skill | Retained substance |
| --- | --- |
| `review` | Two-pass checklist, independent specialist dispatch, adaptive gating, confidence/quality scoring, fix-first, Greptile triage, design and plan audits, local review history |
| `investigate` | Root-cause investigation, pattern signatures, three-strike and blast-radius gates, focused fix, regression proof, automatic investigation lessons |
| `cso` | Infrastructure-first phases, secrets/supply-chain/CI/integration/AI audits, web-risk checklist, STRIDE, verification and report schema |
| `qa` | Diff-aware/full/quick/regression modes, route-state coverage, issue taxonomy, before/after evidence, fix loop and regression tests |
| `context-save` | Append-only snapshots, shared project storage, branch-aware list/restore, durable lesson maintenance |
| `galaxy-brain-mts` | Existing local AI research principles and experiment workflow |

The five derived workflows (`review`, `investigate`, `cso`, `qa`, and `context-save`)
use the recorded revision above as their alignment reference. Galaxy Brain MTS and
the Python code quality scaffold are local additions.
Installation and execution never fetch, synchronize, or invoke gstack.

Remaining adaptations are explicit:

| Skill | Necessary or retained differences |
| --- | --- |
| `review` | Native Codex subagents replace host-specific dispatch and nested model CLIs; no independent-model guarantee. Local JSONL replaces helper binaries and remote history. Upstream shipping/version-queue integration is absent. |
| `investigate` | Scope restriction is instruction-enforced; no edit hook. Missing checks are reported, and fresh unchanged test results need not be run twice. |
| `cso` | Native subagents and local files replace integrations. No blanket exemption for a particular skill author; credential-bearing URLs and attacker-controlled inputs remain reviewable. Secret values are redacted. |
| `qa` | Available browser APIs replace the bundled browser. User authorization and host permissions govern mutations. Reports disclose missing browser coverage and treat stopping scores as heuristics. |
| `context-save` | Local project IDs replace upstream slugs; legacy local handoffs remain readable. No telemetry-based session-duration estimate or hosted memory. |

No runtime, telemetry, updater, browser daemon, hosted memory service, or external agent
CLI is bundled. Tool-dependent passes report a fallback or missing coverage rather than
pretending to have the original tool. Supporting instructions remain local Markdown.
