# Architecture Map

This project has two related "repos" in play:

1. The template repo (this repo): contains Cookiecutter templates and tests.
2. The generated monorepo (output of Cookiecutter): contains a small scaffolder CLI (`tools/scaffold/scaffold.py`) and a
   manifest-driven CI/task model.

This document describes the entry points and "source of truth" files for both.

## High-level flow

    Template repo (project_scaffold)
      templates/monorepo-root/
        |
        |  cookiecutter (generation)
        v
    Generated monorepo (<repo_slug>/)
      tools/scaffold/scaffold.py
        |
        |  reads: tools/scaffold/registry.toml  (kinds + generators)
        |  writes: tools/scaffold/monorepo.toml (projects + recorded tasks)
        v
    CI + task execution
      tools/scaffold/ci_matrix.py -> CI matrix
      scaffold.py run <task> -> executes recorded tasks per project

## Two CI layers

This project intentionally has two CI workflow layers:

1. Template repo CI (this repository): `.github/workflows/ci.yml`
2. Generated monorepo CI template: `templates/monorepo-root/{{cookiecutter.repo_slug}}/.github/workflows/ci.yml`

Use template repo CI when changing checks for template source, docs, and template tests.
Use generated monorepo CI when changing how generated repos validate projects recorded in
`tools/scaffold/monorepo.toml`.

## Template Repo (This Repo)

Primary purpose: generate a monorepo template and validate it via offline tests.

Entry points:

- Generate a monorepo from the template:

      cookiecutter templates/monorepo-root -o <output_dir>

- Run the template repo's offline tests (renders the template and exercises the generated scaffolder):

      pdm run pytest

Key files and directories:

- `README.md`: evaluator vs contributor onboarding and quickstart.
- `CONTRIBUTING.md`: template repo development workflow (PDM + local checks).
- `templates/monorepo-root/`: Cookiecutter template root.
- `templates/monorepo-root/cookiecutter.json`: top-level Cookiecutter variables for the generated repo.
- `templates/monorepo-root/{{cookiecutter.repo_slug}}/`: the generated repo content (stored here as template source).
- `tests/test_scaffold_monorepo_template.py`: renders the monorepo template and runs `tools/scaffold/scaffold.py` inside
  the rendered output.
- `.github/workflows/ci.yml`: CI for the template repo itself (ruff/mypy/deptry/pytest).

Note: paths under `templates/` contain literal `{{cookiecutter...}}` placeholder braces because this repo stores
template source. On PowerShell, quote brace-containing paths and use `-LiteralPath` with cmdlets.

## Generated Monorepo (Output Repo)

Primary purpose: be the monorepo a team actually uses day-to-day. It is toolchain-agnostic by recording explicit task
commands per project in a manifest rather than hardcoding toolchains into CI scripts.

Entry points:

- Scaffolder CLI:

      python tools/scaffold/scaffold.py doctor
      python tools/scaffold/scaffold.py add <kind> <project_id> [--generator <generator_id>] [--no-install]
      python tools/scaffold/scaffold.py run <task> --project <project_id>

Key files and directories:

- `README.md`: generated repo overview and golden path.
- `tools/scaffold/scaffold.py`: the stdlib-only scaffolder CLI.
- `tools/scaffold/registry.toml` (registry):
  - Defines `kinds` (apps/libs/etc.), their output directories, and CI expectations.
  - Defines `generators` (how projects are created, which tasks to record).
- `tools/scaffold/monorepo.toml` (manifest):
  - The source of truth for which projects exist and which task commands to run per project.
  - This is what `scaffold.py run ...` and CI read.
- `tools/scaffold/ci_matrix.py`: emits a CI matrix from `monorepo.toml` (used by the generated repo's CI workflow).
- `tools/templates/internal/`: internal templates shipped with the monorepo (some contain literal
  `{{cookiecutter.project_slug}}` placeholders because they are copied without render and used later by `scaffold.py`).
- `tools/templates/vendor/`: vendored external templates (when using `scaffold.py vendor ...`).
- `tools/monorepo_publish/`: snapshot publishing helper for GitLab PyPI (optional; used by the generated workflow).

## Registry vs Manifest (Why Two Files?)

- The registry (`tools/scaffold/registry.toml`) is configuration: it defines what kinds of projects exist and how to
  create them.
- The manifest (`tools/scaffold/monorepo.toml`) is the recorded result: it captures what you created and the exact task
  commands to run for each project.

The scaffolder reads the registry and writes the manifest when you run `scaffold.py add`. The CI workflow reads the
manifest to decide what to run. This design makes runs reproducible and auditable: the manifest is the canonical record
of what happened and what commands are executed.
