# Unify and Publish a Canonical Scaffold Generation Path

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

After this change, documentation presents one canonical way to generate a monorepo from this template repo, and one explicit fallback way. Users should not have to guess whether to run `cookiecutter ...` directly or via `pdm run cookiecutter ...`, and they should understand when each path is appropriate.

The goal is to reduce “works on my machine” generation friction by making prerequisites and intent explicit:

- canonical path = minimal prerequisites, no template-repo dependency install
- fallback path = uses the template repo’s pinned dev dependencies via PDM

## Progress

- [x] (2026-02-11) Create this ExecPlan from ticket `BLG-004` (fingerprint `c2a52b35f6005432`).
- [x] (2026-02-11) Decide and document the canonical generation path and fallback path (with decision criteria).
- [x] (2026-02-11) Ensure root `README.md` and `docs/TROUBLESHOOTING.md` present consistent prerequisites and commands.
- [x] (2026-02-11) Validate both paths locally by rendering a monorepo and running `scaffold.py doctor`.

## Surprises & Discoveries

- Observation: The repo already documents direct `cookiecutter ...` usage and a no-dependency smoke path, but does not explicitly document `pdm run cookiecutter ...` as a supported fallback path.
  Evidence: Root `README.md` currently shows `cookiecutter templates/monorepo-root ...` and does not mention `pdm run cookiecutter`.

## Decision Log

- Decision: Canonicalize direct `cookiecutter templates/monorepo-root ...` for evaluators and minimal smoke, and document `pdm run cookiecutter ...` as the explicit fallback when you want to use the repo’s pinned dev dependency or when `cookiecutter` is not installed globally.
  Rationale: This aligns with the goal of a no-dependency “first success” path while still offering a stable, repo-managed fallback.
  Date/Author: 2026-02-11 / agent

## Outcomes & Retrospective

- Outcome:
  - Root `README.md` now documents both:
    - canonical generation via `cookiecutter templates/monorepo-root -o ...`, and
    - an explicit fallback via `pdm run cookiecutter ...` (after `pdm install`).
  - `docs/TROUBLESHOOTING.md` now documents the same fallback under the “cookiecutter: command not found” failure mode.
  - Both paths were validated locally via `--no-input` render and `scaffold.py doctor` (prints `OK`).

## Context and Orientation

This repository is the Cookiecutter template source. The template entry point is `templates/monorepo-root/`.

Cookiecutter can be invoked two ways:

- Directly via the `cookiecutter` CLI on PATH.
- Via the template repo’s dev environment: `pdm run cookiecutter ...` (Cookiecutter is a dev dependency in `pyproject.toml`).

Generating a monorepo produces a new repo directory on disk. The generated monorepo’s first command should be:

    python tools/scaffold/scaffold.py doctor

and it must be run from the generated monorepo root.

## Plan of Work

1. Update root `README.md` to document:
   - Canonical path (no template-repo dependency install): `cookiecutter templates/monorepo-root -o <output_dir>`
   - Fallback path (uses PDM environment): `pdm install` then `pdm run cookiecutter templates/monorepo-root -o <output_dir>`
   Include short “when to use which” decision criteria.

2. Update `docs/TROUBLESHOOTING.md` in the “cookiecutter not found” section to include the same fallback path and its prerequisites.

3. Validate both paths by rendering a monorepo and running `doctor`.

## Concrete Steps

From repo root (`i:\\code\\project_scaffold`):

    # Canonical path (requires cookiecutter on PATH)
    New-Item -ItemType Directory -Force .tmp | Out-Null
    cookiecutter templates/monorepo-root --no-input -o .tmp
    python .tmp/my-monorepo/tools/scaffold/scaffold.py doctor

    # Fallback path (requires PDM + repo dev deps installed)
    pdm install
    pdm run cookiecutter templates/monorepo-root --no-input -o .tmp
    python .tmp/my-monorepo/tools/scaffold/scaffold.py doctor

    # Cleanup
    Remove-Item -Recurse -Force .tmp

## Validation and Acceptance

- Root `README.md` documents one canonical and one fallback monorepo generation path, with explicit prerequisites and “when to use” guidance.
- `docs/TROUBLESHOOTING.md` gives the same guidance and does not contradict the root README.
- Both documented command sequences successfully generate a monorepo (no-input) and `doctor` prints `OK`.

## Idempotence and Recovery

All validation steps write into `.tmp/`. Delete `.tmp/` and re-run. If generation fails partway through, delete the output directory and retry.

## Artifacts and Notes

Source ticket: `BLG-004`
Fingerprint: `c2a52b35f6005432`

## Interfaces and Dependencies

No runtime code changes required. Documentation-only change plus local validation.
