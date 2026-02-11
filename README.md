# project-scaffold

This repository is a Cookiecutter template repo. It generates a separate monorepo repository that includes a small
stdlib-only scaffolder CLI (`tools/scaffold/scaffold.py`) for adding projects and running per-project tasks.

## Choose Your Path

Architecture and entry points: see `docs/ARCHITECTURE.md`.

Fastest smoke path (two contexts):

- Generate a monorepo (template repo) and run `doctor` (generated repo):

      cookiecutter templates/monorepo-root --no-input -o .tmp
      python .tmp/my-monorepo/tools/scaffold/scaffold.py doctor

  This smoke path does not require `pdm install`. It requires only `cookiecutter` and `python` on PATH.

  PowerShell one-liner:

      cookiecutter templates/monorepo-root --no-input -o .tmp; python .tmp/my-monorepo/tools/scaffold/scaffold.py doctor

  bash one-liner:

      cookiecutter templates/monorepo-root --no-input -o .tmp && python .tmp/my-monorepo/tools/scaffold/scaffold.py doctor

  Cleanup: delete `.tmp/`.

- Validate the template repo dev environment (template repo):

      pdm install
      pdm run pytest

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

Next, scaffold a small stdlib-only project without running installs:

    python tools/scaffold/scaffold.py add lib demo-lib --generator python_stdlib_copy --no-install

Generated-monorepo docs (as template preview copies in this repo):

- `templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md`
- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md`
- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/SUPPORT_MATRIX.md`

Note: paths under `templates/` contain literal `{{cookiecutter...}}` placeholder braces because this repo stores the
template source. On PowerShell, quote brace-containing paths when using them as command arguments.

PowerShell example (read a template-preview doc path safely):

    Get-Content -LiteralPath 'templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md' | Select-Object -First 20

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
