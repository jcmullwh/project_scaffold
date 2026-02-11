# Troubleshooting

This project has two distinct workflows and failure modes:

- Template repo workflow (this repo): you develop templates and run the offline test suite.
- Generated monorepo workflow (output of Cookiecutter): you run `tools/scaffold/scaffold.py` to add projects and run
  tasks.

Most confusion comes from running the right command in the wrong repo. If you're unsure which repo you are in, start
with "Where am I?" below.

## Where am I?

Template repo (this repo):

- Has `templates/monorepo-root/` and `tests/`.
- Uses PDM (`pdm install`, `pdm run pytest`).

Generated monorepo:

- Has `tools/scaffold/scaffold.py`, `tools/scaffold/registry.toml`, and `tools/scaffold/monorepo.toml`.
- Uses plain `python tools/scaffold/scaffold.py ...` (does not assume PDM exists).

## Prerequisites

Template repo development:

- `python` on PATH (see `pyproject.toml` for the minimum version).
- `pdm` on PATH (this repo's dev workflow uses PDM).

Generated monorepo usage:

- Always: `python` on PATH (Python 3.11+ recommended for stdlib TOML parsing).
- For Cookiecutter generators: `cookiecutter` on PATH.
- For external template sources and vendoring: `git` on PATH.
- For running tasks: whatever commands your chosen generator recorded under `tasks.*` (for example `pdm`, `poetry`, `uv`,
  `npm`, `go`, `cargo`, `terraform`).

For a generator-by-generator view of tool requirements, see the generated monorepo's `tools/scaffold/SUPPORT_MATRIX.md`
(or the preview copy in this repo under `templates/`).

## Common failures and recovery

### "cookiecutter: command not found"

You are trying to generate a monorepo, but Cookiecutter is not installed.

Fix:

- Install Cookiecutter into your preferred environment (pipx/system Python/venv), then re-run:

      cookiecutter templates/monorepo-root -o <output_dir>

### "scaffold.py: command not found" or running `scaffold.py` in the template repo

The scaffolder CLI exists in the generated monorepo. If you run `python tools/scaffold/scaffold.py ...` in this template
repo, the path will not exist.

Fix:

1. Generate a monorepo via Cookiecutter.
2. `cd` into the generated repo root.
3. Run:

      python tools/scaffold/scaffold.py doctor

### "Required command not found on PATH"

When `scaffold.py` runs a task (or runs `tasks.install` by default during `add`), it executes the task command exactly as
recorded in `tools/scaffold/monorepo.toml`. If that command is not on PATH, the run fails.

Fix:

- Install the missing toolchain (for example `pdm`, `poetry`, `uv`, `npm`, `go`, `cargo`, `terraform`), then re-run the
  failing command.
- If you only want to generate files first, add `--no-install`:

      python tools/scaffold/scaffold.py add <kind> <project_id> --no-install

### Install failed after generation (manifest vs on-disk state)

If `scaffold.py add` fails after it creates files, the project may still be recorded in `tools/scaffold/monorepo.toml`.

Fix:

1. Fix the underlying issue (missing tool, broken config, interactive generator prompt, etc.).
2. Re-run install for the recorded project:

      python tools/scaffold/scaffold.py run install --project <project_id>

3. If you want to unregister the project from the manifest:

      python tools/scaffold/scaffold.py remove <project_id>

### External template trust gate failures

External Cookiecutter templates can execute code via hooks. The registry can mark them `trusted = false`, which causes
`scaffold.py add` to refuse to run them by default.

Fix:

- Re-run the `add` with `--trust` for that run only, or vendor the template into `tools/templates/vendor/` for long-lived
  use.

### PowerShell brace-placeholder paths (`{{...}}`)

Both the template repo and the generated monorepo contain literal placeholder directories like
`{{cookiecutter.project_slug}}` under template trees. On PowerShell, quote brace-containing paths and use `-LiteralPath`
with cmdlets.

Examples:

    Get-Content -LiteralPath 'templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md' | Select-Object -First 20
    Get-ChildItem -LiteralPath 'tools/templates/internal/python-stdlib-cookiecutter/{{cookiecutter.project_slug}}'

### Network-restricted environments

Some generators are inherently networked. For example, the built-in `node_vite` generator runs `npm create vite@latest`
and may fetch packages.

Fix:

- Use `--no-install` to separate generation from installs.
- Prefer vendored, pinned templates for long-lived use in restricted environments.

## What CI covers

The template repo's CI (`.github/workflows/ci.yml`) runs on Ubuntu with multiple Python versions and validates:

- formatting/linting/typechecking/dependency checks for the template repo, and
- offline template rendering and scaffolder behavior via `pdm run pytest`.

It does not currently run every external toolchain's tasks end-to-end (npm/go/cargo/terraform) and does not currently
exercise Windows/macOS runners.

