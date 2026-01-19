# Upgrade the generated monorepo baseline: CI that installs, validates, and supports multiple toolchains

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`. If `.agents/agents.md` exists, it is binding.

## Purpose / Big Picture

This work improves what users get when they generate a new monorepo from this template.

After this change, a freshly scaffolded monorepo will have:

- A centralized GitHub Actions CI workflow that runs a manifest-driven project matrix.
- A “doctor” validation step that fails fast when the monorepo registry/manifest is inconsistent.
- An “install” step that makes multi-toolchain projects work in CI (Poetry/PDM/uv/npm/etc.), while remaining safe for projects that do not define install tasks.
- Basic caching and concurrency settings so CI is efficient and stable.

How to see it working: generate a new monorepo from `templates/monorepo-root`, add at least one project with the scaffold tool, and confirm:

- `python tools/scaffold/scaffold.py doctor` prints `OK`
- `python tools/scaffold/ci_matrix.py` prints valid JSON
- the generated `.github/workflows/ci.yml` includes doctor + install and runs successfully in GitHub Actions

## Progress

- [ ] Add “doctor” step to generated monorepo CI and ensure it runs before lint/test/build.
- [x] (2026-01-19) Add “install” step to generated monorepo CI using manifest tasks, safe for missing install.
- [ ] Add caching and concurrency to generated monorepo CI.
- [ ] Add minimal repo hygiene artifacts to the generated monorepo (docs + optional pre-commit/editorconfig).
- [ ] Update generated monorepo docs to explain registry/manifest, generators, trust model, vendoring, and CI behavior.
- [ ] Extend template repo tests to verify CI workflow contains doctor + install steps.

## Surprises & Discoveries

- (none yet)

## Decision Log

- (none yet)

## Outcomes & Retrospective

- (not started)

## Context and Orientation

This repository contains a Cookiecutter root template at:

- `templates/monorepo-root/`

Inside that template, the generated monorepo includes:

- `tools/scaffold/scaffold.py`: a stdlib-only CLI that reads `tools/scaffold/registry.toml` and writes/reads `tools/scaffold/monorepo.toml`.
- `tools/scaffold/ci_matrix.py`: produces JSON used by GitHub Actions to decide what projects exist and what to run.
- `.github/workflows/ci.yml`: a centralized CI workflow that runs tasks per project based on the manifest.

Important terminology used in this plan:

- “Registry” = `tools/scaffold/registry.toml`. It defines project kinds (like app/lib/data) and generators (how to create a project).
- “Manifest” = `tools/scaffold/monorepo.toml`. It lists the projects that exist and the commands (tasks) to run per project.
- “Task” = a command array recorded under `tasks.<name>` in the manifest for each project (for example, `tasks.test = ["pytest", "-q"]`). The scaffold tool uses tasks rather than hardcoding PDM/Poetry/npm so the monorepo can mix toolchains.

Optional reference baseline (no external reading required): `cookiecutter-pdm-pypackage` demonstrates strong CI discipline in a single-project repo. In a monorepo, we keep CI centralized but adopt the same idea: “CI must install dependencies and run quality gates consistently”.

## Plan of Work

First, improve the generated monorepo CI workflow.

1) Add a “Doctor” step:

- Run `python tools/scaffold/scaffold.py doctor` early in the job so invalid registry/manifest entries fail fast.
- This step validates that each listed project exists and that required task commands are on PATH.

2) Add an “Install” step:

- Run `python tools/scaffold/scaffold.py run install --project "${{ matrix.id }}" --skip-missing"`.
- Use `--skip-missing` so projects that do not define `tasks.install` (like minimal stdlib templates) do not fail CI.
- Run this step before lint/test/build so dependencies are present.

3) Add caching:

- Cache pip’s download cache (harmless even if some projects use Poetry/PDM; it still speeds up Python packaging downloads).
- Cache npm’s cache when toolchain is node.
- Keep caching conservative; avoid writing cache paths into the repo.

4) Add concurrency:

- Use GitHub Actions `concurrency` to cancel in-progress runs for the same branch on new pushes.

Second, improve generated monorepo docs and hygiene:

- Update `README.md` in the generated monorepo to include a “golden path”:
  - how to list generators and kinds
  - how to add a project
  - how to run tasks
  - how to add external templates with trust/pinning
  - how to vendor external templates for customization
- Optionally include a `.editorconfig` and minimal `.pre-commit-config.yaml` that only uses language-agnostic hooks (whitespace, YAML/TOML). Do not require ruff globally, because the monorepo must support non-python projects.

Finally, update tests in this template repo so they verify the CI workflow contains the new steps (doctor + install).

## Concrete Steps

All edits are within this template repository, but they target files that will be rendered into generated monorepos.

1) Edit the generated monorepo CI workflow template:

File:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/.github/workflows/ci.yml

Add, in the `project` job (for real projects, not the `__no_projects__` sentinel):

- A “Doctor” step (before everything else that runs tasks).
- An “Install” step (before lint/test/build), using `--skip-missing` (already present in the current template; ensure it remains).

Example structure to implement (indentation shown is YAML, not a code fence):

  - name: Doctor
    if: ${{ matrix.id != '__no_projects__' }}
    run: python tools/scaffold/scaffold.py doctor

  - name: Install
    if: ${{ matrix.id != '__no_projects__' }}
    run: python tools/scaffold/scaffold.py run install --project "${{ matrix.id }}" --skip-missing

2) Add caching steps.

For Python, add:

  - uses: actions/cache@v4
    if: ${{ matrix.id != '__no_projects__' }}
    with:
      path: ~/.cache/pip
      key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml', '**/requirements*.txt', '**/pdm.lock', '**/poetry.lock') }}
      restore-keys: |
        ${{ runner.os }}-pip-

For Node, add caching for npm:

  - uses: actions/cache@v4
    if: ${{ matrix.id != '__no_projects__' && matrix.toolchain == 'node' }}
    with:
      path: ~/.npm
      key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
      restore-keys: |
        ${{ runner.os }}-npm-

3) Add concurrency at the workflow top-level:

  concurrency:
    group: ci-${{ github.ref }}
    cancel-in-progress: true

4) Update generated monorepo documentation:

Files:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md
  templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md

Add “golden path” sections with copy/paste commands, including:

  python tools/scaffold/scaffold.py kinds
  python tools/scaffold/scaffold.py generators
  python tools/scaffold/scaffold.py add app billing-api
  python tools/scaffold/scaffold.py run test --project billing-api
  python tools/scaffold/scaffold.py vendor import <generator_id> --as <vendor_id>

Also document the trust model:

- external cookiecutter templates may execute hooks
- the scaffold tool blocks untrusted external templates unless run with `--trust`, or after vendoring

5) Add minimal repo hygiene (optional but recommended):

- `templates/monorepo-root/{{cookiecutter.repo_slug}}/.editorconfig`
- `templates/monorepo-root/{{cookiecutter.repo_slug}}/.pre-commit-config.yaml` with only generic checks

6) Extend the template repo test suite to validate CI workflow changes.

In `tests/test_scaffold_monorepo_template.py`:

- In `test_template_renders_and_internal_templates_are_not_rendered`, read the rendered `.github/workflows/ci.yml` and assert it contains strings like:
  - `scaffold.py doctor`
  - `scaffold.py run install`

This prevents regressions where CI stops installing dependencies.

## Validation and Acceptance

Acceptance is achieved when:

1) Local tests for this template repo still pass:

  pdm install
  pdm run pytest

2) A rendered monorepo has the updated CI workflow and the steps are present:

- After rendering, check the file exists:
  `<rendered_repo>/.github/workflows/ci.yml`
- Confirm it contains “Doctor” and “Install” steps as described.

3) In a rendered monorepo, a basic scenario works:

  cd <rendered_repo>
  python tools/scaffold/scaffold.py doctor
  python tools/scaffold/scaffold.py add app billing-api
  python tools/scaffold/scaffold.py run test --project billing-api

Expected outputs:

- `doctor` prints `OK`
- `add` prints `Created project billing-api at apps/billing-api`
- `run test` exits 0

4) On GitHub, a generated monorepo’s CI succeeds after adding a project that requires dependency installation (to be validated after Plan 4 introduces such generators).

## Idempotence and Recovery

- Editing the template files is safe and repeatable.
- If CI caching breaks for some environments, remove caches or narrow the cache paths; do not write cache artifacts into the repo.
- If `doctor` fails due to missing tools, the correct fix is to update tasks or CI toolchain setup, not to remove doctor.

## Artifacts and Notes

Keep the generated monorepo docs short and practical. The goal is that a new user can follow the golden path in under 10 minutes.

## Interfaces and Dependencies

This plan modifies only template files and documentation. No new Python API surface is introduced, but the generated CI workflow behavior changes (doctor + install).
