# Document Primary Entry Points and an Architecture Map

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

After this change, an evaluator can find a single “architecture map” document that answers:

- what the primary entry points are (commands and files),
- where the source of truth lives (registry vs manifest vs templates),
- how the generated monorepo relates to this template repo, and
- which files to read first depending on their goal.

This reduces mental-model confusion and prevents misuse of internal-only surfaces.

## Progress

- [x] (2026-02-11) Create this ExecPlan from ticket `BLG-035` (fingerprint `569c90e92bf14695`).
- [ ] Inventory entry points and configuration surfaces in both the template repo and the generated monorepo template.
- [ ] Write a single architecture map doc page with an entry-point index and repo layout map.
- [ ] Link to the architecture map from the root `README.md`.
- [ ] Validate all referenced paths and commands exist and are current.

## Surprises & Discoveries

- Observation: The root `README.md` is currently too small to convey entry points; the richest “how it works” content is embedded in the generated monorepo’s `tools/scaffold/README.md`, which is not linked from the root.
  Evidence: `README.md` has no links to `templates/monorepo-root/{{cookiecutter.repo_slug}}/...`.

## Decision Log

- Decision: Create a dedicated `docs/ARCHITECTURE.md` in the template repo rather than trying to squeeze the architecture map into the root README.
  Rationale: The architecture map benefits from stable headings and room for nuance; the root README should stay action-oriented and link out.
  Date/Author: 2026-02-11 / agent

## Outcomes & Retrospective

- Outcome: (fill in after implementation)

## Context and Orientation

There are two related repositories in play:

1. The template repo (this repository): contains Cookiecutter templates and tests for generating another repo.
2. The generated monorepo (output of Cookiecutter): contains `tools/scaffold/scaffold.py` and a manifest-driven CI model.

Key files and directories in the template repo:

- `templates/monorepo-root/`: Cookiecutter template entry point.
- `templates/monorepo-root/cookiecutter.json`: Cookiecutter prompt variables and copy-without-render config.
- `templates/monorepo-root/{{cookiecutter.repo_slug}}/`: the generated monorepo content as template source.
- `tests/test_scaffold_monorepo_template.py`: offline tests that render the template and exercise the generated scaffolder.
- `.github/workflows/ci.yml`: CI for the template repo itself.
- `USERS.md`: user notes and missions (useful context, but not a substitute for architecture docs).

Key files in the generated monorepo template:

- `README.md`: generated repo orientation.
- `tools/scaffold/scaffold.py`: the generated scaffolder CLI.
- `tools/scaffold/registry.toml`: kinds and generator definitions (config input).
- `tools/scaffold/monorepo.toml`: created projects and task commands (source of truth for execution).
- `tools/scaffold/ci_matrix.py`: emits a CI matrix based on the manifest.

## Plan of Work

1. Create `docs/ARCHITECTURE.md` in the template repo. The doc must include:
   - A “Start here” section that points evaluators to:
     - generation quickstart (root README),
     - generated monorepo docs (generated README and `tools/scaffold/README.md`),
     - contributor setup (CONTRIBUTING).
   - An “Entry points” section that lists, in plain language:
     - how to generate a monorepo (`cookiecutter templates/monorepo-root ...`),
     - how to run the generated scaffold tool (`python tools/scaffold/scaffold.py ...`),
     - how CI is driven (manifest -> matrix -> tasks).
   - A “Source of truth” section explaining registry vs manifest and how they interact.
   - A “Repo layout map” section describing the major directories in both the template repo and generated monorepo.

2. Add a link to `docs/ARCHITECTURE.md` from the root `README.md` near the top (after the quickstart fork), so evaluators can find it immediately.

3. Validate the doc by clicking through every referenced path (or using `Test-Path`) and ensuring it exists in the current tree.

## Concrete Steps

From repo root (`i:\\code\\project_scaffold`):

    # Confirm the key files exist so the architecture doc can refer to them.
    Test-Path templates/monorepo-root/cookiecutter.json
    Test-Path 'templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/scaffold.py'
    Test-Path 'templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/registry.toml'
    Test-Path tests/test_scaffold_monorepo_template.py

    # (After implementation) confirm the new doc exists.
    Test-Path docs/ARCHITECTURE.md

## Validation and Acceptance

- There is one architecture map doc page at `docs/ARCHITECTURE.md`.
- It lists primary entry points and configuration surfaces for both the template repo and the generated monorepo.
- Every referenced path exists in the current repo and every command is syntactically correct.
- Root `README.md` links to the architecture map in a high-visibility location.

## Idempotence and Recovery

Documentation-only change. Re-running validation is safe. If the repo layout changes, update `docs/ARCHITECTURE.md` and keep links current.

## Artifacts and Notes

Source ticket: `BLG-035`  
Fingerprint: `569c90e92bf14695`

## Interfaces and Dependencies

No runtime dependencies. Documentation-only change.
