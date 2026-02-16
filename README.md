# project-scaffold

This repository is a Cookiecutter template repo. It generates a separate monorepo repository that includes a small
stdlib-only scaffolder CLI (`tools/scaffold/scaffold.py`) for adding projects and running per-project tasks.

## What This Repo Is / Isn't

What this repo is:

- The template source (`templates/monorepo-root`) used to generate a monorepo.
- The place where template maintainers run `pdm` checks and tests.

What this repo is not:

- Not the generated monorepo you work in day-to-day.
- Not the location where `python tools/scaffold/scaffold.py ...` exists and runs.

First success is always a three-step flow:

1. Render the template from this template repo.
2. Change directory into the generated repo.
3. Run `python tools/scaffold/scaffold.py doctor` in the generated repo.

Expected success signal: `doctor` prints `OK` and exits with code `0`.

## Choose Your Path

Architecture and entry points: see `docs/ARCHITECTURE.md`.
Troubleshooting: see `docs/TROUBLESHOOTING.md`.

Recommended defaults:

- Evaluators/integrators/automation smoke checks: use path 1 (`cookiecutter` + `doctor`), because it is the fastest and
  does not require `pdm install`.
- Contributors maintaining this template repo and its CI: use path 2 (`pdm install` + full local checks).

### 1) Generate and use a monorepo (recommended for evaluation and smoke validation)

Deterministic first-success command sequence (template repo -> generated repo):

    cookiecutter templates/monorepo-root --no-input -o .tmp
    cd .tmp/my-monorepo
    python tools/scaffold/scaffold.py doctor

Expected success signal: `doctor` prints `OK` and exits with code `0`.

PowerShell one-liner:

    cookiecutter templates/monorepo-root --no-input -o .tmp; python .tmp/my-monorepo/tools/scaffold/scaffold.py doctor

bash one-liner:

    cookiecutter templates/monorepo-root --no-input -o .tmp && python .tmp/my-monorepo/tools/scaffold/scaffold.py doctor

This path requires:

- `python` on PATH.
- `cookiecutter` on PATH.

Next, in the generated monorepo, scaffold a small stdlib-only project without installs:

    python tools/scaffold/scaffold.py add lib demo-lib --generator python_stdlib_copy --no-install

Generated-monorepo docs (template preview copies in this repo):

- `templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md`
- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md`
- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/SUPPORT_MATRIX.md`

### 2) Contribute to the template repo (recommended for contributors and template CI parity)

This path validates the template-source repository itself.

    pdm install
    pdm run pytest

Expected success signal: pytest passes.

Run the full check suite:

    pdm run ruff format --check .
    pdm run ruff check .
    pdm run mypy .
    pdm run deptry .
    pdm run pytest

See `CONTRIBUTING.md` for details.

## If `pdm install` Hangs on Windows

Failure mode: `pdm install` shows no new output for 5 or more minutes.

Preferred recovery sequence:

    pdm info
    pdm install

If it still hangs and you need first success quickly, use the global-Python smoke path:

    python -m pip install --upgrade pip
    python -m pip install cookiecutter
    cookiecutter templates/monorepo-root --no-input -o .tmp
    python .tmp/my-monorepo/tools/scaffold/scaffold.py doctor

If you already have test dependencies available outside PDM, a minimal fallback test run is:

    python -m pytest -q tests/test_scaffold_monorepo_template.py

This fallback is non-ideal; use it to unblock first validation, then return to the PDM workflow when possible.

## PowerShell Note for `{{cookiecutter...}}` Paths

Paths under `templates/` contain literal `{{cookiecutter...}}` placeholder braces because this repo stores template
source. On PowerShell, use quoted strings and `-LiteralPath` with cmdlets:

    Get-Content -LiteralPath 'templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md' | Select-Object -First 20

See `docs/TROUBLESHOOTING.md` for more PowerShell examples and common recovery paths.

## Two CI Layers

This project has two separate CI workflow layers:

1. Template repo CI (this repo): `.github/workflows/ci.yml`
2. Generated monorepo CI (copied into generated repos): `templates/monorepo-root/{{cookiecutter.repo_slug}}/.github/workflows/ci.yml`

Edit the template repo CI when changing checks for template source code and template tests.
Edit the generated CI template when changing how generated monorepos validate projects from `tools/scaffold/monorepo.toml`.

Planning artifacts live in `.agents/`.
