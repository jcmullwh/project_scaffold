# {{ cookiecutter.repo_name }}

This monorepo was generated from a Cookiecutter template.

## Scaffold tool

This repo includes `tools/scaffold/scaffold.py`, a small Python CLI that:

- adds new projects based on a configurable registry (`tools/scaffold/registry.toml`)
- records created projects in a manifest (`tools/scaffold/monorepo.toml`)
- runs explicit per-project tasks from the manifest (no toolchain assumptions)

## Requirements

- Always: `python` (Python 3.11+ recommended).
- For Cookiecutter generators: `cookiecutter`.
- For external templates and vendoring: `git`.

See `tools/scaffold/README.md` for details.

Quick start:

    python tools/scaffold/scaffold.py doctor
    python tools/scaffold/scaffold.py kinds
    python tools/scaffold/scaffold.py add app demo-app
    python tools/scaffold/scaffold.py run test --project demo-app
