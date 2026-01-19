# User Info: project-scaffold

This document captures who uses/maintains this repo and what constraints/preferences should guide changes.

How to use:
- Keep this file up to date as constraints change.
- Prefer linking to existing docs (`README.md`, `CONTRIBUTING.md`, `.agents/agents.md`) instead of duplicating them.

## Primary Maintainer

- Name/handle: Jason (GitHub: `jcmullwh`)
- Role: Maintains the Cookiecutter templates + scaffolding tooling; uses plans/artifacts under `.agents/` for a
  reproducible audit trail.
- Working environment (OS/shell/editor): Windows + PowerShell locally; editor not specified (update if needed); CI runs on
  GitHub Actions (ubuntu-latest).
- Priorities (what "good" looks like): Repeatable runs + audit trail under `.agents/`; toolchain-agnostic generated
  monorepos (explicit `tasks.*` in a manifest); loud failures; offline tests; cross-platform outputs.
- Hard constraints (non-negotiable): Use PDM for *this* repo’s workflow (`pdm install`, `pdm run ...`); tests run offline
  (no network; no real external binaries); no silent defaults/fallbacks; fix root causes and keep changes generic.
- "Do not do" list: No placeholder behavior in runtime tooling; no silent degradation; no implicit toolchain coupling in
  generated monorepos (CI follows manifest `tasks.*`).
- Review/acceptance expectations: Update docs when behavior changes; add/update offline tests; `pdm run ruff format --check
  .`, `pdm run ruff check .`, `pdm run mypy .`, `pdm run deptry .`, `pdm run pytest` pass.

## Contributors (optional)

- Who contributes and how (PRs only? direct pushes?): Primarily a single maintainer; outside contributions should be PRs.
- Expectations for code style and docs: Treat `.agents/agents.md` as binding; run the repo checks from
  `CONTRIBUTING.md`; keep edits small/explicit; keep tests offline; keep `.agents/` planning artifacts current when doing
  multi-step work.

## Consumers / Intended Audience

Describe the people who use this repo's output (generated monorepo scaffold), not just the repo itself.

- Persona 1: Monorepo creator/maintainer (developer)
  - Goal: Generate a new monorepo, then add new subprojects over time with explicit, per-project task commands.
  - Assumed tooling: `python` on PATH (Python 3.11+ recommended); optionally `cookiecutter` + `git` for
    cookiecutter/vendoring; toolchains referenced by `tasks.*` (pdm/poetry/uv/npm/cargo/terraform/etc.) as needed.
  - Common pitfalls / sharp edges: Expecting the scaffolder to manage virtualenvs (it does not); assuming CI hardcodes
    tooling (it follows the manifest `tasks.*`); forgetting to record/maintain `tasks.*` when changing how a project is
    built/tested; underestimating the trust implications of Cookiecutter hooks.
- Persona 2: Contributor extending generators/templates (developer)
  - Goal: Add or improve internal templates/generators while keeping the system reproducible and testable offline.
  - Assumed tooling: PDM for this repo’s workflow; `python` on PATH; plus whatever a generator requires to run its
    recorded `tasks.*` (pdm/poetry/uv/npm/etc.).
  - Common pitfalls / sharp edges: Adding silent defaults/fallbacks; adding network dependencies to tests; writing
    generator behavior that isn’t captured in the manifest; changing template outputs without updating docs/tests.

## Notes For Agents

- Where the "product" lives (key directories): Template source is `templates/monorepo-root/{{cookiecutter.repo_slug}}/`;
  scaffold CLI is `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/scaffold.py`; registry is
  `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/registry.toml`; repo tests are `tests/`; binding
  process rules are `.agents/agents.md`.
- Commands to use for development in this repo: `pdm install`; `pdm run ruff format --check .`; `pdm run ruff check .`;
  `pdm run mypy .`; `pdm run deptry .`; `pdm run pytest`.
- Testing constraints (offline? network allowed? external binaries?): Offline only; no network calls; no real external
  binaries (use fakes/stubs in tests).
- Where plans/specs/artifacts must live: Under `.agents/` (plans in `.agents/plans/*`; todos/specs in `.agents/todos/*`;
  see `.agents/agents.md` for required structure).
- CI expectations (supported OS/Python versions, etc.): Template repo CI uses ubuntu-latest and currently tests Python 3.11
  and 3.12. This repo requires Python `>=3.11` (`pyproject.toml`) and targets `py311` for type checking/linting. Generated
  monorepos should remain cross-platform; scaffold tooling recommends Python 3.11+.
