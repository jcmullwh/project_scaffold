# Add an Architectural Overview of Templates, Scaffold Tooling, and Generated Outputs

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

After this change, a first-time maintainer has a single-page architecture overview that explains:

- what this template repo generates,
- where the scaffold CLI lives (in the generated monorepo),
- how `registry.toml` (configuration) and `monorepo.toml` (recorded manifest) interact, and
- how CI is driven by the manifest.

The overview must include a small diagram and link to concrete files so it is actionable, not aspirational.

## Progress

- [x] (2026-02-11) Create this ExecPlan from ticket `BLG-005` (fingerprint `eb81eab172648171`).
- [x] (2026-02-11) Ensure `docs/ARCHITECTURE.md` contains a diagram + narrative covering the generation flow and main components.
- [x] (2026-02-11) Link the architecture overview from the root `README.md` near the top.
- [x] (2026-02-11) Validate that every referenced path exists in the repo.

## Surprises & Discoveries

- Observation: The root `README.md` is intentionally short and previously did not link to any “how it works”/architecture page.
  Evidence: Prior to this work, `README.md` contained only dev setup and checks.

## Decision Log

- Decision: Maintain the architecture overview as a dedicated doc page (`docs/ARCHITECTURE.md`) and link to it from the root README.
  Rationale: The root README must stay action-oriented; an architecture map benefits from stable headings and room for context.
  Date/Author: 2026-02-11 / agent

## Outcomes & Retrospective

- Outcome:
  - `docs/ARCHITECTURE.md` now includes a small ASCII diagram plus a narrative “entry points and sources of truth” map.
  - Root `README.md` links to `docs/ARCHITECTURE.md` near the top for discoverability.

## Context and Orientation

Key entry points and sources of truth:

- Template entry point: `templates/monorepo-root/` (Cookiecutter template).
- Generated monorepo scaffolder:
  - CLI: `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/scaffold.py`
  - Registry (configuration): `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/registry.toml`
  - Manifest (recorded state): `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/monorepo.toml`
  - CI matrix: `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/ci_matrix.py`
- Offline validation: `tests/test_scaffold_monorepo_template.py` renders the template and runs scaffold commands against the output.

## Plan of Work

1. Create or update `docs/ARCHITECTURE.md` to include:
   - a diagram of the flow (template repo -> cookiecutter -> generated monorepo -> scaffold add -> manifest -> CI),
   - a short narrative describing each component and the data flow, and
   - concrete file/path links for each component.

2. Ensure root `README.md` links to `docs/ARCHITECTURE.md` near the top (in the evaluator/contributor entry area).

3. Validate that every referenced path exists with `Test-Path` (or by inspection).

## Concrete Steps

From repo root (`i:\\code\\project_scaffold`):

    Test-Path docs/ARCHITECTURE.md
    Test-Path templates/monorepo-root/cookiecutter.json
    Test-Path 'templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/scaffold.py'
    Test-Path tests/test_scaffold_monorepo_template.py

## Validation and Acceptance

- `docs/ARCHITECTURE.md` exists and contains:
  - a diagram,
  - a narrative explaining the main components and flows, and
  - concrete file references.
- Root `README.md` links to the architecture overview near the top.

## Idempotence and Recovery

Documentation-only change. Updating the architecture map is safe and should be done whenever entry points change.

## Artifacts and Notes

Source ticket: `BLG-005`  
Fingerprint: `eb81eab172648171`

## Interfaces and Dependencies

No runtime code changes required. Documentation-only change.
