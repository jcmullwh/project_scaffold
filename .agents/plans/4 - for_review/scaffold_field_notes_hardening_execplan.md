# Incorporate downstream scaffold field notes (hardening + user docs)

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and
`Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

Downstream users exercised `project_scaffold` by generating a monorepo and adding a mix of projects (PDM/uv/Node/Terraform,
vendored Cookiecutter templates). They reported a set of sharp edges: missing tool detection surfacing late, install
failures leaving the project recorded in the manifest, and lack of a `remove/unregister` workflow for recovery.

This change set makes those failure modes easier to understand and recover from, without turning the notes into mandates:

- improve missing-tool errors (raise `ScaffoldError` instead of `FileNotFoundError` tracebacks)
- add a preflight check for the install tool when `scaffold add` will run install (fail early; suggest `--no-install`)
- add a `scaffold remove` command to unregister a project (optional directory delete with explicit confirmation)
- incorporate the notes into `.agents/user_info/users.md` (intent + personas + missions + open questions)

## Progress

- [x] (2026-01-20) Create this ExecPlan and keep it updated.
- [x] (2026-01-20) Update generated `tools/scaffold/scaffold.py` (preflight + remove + clearer missing-tool errors).
- [x] (2026-01-20) Update generated scaffold docs to document recovery workflows and common gotchas.
- [x] (2026-01-20) Update `.agents/user_info/users.md` to incorporate the new field notes.
- [x] (2026-01-20) Add/adjust offline tests and run `pdm run pytest`.

## Surprises & Discoveries

- Observation: Local dev lint/typecheck can be polluted by untracked generated monorepo content in the repo root.
  Evidence: `pdm run pytest` passes; `pdm run ruff check .` and `pdm run mypy .` reported errors under an untracked
  `services/` tree.

## Decision Log

- Decision: Treat downstream notes as inputs, not mandates; implement only high-signal, low-risk mitigations.
  Rationale: Keep the system generic and avoid overfitting to one user’s run while still reducing common failure modes.
  Date/Author: 2026-01-20 / agent

- Decision: Convert missing-command `FileNotFoundError` into `ScaffoldError` in the generated scaffolder.
  Rationale: Users should get a clear, actionable error message instead of a Python traceback for common PATH issues.
  Date/Author: 2026-01-20 / agent

- Decision: Add `scaffold remove <project_id>` with optional `--delete-dir --yes`.
  Rationale: Downstream runs commonly need a recovery path to unregister projects (and sometimes clean their directories)
  without manual TOML editing.
  Date/Author: 2026-01-20 / agent

- Decision: Preflight only the install tool for `scaffold add` (when install will run).
  Rationale: Catch the most common "tool missing on PATH" failure mode early without overreaching into generator-specific
  behavior.
  Date/Author: 2026-01-20 / agent

## Outcomes & Retrospective

- Outcome:
  - Generated scaffolder hardening:
    - `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/scaffold.py` catches missing commands as
      `ScaffoldError`, preflights install tool availability for `add`, and adds a `remove` command.
  - Generated docs:
    - `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md` documents `--no-install`, `remove`,
      and PowerShell `--vars` quoting.
  - Repo user notes:
    - `.agents/user_info/users.md` incorporates the new downstream notes (missing tools, interactive generators,
      recovery, PowerShell quoting, per-project lockfiles, CI/task enforcement).
  - Tests:
    - `tests/test_scaffold_monorepo_template.py` adds coverage for `remove`, install-tool preflight, and missing-command
      error shape; `pdm run pytest` passes offline.

## Context and Orientation

Key files:

- `.agents/user_info/users_template.md`: canonical user-notes template (must not be edited as part of this work).
- `.agents/user_info/users.md`: repo-specific user-notes document to update with downstream field notes.
- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/scaffold.py`: the generated monorepo’s stdlib-only
  scaffolder CLI (add/run/doctor/vendor).
- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md`: generated docs for the scaffolder CLI.
- `tests/test_scaffold_monorepo_template.py`: offline tests that render the monorepo template and exercise `scaffold.py`.

## Plan of Work

1) Make missing-tool failures explicit and clean:
   - In `_run(...)`, catch `FileNotFoundError` (and similar OS errors) and raise `ScaffoldError` with a clear message.

2) Add a preflight check for `scaffold add` installs:
   - If `--no-install` is not set and the selected generator defines `tasks.install`, check that the install tool exists
     on PATH before generating and writing to the manifest. If missing, raise a `ScaffoldError` suggesting `--no-install`.

3) Add `scaffold remove`:
   - Remove a project entry from `tools/scaffold/monorepo.toml`.
   - Optionally delete the project directory with `--delete-dir --yes`.
   - Keep behavior loud and safe: validate ids, validate paths are inside repo root, print explicit output.

4) Update docs and repo user notes:
   - Document the recovery path for partial adds (re-run install, or unregister with remove).
   - Capture the new downstream notes in `.agents/user_info/users.md` (missing tools, interactive generators, PowerShell
     quoting, per-project lockfiles, and CI/task enforcement gotchas).

5) Add tests and validate:
   - Add a test for `scaffold remove`.
   - Add a test that missing tools produce `ERROR: Required command not found on PATH` (no traceback).
   - Run `pdm run pytest` (offline).

## Concrete Steps

From repo root (`i:\\code\\project_scaffold`):

    pdm run pytest

## Validation and Acceptance

- Tests: `pdm run pytest` passes offline.
- Rendered monorepo: `tools/scaffold/scaffold.py remove <id>` removes the project from `monorepo.toml`; with
  `--delete-dir --yes` also removes the directory.
- Error behavior: running a task whose command is missing fails with a `ScaffoldError` message, not a Python traceback.

## Idempotence and Recovery

- `scaffold remove` without `--delete-dir` is safe to retry; it should be idempotent if the project is already absent
  (expect an error unless explicitly designed otherwise).
- `scaffold remove --delete-dir` is destructive; require `--yes` to proceed.

## Artifacts and Notes

- This plan lives at `.agents/plans/4 - for_review/scaffold_field_notes_hardening_execplan.md`.

## Interfaces and Dependencies

- No new third-party runtime dependencies: generated `tools/scaffold/scaffold.py` remains stdlib-only.
- Tests remain offline and do not require external binaries beyond those already used in the suite (`git` is optional via
  existing skip markers).
