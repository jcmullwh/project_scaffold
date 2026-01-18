# `tools/scaffold`

`tools/scaffold/scaffold.py` is a stdlib-only Python CLI for managing this monorepo.

## Minimal requirements

- Always required: `python` on PATH (Python 3.11+ recommended; older Pythons need `tomli` installed to parse TOML).
- Required only for Cookiecutter-based generators: `cookiecutter` on PATH.
- Required only for external Cookiecutter sources and vendoring: `git` on PATH.
- Required only for running tasks: whatever commands your `tasks.*` reference (e.g. `poetry`, `uv`, `npm`, `cargo`, `terraform`).

## Virtual environments

This tool does not create or manage virtual environments. For Python projects, use whatever per-project environment strategy your generator and `tasks.*` imply (Poetry/uv/pip-tools/conda/PDM/venv/etc.). The scaffolder runs tasks exactly as recorded in `tools/scaffold/monorepo.toml`.

## Configuration model

- Kinds and generators are defined in `tools/scaffold/registry.toml`.
- Created projects are recorded in `tools/scaffold/monorepo.toml` and are the source of truth for repo-wide task execution and CI.

## Generator types (registry examples)

Copy (local skeleton directory):

    [generators.terraform_module]
    type = "copy"
    source = "tools/templates/internal/terraform-module"
    toolchain = "terraform"
    package_manager = "none"
    tasks.lint = ["terraform", "fmt", "-check", "-recursive"]

Cookiecutter (local or external; external should be pinned and untrusted by default):

    [generators.external_cookiecutter_x]
    type = "cookiecutter"
    source = "https://github.com/someone/some-template.git"
    ref = "v1.2.3"
    trusted = false
    toolchain = "python"
    package_manager = "poetry"
    tasks.install = ["poetry", "install"]
    tasks.test = ["poetry", "run", "pytest"]

Command (anything that can create the destination directory):

    [generators.node_vite]
    type = "command"
    toolchain = "node"
    package_manager = "npm"
    command = ["npm", "create", "vite@latest", "{dest_dir}"]
    tasks.install = ["npm", "install"]
    tasks.build = ["npm", "run", "build"]
