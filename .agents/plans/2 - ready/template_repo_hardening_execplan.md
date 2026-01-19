# Harden the project_scaffold template repository: linting, typing, pre-commit, and CI

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`. If this repository contains `.agents/agents.md`, treat it as binding for how to work (for example, it may require using PDM for development).

## Purpose / Big Picture

This work makes the *template repository itself* (the repo that contains the Cookiecutter templates and tests) reliable and safe to change.

After this change, a contributor can run one command locally to verify quality gates (formatting, linting, typing, tests), and the repository will also enforce those gates in GitHub Actions. This prevents subtle regressions in the Cookiecutter templates and in the generated monorepo’s scaffold tooling.

How to see it working: on a clean checkout, running:

  pdm install
  pdm run ruff check .
  pdm run mypy .
  pdm run pytest

should succeed locally, and GitHub Actions for this repo should run the same checks on pushes and PRs.

## Progress

- [ ] Add ruff, mypy, deptry, and coverage configuration and dev dependencies to the template repo.
- [ ] Add pre-commit hooks and basic repo hygiene files for contributors.
- [ ] Add GitHub Actions CI workflow for the template repo (lint/type/test + template smoke).
- [ ] Ensure all existing tests still pass and adjust tests only if required by new strictness.
- [ ] Document local developer workflow in CONTRIBUTING.md / DEVELOPING.md.

## Surprises & Discoveries

- (none yet)

## Decision Log

- (none yet)

## Outcomes & Retrospective

- (not started)

## Context and Orientation

This repository is a “template repo”: its primary deliverable is a Cookiecutter template that generates a monorepo skeleton.

Key paths you should know (repository-relative):

- `templates/monorepo-root/` is the Cookiecutter template directory. When a user runs Cookiecutter, it produces a new monorepo folder.
- `tests/test_scaffold_monorepo_template.py` renders the template into a temp directory and runs end-to-end checks by calling the generated repo’s `tools/scaffold/scaffold.py`.
- `pyproject.toml` at repo root configures how to develop and test this template repo itself. In many setups, this repo uses PDM for development; if `.agents/agents.md` says “use pdm”, follow it.

Important constraint: this plan is about improving the *template repository itself*. Do not make changes that force generated monorepos to use PDM; generated monorepos must remain toolchain-agnostic.

Optional reference baseline (no external reading required): `cookiecutter-pdm-pypackage` is a single-project Python template that demonstrates a “gold standard” quality baseline (ruff, mypy, deptry, pytest, tox, docs, CI). We will borrow the *idea* (quality gates and CI discipline) for this repo, not necessarily the exact implementation.

## Plan of Work

First, add static analysis and test tooling to this repository’s development setup:

- Add ruff as both linter and formatter.
- Add mypy for type checking.
- Add deptry (or similar) to prevent dependency drift.
- Add coverage configuration so tests can report meaningful coverage.

Second, add contributor ergonomics:

- Add a `.pre-commit-config.yaml` using ruff and basic whitespace/YAML/TOML checks.
- Add `.editorconfig` for consistent newlines/indentation.
- Add `CONTRIBUTING.md` (or `DEVELOPING.md`) with “how to run checks locally”.

Third, add GitHub Actions CI for this repository:

- Use `actions/checkout`.
- Set up Python (use a small matrix like 3.11 and 3.12; keep it simple at first).
- Run `pdm install` and then run the same commands contributors run locally:
  - `pdm run ruff check .`
  - `pdm run ruff format --check .`
  - `pdm run mypy .`
  - `pdm run pytest`

The existing pytest suite already acts as a “template smoke test” by rendering a monorepo and exercising the generated `tools/scaffold` CLI. Keep those tests; this CI should run them.

Finally, ensure everything passes and update docs.

## Concrete Steps

All commands in this section are run from the repository root (where `pyproject.toml` lives).

1) Install development dependencies:

  pdm install

Expected: PDM creates/uses a virtual environment and installs test + tooling dependencies.

2) Add tooling dependencies and configs.

Edit `pyproject.toml` and add dev dependencies for:

- ruff
- mypy
- deptry
- coverage[toml]

Also add config sections:

- `[tool.ruff]` and optionally `[tool.ruff.format]`
- `[tool.mypy]`
- `[tool.deptry]` (if used)
- `[tool.coverage.run]` and `[tool.coverage.report]`

3) Run formatting and lint checks:

  pdm run ruff format .
  pdm run ruff check .

Expected: exit code 0; if not, fix issues and re-run.

4) Run type check:

  pdm run mypy .

Expected: exit code 0. If you see errors, prefer fixing types; if a module is intentionally dynamic, use narrow per-line `# type: ignore[code]` comments instead of turning off checks globally.

5) Run tests:

  pdm run pytest

Expected: exit code 0.

6) Add pre-commit.

Create `.pre-commit-config.yaml` at repo root with:

- basic repo hooks (trailing whitespace, end-of-file-fixer, check-yaml, check-toml)
- ruff check
- ruff format

Install and run:

  pdm run pre-commit install
  pdm run pre-commit run --all-files

If you do not want to add `pre-commit` as a dependency, document that it is optional. If you do add it, put it in dev dependencies.

7) Add CI workflow for this repo.

Create `.github/workflows/ci.yml` (repo root, not in templates) that runs the steps above.

8) Add contributor docs.

Create `CONTRIBUTING.md` describing:

- `pdm install`
- `pdm run ruff check .`
- `pdm run mypy .`
- `pdm run pytest`

## Validation and Acceptance

Acceptance is achieved when:

1) Local validation passes on a clean checkout:

  pdm install
  pdm run ruff check .
  pdm run ruff format --check .
  pdm run mypy .
  pdm run pytest

2) GitHub Actions CI for this repository runs those same checks and passes on PRs.

3) The template smoke tests still render a monorepo and can run scaffold commands.

## Idempotence and Recovery

- All commands are safe to run repeatedly.
- If CI fails due to formatting, run `pdm run ruff format .` locally and commit the changes.
- If mypy fails unexpectedly, fix type hints first. Only relax rules if there is a clear justification and document it in `Decision Log`.

## Artifacts and Notes

Keep changes minimal and observable. When you add CI, include a short snippet of expected job steps in the PR description, e.g.:

  - lint: ruff check, ruff format --check
  - typecheck: mypy
  - tests: pytest

## Interfaces and Dependencies

No public interfaces are introduced in this plan. Dependencies added (ruff/mypy/deptry/coverage) are only for developing and testing this template repository.

