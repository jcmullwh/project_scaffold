# Adopt snapshot publishing tooling + GitLab walkthrough

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

Add a first-class, repeatable way for generated monorepos to publish “snapshot” (dev) builds of eligible Python packages to a GitLab PyPI registry, along with CI wiring and a setup walkthrough. After this change, a freshly scaffolded monorepo will contain:

- A `tools/monorepo_publish` Python utility that discovers eligible packages under `packages/`, rewrites internal dependencies to pinned snapshot versions, builds dists, and uploads them to a GitLab PyPI registry.
- A CI workflow (`.github/workflows/publish-snapshots.yml`) that runs the publisher in GitHub Actions.
- Clear documentation for how to configure GitLab credentials/variables and how to consume the published packages via `pip` and `pdm`.

The visible “it works” proof is: in a generated monorepo with at least one eligible package, running the publisher with `--dry-run` prints computed snapshot versions and validates dependency rewrites, and the CI workflow can run the publisher self-test successfully.

## Progress

- [x] (2026-02-01 22:58Z) Read existing repo instructions and template layout; located the source `tools/monorepo_publish` and `publish-snapshots.yml` to adopt.
- [x] (2026-02-01 23:09Z) Imported `tools/monorepo_publish` and `tools/requirements-publish.txt` into the monorepo-root template.
- [x] (2026-02-01 23:09Z) Imported `.github/workflows/publish-snapshots.yml` into the monorepo-root template.
- [x] (2026-02-01 23:09Z) Added docs: GitLab publishing setup + consuming packages via `pip` and `pdm` (`tools/monorepo_publish/README.md`), and linked it from the template root `README.md`.
- [x] (2026-02-01 23:09Z) Validated: `pdm run ruff format`, `pdm run ruff check`, `pdm run mypy`, `pdm run deptry`, `pdm run pytest` (19 passed).
- [x] (2026-02-01 23:09Z) Moved plan to `4 - for_review`.

## Surprises & Discoveries

- Observation: The `templates/monorepo-root/{{cookiecutter.repo_slug}}/packages/` directory starts empty (only `.gitkeep`), so snapshot publishing needs documentation that packages must opt-in to publishing (and/or an explicit `status` field).
  Evidence: `templates/monorepo-root/{{cookiecutter.repo_slug}}/packages/.gitkeep`.
- Observation: The adopted publisher scripts required repo-standard Ruff formatting/lint fixes (import sorting and one exception-chaining lint).
  Evidence: `pdm run ruff format .` and `pdm run ruff check --fix .` were required after copying.

## Decision Log

- Decision: Install the publisher into the *monorepo template* (`templates/monorepo-root/...`) rather than the scaffold repo runtime itself.
  Rationale: The publisher expects a monorepo layout with `packages/` and is intended for use in generated monorepos, not in the template generator repo.
  Date/Author: 2026-02-01 / Codex
- Decision: Exclude the new template publisher directory from this repo’s `mypy` and `deptry` scans.
  Rationale: The template publisher intentionally depends on third-party publish-time libraries; treating those imports as dependencies of the *template generator repo* breaks CI signals for this repo. We continue to type-check the stdlib-only `tools/scaffold` template code.
  Date/Author: 2026-02-01 / Codex
- Decision: Make publishing opt-in explicit in Python templates by adding `[tool.monorepo].status = "internal"` to the PDM and uv templates.
  Rationale: The publisher uses `status` as the eligibility gate; making it explicit avoids “invisible” defaults and makes opt-in a one-line change (`internal` → `incubator`/`supported`/`stable`).
  Date/Author: 2026-02-01 / Codex

## Outcomes & Retrospective

The monorepo-root template now ships with a snapshot publishing utility and a GitHub Actions workflow to publish snapshots to a GitLab PyPI registry. A GitLab setup + consumption walkthrough is included alongside the tool.

Potential follow-ups (not implemented here):

- Add a `tools/monorepo_publish/setup_gitlab.py` helper that validates a GitLab token, resolves project ID from a path, and prints the exact URLs/variables to set for publishing and installing.
- Add an optional scaffold command (or generator) that can drop in a `.gitlab-ci.yml` publishing job for teams using GitLab CI instead of GitHub Actions.
- Extend the publisher to support group-level registries and/or multi-project installs (GitLab “group deploy token” guidance + pip/PDM config patterns).
- Add a small “publisher doctor” mode that checks for common misconfigurations (missing `[tool.monorepo].status`, Poetry-format packages under `packages/`, local `file://` deps to non-monorepo packages, etc.).

## Context and Orientation

This repository (`project-scaffold`) is the Cookiecutter template source for generated monorepos. The monorepo template lives under:

    templates/monorepo-root/{{cookiecutter.repo_slug}}/

Within the generated monorepo template:

- `.github/workflows/ci.yml` runs a project-matrix CI using `tools/scaffold/scaffold.py`.
- `packages/` is where monorepo libraries live by default (`tools/scaffold/registry.toml` has `kinds.lib.output_dir = "packages"`).
- `tools/scaffold/` is a small Python CLI to add projects and run tasks without assuming a single toolchain.

The source material to adopt comes from another monorepo working tree:

- `tools/monorepo_publish/` (Python module + script)
- `tools/requirements-publish.txt` (publisher runtime dependencies)
- `.github/workflows/publish-snapshots.yml` (GitHub Actions workflow that installs the publish deps and runs the publisher)

## Plan of Work

1) Copy the publisher tool (`tools/monorepo_publish`) and its runtime dependency list (`tools/requirements-publish.txt`) into `templates/monorepo-root/{{cookiecutter.repo_slug}}/`.

2) Copy the workflow `publish-snapshots.yml` into `templates/monorepo-root/{{cookiecutter.repo_slug}}/.github/workflows/`, and ensure its paths align with the template layout.

3) Add documentation to the generated monorepo template describing:

- How package eligibility works (via `[tool.monorepo].status`), including recommended defaults.
- How to create GitLab credentials (deploy token or equivalent) and wire them into CI variables/secrets.
- How to test the publisher without publishing (`--self-test`, `--dry-run`).
- How to install published packages from GitLab PyPI using `pip` and using `pdm` configuration.

4) Validate changes by running this repo’s checks via `pdm run ...`, and by running the publisher self-test from within the template tree.

## Concrete Steps

All commands run from the repository root `i:\\code\\project_scaffold`.

1) Run this repo’s checks:

    pdm install
    pdm run ruff format --check .
    pdm run ruff check .
    pdm run mypy .
    pdm run deptry .
    pdm run pytest

2) Publisher sanity checks (from repo root):

    python templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/monorepo_publish/publish_snapshots.py --self-test

Expected output includes:

    self-test: ok (snapshot_id=...)

## Validation and Acceptance

Acceptance is met when:

- The generated monorepo template contains `tools/monorepo_publish/`, `tools/requirements-publish.txt`, and `.github/workflows/publish-snapshots.yml`.
- Documentation exists in the generated monorepo template that a novice can follow to:
  - set up GitLab credentials/variables,
  - run `--self-test` locally,
  - run `--dry-run` in CI or locally,
  - and install published packages via `pip` and via `pdm`.
- Running this repo’s existing CI-equivalent commands (`pdm run ...`) still passes.

## Idempotence and Recovery

The publisher does all mutation in a temporary directory when publishing; local runs are safe. CI variables should be additive; if secrets are missing, the publisher should fail loudly rather than silently skipping publishing.

## Artifacts and Notes

Key validation transcript:

    pdm run pytest
    ...................                                                      [100%]
    19 passed in 22.69s

## Interfaces and Dependencies

The publisher depends on Python 3.11+ and these runtime libs when invoked:

- `build` (PEP 517 build frontend for sdists/wheels)
- `packaging` (version parsing + requirement parsing)
- `tomlkit` (TOML rewrite preserving formatting)
- `twine` (uploading dists)
