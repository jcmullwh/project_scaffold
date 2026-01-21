## Task

Address additional downstream scaffolder feedback: make generator task commands support placeholder substitution before
writing to `tools/scaffold/monorepo.toml`, reduce friction around CI task enforcement messaging, and add a command to list
scaffolded projects.

## Goal

- Generator task commands recorded in `monorepo.toml` have placeholders resolved (e.g., `__NAME_SNAKE__`, `{name}`,
  `{name_snake}`).
- Missing tools fail loudly but with clear errors and recovery guidance (`--no-install`, `remove`, rerun install).
- Users can list scaffolded projects without opening TOML.

## Context

Downstream notes reported:

- Tasks in `registry.toml` support placeholders for generation, but those placeholders were not being applied to the task
  commands written to `monorepo.toml`, leaving broken paths in recorded tasks.
- CI flag/task mismatch errors were correct but didn't point users at `--allow-missing-ci-tasks`.
- There is no `projects` listing command.

## Constraints

- No silent fallbacks (errors must be clear and actionable).
- Tests run offline (no network; no real external binaries).
- Generated `tools/scaffold/scaffold.py` remains stdlib-only.

## Non-goals

- Not implementing new language templates (Go/Rust/TypeScript) in this change.
- Not changing the trust/vendoring model.
- Not guaranteeing full atomicity of `scaffold add` (manifest vs install), beyond improving recovery and messaging.

## Functional requirements

1) Task command templating:
   - When recording `tasks.*` into `monorepo.toml`, the scaffolder must resolve:
     - copy-generator `substitutions` tokens (e.g., `__NAME_SNAKE__`) and
     - `{...}` placeholders using the scaffolder context (`name`, `name_snake`, `dest_path`, etc.).
   - Unknown placeholders must raise `ScaffoldError` (no silent partial formatting).

2) Project listing:
   - Add `scaffold.py projects` to list projects recorded in `monorepo.toml` in a stable, human-readable format.

3) CI mismatch guidance:
   - When CI-required tasks are missing, the error should mention `--allow-missing-ci-tasks` as an explicit override.

## Testing requirements (pytest, offline)

- Add tests that:
  - prove task placeholder substitution is reflected in `monorepo.toml` for a generated project,
  - validate `scaffold projects` output contains expected project ids,
  - preserve existing tests and keep the suite offline.

## Documentation updates

- Update generated `tools/scaffold/README.md` to document:
  - task placeholder templating + brace escaping guidance,
  - `scaffold projects`.

## Acceptance criteria

- `pdm run pytest` passes.
- A rendered monorepo can:
  - record resolved task commands (no leftover `__NAME_SNAKE__`/`{name_snake}` when used),
  - list projects via `scaffold.py projects`.

## Status

- Implemented; pending review.
