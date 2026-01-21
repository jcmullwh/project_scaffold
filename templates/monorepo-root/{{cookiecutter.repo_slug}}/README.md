# {{ cookiecutter.repo_name }}

This monorepo was generated from a Cookiecutter template.

## Scaffold tool

This repo includes `tools/scaffold/scaffold.py`, a small Python CLI that:

- adds new projects based on a configurable registry (`tools/scaffold/registry.toml`)
- records created projects in a manifest (`tools/scaffold/monorepo.toml`)
- runs explicit per-project tasks from the manifest (no toolchain assumptions)

## Golden path

List what you can scaffold, then create a project and run its tasks:

    python tools/scaffold/scaffold.py doctor
    python tools/scaffold/scaffold.py kinds
    python tools/scaffold/scaffold.py generators
    python tools/scaffold/scaffold.py add app billing-api
    python tools/scaffold/scaffold.py add app billing-api --dry-run
    python tools/scaffold/scaffold.py run test --project billing-api

The manifest at `tools/scaffold/monorepo.toml` is the source of truth for what projects exist and what tasks they run.

## PDM generators

This monorepo template includes monorepo-safe PDM-based generators:

    python tools/scaffold/scaffold.py add lib my-lib --generator python_pdm_lib --no-install
    python tools/scaffold/scaffold.py add app my-app --generator python_pdm_app --no-install

These generators require `pdm` on PATH to run `install`/`lint`/`test` tasks.

## Other generators

- Poetry (Python): `python_poetry_app`
- uv (Python): `python_uv_app`
- Vite (Node): kind `web` defaults to `node_vite`
- Go (stdlib): `go_stdlib_lib`
- Rust (Cargo): `rust_cargo_lib`
- TypeScript (Node): `node_typescript_lib`

Examples:

    python tools/scaffold/scaffold.py add app my-poetry-app --generator python_poetry_app --no-install
    python tools/scaffold/scaffold.py add app my-uv-app --generator python_uv_app --no-install
    python tools/scaffold/scaffold.py add web my-site --no-install
    python tools/scaffold/scaffold.py add lib my-go-lib --generator go_stdlib_lib --no-install
    python tools/scaffold/scaffold.py add lib my-rust-lib --generator rust_cargo_lib --no-install
    python tools/scaffold/scaffold.py add lib my-ts-lib --generator node_typescript_lib --no-install

Note: some command-based generators (for example `node_vite`) may require network access the first time they run (because
`npm create ...@latest` can fetch packages).

## Requirements

- Always: `python` (Python 3.11+ recommended).
- For Cookiecutter generators: `cookiecutter`.
- For external templates and vendoring: `git`.

See `tools/scaffold/README.md` for details.

## Registry vs manifest

- Registry = `tools/scaffold/registry.toml`. Defines project kinds (apps/libs/etc.) and generators (how to create a
  project).
- Manifest = `tools/scaffold/monorepo.toml`. Lists the projects that exist and the task commands to run for each project.

The monorepo stays toolchain-agnostic by recording explicit task commands (for example `tasks.test = ["pytest", "-q"]` or
`tasks.build = ["npm", "run", "build"]`) instead of hardcoding Poetry/PDM/npm in CI scripts.

## Internal templates

This repo includes internal templates under `tools/templates/internal/`.

These are intentionally copied without render as part of the initial monorepo Cookiecutter run, so you will see literal
`{% raw %}{{cookiecutter.project_slug}}{% endraw %}` placeholders inside them. They are used later by
`tools/scaffold/scaffold.py add ...`.

## External templates, trust, and vendoring

Cookiecutter templates can execute code via hooks. For safety, registry entries for external templates should be pinned to
a specific git ref and default to untrusted.

- To run an untrusted external generator once: re-run `scaffold add ...` with `--trust`.
- To vendor a template into this repo (recommended for long-lived use):

    python tools/scaffold/scaffold.py vendor import <generator_id> --as <vendored_id>

## CI

The centralized GitHub Actions workflow at `.github/workflows/ci.yml`:

- builds a project matrix from `tools/scaffold/monorepo.toml` via `tools/scaffold/ci_matrix.py`
- runs `scaffold.py doctor`, then `scaffold.py run install --skip-missing`, then runs lint/test/build per project based on
  the manifest's `ci` flags and `tasks.*` commands
