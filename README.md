# project-scaffold

This repository is a Cookiecutter template repo. It generates a separate monorepo repository that includes a small
stdlib-only scaffolder CLI (`tools/scaffold/scaffold.py`) for adding projects and running per-project tasks.

If you are evaluating or adopting the generated monorepo, start with **Quick Start (Generate a Monorepo)** below.

If you are contributing to this template repo (templates/tests/CI), start with **Dev (Template Repo)** and
`CONTRIBUTING.md`.

Generated-monorepo docs (as template preview copies in this repo):

- `templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md`
- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md`

Note: paths under `templates/` contain literal `{{cookiecutter...}}` placeholder braces because this repo stores the
template source. On PowerShell, quote brace-containing paths when using them as command arguments.

## Quick Start (Generate a Monorepo)

From this repo root (template repo), generate a monorepo into an output directory:

    cookiecutter templates/monorepo-root -o <output_dir>

Then, in the generated monorepo, run the scaffolder's `doctor` command:

    cd <output_dir>/<repo_slug>
    python tools/scaffold/scaffold.py doctor

## Dev (Template Repo)

This repo uses PDM for the development environment:

    pdm install

Run checks:

    pdm run ruff format --check .
    pdm run ruff check .
    pdm run mypy .
    pdm run deptry .
    pdm run pytest

See `CONTRIBUTING.md` for details.
