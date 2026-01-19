# Add monorepo-ready “gold standard” Python generators based on cookiecutter-pdm-pypackage (PDM lib + PDM app)

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`. If `.agents/agents.md` exists, it is binding.

## Purpose / Big Picture

This work adds high-quality Python scaffolding options to the generated monorepo, inspired by the “cookiecutter-pdm-pypackage” template (used here only as a conceptual baseline; no external reading required).

Reference URL: https://github.com/jcmullwh/cookiecutter-pdm-pypackage

That reference template is designed for a single Python package using PDM and includes a mature “baseline” for real projects (ruff, mypy, deptry, pytest, optional tox, optional docs with MkDocs).

After this change, a newly generated monorepo can create Python projects that are “ready for real work” by choosing generators such as:

- `python_pdm_lib` (publishable library defaults; strict checks)
- `python_pdm_app` (deployable app/service defaults; practical runtime structure)

These generators must be monorepo-safe: they must not create their own GitHub workflows or assume they are the repo root. CI remains centralized at the monorepo root and runs tasks defined in the manifest.

How to see it working: in a generated monorepo:

  python tools/scaffold/scaffold.py add lib my-lib --generator python_pdm_lib
  python tools/scaffold/scaffold.py run install --project my-lib
  python tools/scaffold/scaffold.py run lint --project my-lib
  python tools/scaffold/scaffold.py run test --project my-lib

should work without manual wiring.

## Progress

- [x] (2026-01-19) Decide whether the PDM templates will be (a) vendored copies of cookiecutter-pdm-pypackage or (b) new internal templates modeled after it.
- [x] (2026-01-19) Implement `python_pdm_lib` generator template and registry entry with install/lint/format/typecheck/test tasks.
- [x] (2026-01-19) Implement `python_pdm_app` generator template and registry entry with install/lint/format/typecheck/test tasks.
- [x] (2026-01-19) Ensure generated subprojects do not include `.github/workflows` (monorepo-safe).
- [x] (2026-01-19) Add end-to-end tests in the template repo that scaffold both generators with `--no-install` and validate manifest tasks (offline-safe).
- [x] (2026-01-19) Document how to use these generators in generated monorepo README.

## Surprises & Discoveries

- Observation: Running `pdm install` for newly scaffolded subprojects is not reliably offline-friendly for the template repo’s pytest suite.
  Evidence: The suite must run without network calls; installing real dependencies from PyPI would violate that constraint.

## Decision Log

- Decision: Implement these generators as new internal cookiecutter templates (not a vendored upstream snapshot).
  Rationale: Keep the generator offline-friendly, monorepo-safe, and easy to iterate without tracking upstream template changes.
  Date/Author: 2026-01-19 / Codex
- Decision: Set `python_pdm_lib` as a distribution project and `python_pdm_app` as non-distribution.
  Rationale: Libraries typically publish artifacts; apps/services often prioritize runtime layout over packaging.
  Date/Author: 2026-01-19 / Codex
- Decision: Keep template repo tests offline by scaffolding with `--no-install` and asserting manifest tasks instead of running `pdm install`.
  Rationale: Validates integration (template + registry + scaffold manifest wiring) without requiring network access or external tools during the template repo’s CI.
  Date/Author: 2026-01-19 / Codex

## Outcomes & Retrospective

- Outcome: Generated monorepos include `python_pdm_lib` and `python_pdm_app` generator IDs with explicit manifest tasks for install/lint/format/typecheck/depcheck/test.
- Outcome: Internal templates live under `tools/templates/internal/python-pdm-lib/` and `tools/templates/internal/python-pdm-app/` and do not add any per-project CI.
- Outcome: Template repo tests scaffold both generators (offline) and confirm the manifest records the expected tasks.

## Context and Orientation

Where the work lives:

- This repository’s root template is at `templates/monorepo-root/`.
- Inside that template, the generated monorepo contains:
  - `tools/scaffold/registry.toml`: defines generators
  - `tools/templates/internal/`: internal generator templates/skeletons
  - `tools/scaffold/scaffold.py`: the CLI that creates a project using a generator and records tasks in `tools/scaffold/monorepo.toml`

Important constraints:

- The generated monorepo must be toolchain-agnostic. The scaffold tool runs with plain `python`.
- A generator defines tasks explicitly. For example, PDM-based projects should include:
  - `tasks.install = ["pdm", "install"]`
  - `tasks.test = ["pdm", "run", "pytest"]` (or similar)
- Subprojects must not create `.github/workflows/**` because CI is centralized at monorepo root.

Reference baseline from cookiecutter-pdm-pypackage (embed the relevant idea so we do not depend on external docs):

- Use ruff for lint and formatting.
- Use mypy for typing.
- Use deptry for unused/missing dependency checks.
- Use pytest for tests.
- Optional: tox for testing against multiple Python versions.
- Optional: docs site with MkDocs Material + mkdocstrings.

We will include these as defaults in library template and as opt-in in app template.

## Plan of Work

Step 1: Choose implementation approach for incorporating cookiecutter-pdm-pypackage.

Preferred approach for maintainability:

- Vendor a snapshot of cookiecutter-pdm-pypackage into the template repo (or into the generated monorepo internal templates), then adapt it:
  - remove `.github/workflows`
  - adjust documentation to monorepo usage
  - ensure cookiecutter variables align with scaffold context defaults

Alternative approach:

- Re-create a simplified internal template that uses the same stack and conventions, but is authored specifically for monorepo.

This plan assumes the “adapted internal template” approach, because it produces a stable offline-friendly generator even if upstream changes.

Step 2: Implement two internal cookiecutter templates in the generated monorepo template:

Create directories under:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/templates/internal/

- `python-pdm-lib/`
- `python-pdm-app/`

Each contains:
- `cookiecutter.json`
- `{{cookiecutter.project_slug}}/...` template files

The lib template must include:
- `pyproject.toml` configured for PDM distribution (publishable library)
- ruff config, mypy config, deptry config, pytest config
- tests directory with a passing basic test
- an installable package under `src/<package_name>/`

The app template must include:
- `pyproject.toml` configured for PDM but not necessarily distribution-focused (apps may not publish)
- runtime entrypoint or `src/<package_name>/__main__.py`
- ruff/mypy/pytest as baseline, deptry optional
- optional Dockerfile is allowed but not required in this milestone

Step 3: Register generators in the generated monorepo registry.

Edit:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/registry.toml

Add:

- `[generators.python_pdm_lib]` (type cookiecutter, source local internal template path, name_var, context_defaults)
- `[generators.python_pdm_app]` (same)

Each must define tasks:

- install: `["pdm", "install"]`
- lint: `["pdm", "run", "ruff", "check", "."]` or `["pdm", "run", "lint"]` if your template defines scripts
- format (optional): `["pdm", "run", "ruff", "format", "."]` or `["pdm", "run", "format"]`
- typecheck: `["pdm", "run", "mypy", "."]`
- test: `["pdm", "run", "pytest", "-q"]`
- depcheck (optional): `["pdm", "run", "deptry", "."]`
- docs (optional): `["pdm", "run", "mkdocs", "build"]`

Prefer explicit tool invocations in tasks rather than relying on custom scripts, unless you are committed to maintaining those scripts.

Step 4: Add template repo tests.

Extend `tests/test_scaffold_monorepo_template.py` to:

- Render a monorepo
- Add one lib project using `python_pdm_lib` generator, with `--no-install` (so the test doesn’t require PDM installed), and verify directory structure exists
- Add one app project using `python_pdm_app`
- Optionally, if `pdm` exists on PATH in test environment, run `install` + `test`; otherwise, verify that `doctor` reports missing pdm and fail with a clear reason. (Decide one behavior and document it.)

Because this template repo must run tests offline, do not depend on downloading packages from the internet. If you want to test real `pdm install`, you must keep dependencies minimal and allow it to run without network (hard). The safer approach is:

- Unit-test scaffold behavior (file creation + manifest tasks recorded)
- Do not require `pdm install` in template repo tests

Monorepo CI (Plan 2) can run install in real generated repos when used in real projects.

Step 5: Document these generators in the generated monorepo README and tools docs.

Update:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md
  templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md

Include:

- Example usage of these generators
- Note that they require `pdm` to run tasks

## Concrete Steps

1) Create internal cookiecutter templates.

Create directories:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/templates/internal/python-pdm-lib/
  templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/templates/internal/python-pdm-app/

Add `cookiecutter.json` files with at least:

- `project_slug` (folder name)
- `package_name` (python import package name)

2) Implement a minimal but realistic PDM `pyproject.toml` in each template.

Library template should set PDM as distribution project (publishable). App template can set it as non-distribution (or still distribution if you want consistency; record decision).

Both should include:

- ruff config
- mypy config
- pytest config

3) Add registry entries and tasks in:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/registry.toml

4) Run template repo tests:

From template repo root:

  pdm install
  pdm run pytest

Expected: tests pass and new generators can be selected in scaffold CLI.

5) Manual smoke in a rendered monorepo:

Render a monorepo using cookiecutter (either via the existing test helper or manually), then:

  cd <rendered_repo>
  python tools/scaffold/scaffold.py generators
  python tools/scaffold/scaffold.py add lib my-lib --generator python_pdm_lib --no-install
  python tools/scaffold/scaffold.py add app my-app --generator python_pdm_app --no-install

Confirm directories exist and `tools/scaffold/monorepo.toml` includes tasks for these projects.

## Validation and Acceptance

Acceptance is achieved when:

1) A generated monorepo contains the new internal templates and registry entries.

2) `python tools/scaffold/scaffold.py generators` lists `python_pdm_lib` and `python_pdm_app`.

3) Adding projects works and records tasks:

  python tools/scaffold/scaffold.py add lib my-lib --generator python_pdm_lib --no-install
  python tools/scaffold/scaffold.py add app my-app --generator python_pdm_app --no-install

4) The template repo test suite passes offline.

## Idempotence and Recovery

- Creating a project should refuse if destination exists; this is already how scaffold behaves. If you need to re-run, delete the created project dir and remove its entry from the manifest.
- Keep templates small and composable. If you later decide to vendor upstream, you can replace these internal templates while keeping generator IDs stable.

## Artifacts and Notes

When porting conventions from cookiecutter-pdm-pypackage, avoid bringing over per-repo GitHub workflows. A monorepo must keep CI centralized.

## Interfaces and Dependencies

This plan introduces two new generator IDs in `tools/scaffold/registry.toml` (inside generated monorepos):

- `python_pdm_lib`
- `python_pdm_app`

It introduces new internal template directories under `tools/templates/internal/`.

---

Plan update (2026-01-19): Marked milestones complete and recorded decisions about template structure, offline testing, and app vs. lib distribution settings.
