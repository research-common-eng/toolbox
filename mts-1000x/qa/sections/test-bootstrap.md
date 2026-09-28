# Test framework bootstrap

Read AGENTS.md and TESTING.md first. If a test command is documented, use it and skip
bootstrap. Otherwise inspect ecosystem markers and existing test files before suggesting
a runner. A manifest is evidence, not a command to execute blindly.

## B1: Detect existing tests

Check the project's manifests, config, test directories, scripts, and CI. Look for both
runtime markers and actual tests: package.json with test scripts, pytest/unittest, Cargo,
go.mod, Gemfile/spec/test, Maven/Gradle, Composer/PHPUnit, or Mix/ExUnit.

When existing tests are found but their invocation is unclear, ask for or determine the
correct command; do not install a second framework. If no ecosystem is recognizable,
ask for the runtime/test command or let the user choose to skip. Remember a declined
bootstrap in `.mts-1000x/no-test-bootstrap`; don't repeatedly offer it in later runs.

## B2: Research the choice

If there is no framework, consult available current official documentation for the
project's runtime and compare suitable options. If research is unavailable, explain that
and use these starting points, checking versions before installing:

| Runtime | Primary | Alternative |
| --- | --- | --- |
| Ruby/Rails | Minitest + fixtures + Capybara | RSpec + factory_bot |
| Node.js | Vitest + Testing Library | Jest |
| Next.js | Vitest + React Testing Library + Playwright | Jest + Cypress |
| Python | pytest + coverage | unittest |
| Django | pytest + pytest-django | manage.py test |
| Go | standard testing | testify alongside standard testing |
| JVM | JUnit + AssertJ | JUnit |
| Rust | cargo test | mockall for needed isolation |
| PHP | PHPUnit | Pest |
| Elixir | ExUnit | ex_machina fixtures |

## B3: Selection

Offer the primary framework, an alternative, or skip with rationale and exact packages.
A bootstrap decision already authorized need not be asked again. In report-only mode,
record missing tests and offer the plan without installing. Installing test dependencies
belongs to the target project when authorized, never to this skill pack's installer.

## B4: Implement selected setup

Install only the agreed development dependencies using the project's package manager.
Create minimal configuration and fixtures matching its structure. Add a useful smoke
test and test command, avoiding a parallel ecosystem. Document the command in the project's
existing instructions/TESTING.md. Do not rewrite CI during QA bootstrap.

## B5: Verify

Run the documented command. Show what actually passed, failed, or could not start. A
configuration file alone is not a working test framework. Use the verified runner for
regression tests later in the QA workflow. If setup fails, preserve useful diagnostics
and continue browser testing with the test-coverage limitation reported.
