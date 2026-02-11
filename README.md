# project-scaffold

This repository is a Cookiecutter template repo. It generates a separate monorepo repository that includes a small
stdlib-only scaffolder CLI (`tools/scaffold/scaffold.py`) for adding projects and running per-project tasks.

## Choose Your Path

### 1) Generate and use a monorepo (recommended for evaluation)

From this repo root (template repo), generate a monorepo into an output directory:

    cookiecutter templates/monorepo-root -o <output_dir>

Cookiecutter will prompt for:

- `repo_slug`: the directory name for the generated repo (for example `my-monorepo`).
- `repo_name`: a display name used in the generated repo docs (defaults to `repo_slug`).

These variables are defined in `templates/monorepo-root/cookiecutter.json`.

Deterministic smoke render (uses template defaults; does not prompt):

    cookiecutter templates/monorepo-root --no-input -o .tmp

Then, in the generated monorepo, run the scaffolder's `doctor` command:

    cd <output_dir>/<repo_slug>
    python tools/scaffold/scaffold.py doctor

Success checkpoint: `doctor` prints `OK` and exits with code 0.

Generated-monorepo docs (as template preview copies in this repo):

- `templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md`
- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md`

Note: paths under `templates/` contain literal `{{cookiecutter...}}` placeholder braces because this repo stores the
template source. On PowerShell, quote brace-containing paths when using them as command arguments.

### 2) Contribute to the template repo (develop templates/tests/CI)

This repo uses PDM for the development environment:

    pdm install

First success test run:

    pdm run pytest

Success checkpoint: pytest passes.

See `CONTRIBUTING.md` for the full local check suite.

Run checks:

    pdm run ruff format --check .
    pdm run ruff check .
    pdm run mypy .
    pdm run deptry .
    pdm run pytest

Planning artifacts live in `.agents/`.
