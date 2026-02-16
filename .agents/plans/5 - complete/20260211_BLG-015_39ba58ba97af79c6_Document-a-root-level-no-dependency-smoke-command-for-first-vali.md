# Document a Root-Level No-Dependency Smoke Command for First Validation

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

After this change, the root `README.md` has a prominently placed “fastest smoke” command that a new user can run to validate they are in the correct repo and the template can generate a working monorepo. The smoke path must not require installing this template repo’s development dependencies via `pdm install`.

The smoke path is intentionally minimal: it proves the template renders and the generated scaffolder can run `doctor`. It is not meant to validate every generator/toolchain.

## Progress

- [x] (2026-02-11) Create this ExecPlan from ticket `BLG-015` (fingerprint `39ba58ba97af79c6`).
- [x] (2026-02-11) Decide on a deterministic, safe smoke command sequence that does not require `pdm install`.
- [x] (2026-02-11) Add a prominently labeled “Fastest smoke” section near the top of `README.md` with copy-pasteable commands and a clear success checkpoint.
- [x] (2026-02-11) Ensure the smoke section explicitly labels which working directory each command runs in (template repo vs generated repo).
- [x] (2026-02-11) Validate the smoke commands locally (cookiecutter `--no-input` render + `doctor`).

## Surprises & Discoveries

- Observation: The root `README.md` currently starts with template-repo development instructions (`pdm install`, lint/typecheck/test) and offers no low-friction evaluator smoke path.
  Evidence: `README.md` contains no generation or `scaffold.py doctor` commands.

## Decision Log

- Decision: Use Cookiecutter’s `--no-input` mode to provide a deterministic smoke render into `.tmp/`, then run the generated `scaffold.py doctor`.
  Rationale: `--no-input` avoids interactive prompts and makes the smoke path repeatable; rendering into `.tmp/` keeps the repository clean and easy to delete.
  Date/Author: 2026-02-11 / agent

## Outcomes & Retrospective

- Outcome:
  - `README.md` now includes a “Fastest smoke path” section with a deterministic no-input render and an explicit `doctor` success checkpoint.
  - The smoke path is documented as not requiring `pdm install` (only `cookiecutter` + `python` on PATH).
  - PowerShell and bash one-liner variants are included for copy/paste.

## Context and Orientation

The “no dependency install” requirement is about this template repo’s development dependencies (`pdm install`). The smoke path should only require external tools that an evaluator would already have or can install independently:

- `cookiecutter` on PATH (Cookiecutter CLI)
- `python` on PATH (to run the generated monorepo’s stdlib-only scaffolder)

The Cookiecutter template entry point is `templates/monorepo-root/`. Running Cookiecutter creates a new repo directory (the generated monorepo). The generated monorepo’s scaffolder is `tools/scaffold/scaffold.py`, which provides `doctor`.

## Plan of Work

Edit `README.md` and add a “Fastest smoke (no template-repo dependency install)” section near the top. The section should:

1. State prerequisites plainly: `cookiecutter` and `python` must be on PATH.
2. Provide a short copy-paste command sequence that:
   - renders the monorepo template into a `.tmp/` folder using `--no-input`, and
   - runs `python .tmp/<repo>/tools/scaffold/scaffold.py doctor`.
3. Include a concrete success checkpoint (exit code 0; a short description of expected output).
4. State cleanup instructions (delete `.tmp/`).

If the root README already has a “Quick Start” section from other plans, make “Fastest smoke” either the first subsection under that quick start or a sibling section placed above contributor/dev instructions.

## Concrete Steps

From repo root (`i:\\code\\project_scaffold`):

    # Render deterministically using cookiecutter defaults into .tmp/
    New-Item -ItemType Directory -Force .tmp | Out-Null
    cookiecutter templates/monorepo-root --no-input -o .tmp

    # Run the generated scaffolder’s doctor command.
    python .tmp/my-monorepo/tools/scaffold/scaffold.py doctor

    # Cleanup
    Remove-Item -Recurse -Force .tmp

If `cookiecutter` is not available globally, the same commands can be run via the template repo’s dev environment:

    pdm run cookiecutter templates/monorepo-root --no-input -o .tmp

But the README’s headline smoke path should not require `pdm install`.

## Validation and Acceptance

- `README.md` contains a clearly labeled “Fastest smoke” section near the top.
- The smoke path:
  - does not require running `pdm install`,
  - renders the template into `.tmp/` deterministically (via `--no-input`), and
  - successfully runs `scaffold.py doctor` in the generated repo.
- The docs make the repo-context boundary explicit: generation is run in the template repo; `doctor` is run in the generated repo.

## Idempotence and Recovery

The smoke render writes under `.tmp/`. It is safe to delete `.tmp/` and repeat the process. If Cookiecutter fails partway through, delete `.tmp/` and re-run.

## Artifacts and Notes

Source ticket: `BLG-015`
Fingerprint: `39ba58ba97af79c6`

## Interfaces and Dependencies

No runtime logic changes required. This plan is documentation-only.
