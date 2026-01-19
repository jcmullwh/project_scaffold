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

- [x] (2026-01-19) Add ruff, mypy, deptry, and coverage configuration and dev dependencies to the template repo.
- [x] (2026-01-19) Add pre-commit hooks and basic repo hygiene files for contributors.
- [x] (2026-01-19) Add GitHub Actions CI workflow for the template repo (lint/type/test + template smoke).
- [x] (2026-01-19) Ensure all existing tests still pass and adjust tests only if required by new strictness.
- [x] (2026-01-19) Document local developer workflow in CONTRIBUTING.md / DEVELOPING.md.

## Surprises & Discoveries

- Observation: Cookiecutter templates can include Python files that are intentionally not valid Python until rendered (e.g. `import {{ cookiecutter.package_name }}`), which breaks static tooling that parses `.py` files.
  Evidence: `python-stdlib-cookiecutter/{{cookiecutter.project_slug}}/tests/test_basic.py` contains cookiecutter placeholders.
- Observation: Deptryâ€™s `exclude` config option overwrites its default excludes (including `.venv/` and `tests/`), which can accidentally scan the virtualenv and explode into thousands of false positives.
  Evidence: Running `pdm run deptry .` after setting `exclude` scanned `.venv/Lib/site-packages/**` and reported thousands of issues.

## Decision Log

- Decision: Exclude generator template directories from ruff/mypy/deptry scanning via `templates/**/tools/templates/**`.
  Rationale: Generator templates may contain non-parseable placeholder Python, but we still want to typecheck/lint the scaffold tooling under `templates/**/tools/scaffold/**`.
  Date/Author: 2026-01-19 / Codex
- Decision: Set `ruff` line length to 120.
  Rationale: The scaffold tooling has many user-facing error messages and help strings; 100 was overly noisy while still keeping lines reasonably bounded.
  Date/Author: 2026-01-19 / Codex
- Decision: Keep `tomli` as an optional fallback for Python <3.11 and teach deptry to tolerate its dev-only declaration.
  Rationale: The generated scaffold tooling supports older Python with `tomli`; deptry otherwise reports it as a DEP004 mismatch. We want deptry signal for real drift, not for optional backports.
  Date/Author: 2026-01-19 / Codex
- Decision: Ignore Ruff rule `UP017` (prefer `datetime.timezone.utc` over `datetime.UTC`).
  Rationale: `datetime.UTC` is Python 3.11+; the generated scaffold tooling includes compatibility code for older Python versions.
  Date/Author: 2026-01-19 / Codex

## Outcomes & Retrospective

- Outcome: The template repo now has a repeatable local and CI quality baseline: ruff format/lint, mypy, deptry, and pytest.
- Outcome: Repo hygiene files and a contributor guide exist to make it easy to run the same gates locally that CI enforces.

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

---

Plan update (2026-01-19): Recorded implementation decisions/discoveries and marked all milestones complete after adding tooling, CI, and docs.
