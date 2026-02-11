# Clarify Meta-Repository Model and Evaluator Entry Path in Docs

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

After this change, a first-time evaluator can open the root `README.md` and immediately understand that `project_scaffold` is a template repository that generates a separate monorepo repository. They can also see, without hunting, the shortest “first success” path: generate a monorepo via Cookiecutter and then run the generated monorepo’s `tools/scaffold/scaffold.py doctor`.

This work is documentation-only. It changes the story at the top of the repo so evaluators do not confuse “template repo development” with “using the generated monorepo.”

## Progress

- [x] (2026-02-11) Create this ExecPlan from ticket `BLG-018` (fingerprint `a28a81f37504adb2`).
- [ ] Update root `README.md` with an evaluator-first orientation block and clear entry-point links.
- [ ] Ensure contributor setup details remain in `CONTRIBUTING.md` (and avoid mixing contributor steps into evaluator quickstart).
- [ ] Validate the root README’s links/paths and that the “first success” path is copy-pasteable and context-labeled.

## Surprises & Discoveries

- Observation: The current root `README.md` is primarily a “dev environment” note (PDM + quality checks) and does not explain the template-vs-generated split.
  Evidence: `README.md` contains only a high-level description and a `## Dev` section.

## Decision Log

- Decision: Put the evaluator orientation at the very top of `README.md` and treat contributor workflow as a secondary track linked to `CONTRIBUTING.md`.
  Rationale: Evaluators need to decide “what is this repo” and “how do I see it work” before they care about lint/typecheck tools.
  Date/Author: 2026-02-11 / agent

## Outcomes & Retrospective

- Outcome: (fill in after implementation)

## Context and Orientation

This repository is the template source. Its primary deliverable is a Cookiecutter template at `templates/monorepo-root/` that renders a new monorepo repository.

Important files to reference in docs:

- `README.md`: the root doc page that currently lacks an evaluator-first entry path.
- `CONTRIBUTING.md`: contributor-focused development environment instructions (PDM + checks).
- `templates/monorepo-root/cookiecutter.json`: the Cookiecutter prompt variables and copy-without-render rules for the generated monorepo.
- `templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md`: the README that will appear in the generated monorepo.
- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md`: the generated monorepo’s scaffolder CLI docs (what end users use after generation).

Note: paths inside `templates/` include literal `{{cookiecutter...}}` braces because they are template placeholders. On PowerShell, those braces must be quoted when used as arguments.

## Plan of Work

Edit `README.md` to lead with an “orientation block” that answers, in plain language:

1. What this repo is (a template repo that generates another repo).
2. Who should read what:
   - Evaluators: follow the “Generate and run” quickstart.
   - Contributors: follow `CONTRIBUTING.md` and the dev section (kept short in `README.md`).
3. Where the generated monorepo docs live:
   - In a generated repo: `README.md` and `tools/scaffold/README.md`.
   - In this template repo (for preview): the corresponding files under `templates/monorepo-root/{{cookiecutter.repo_slug}}/...`.

Keep the change additive and low-risk: do not delete contributor information, but move it below the evaluator path and link to `CONTRIBUTING.md` for the full details.

## Concrete Steps

From repo root (`i:\\code\\project_scaffold`):

    # Inspect current docs
    Get-Content README.md
    Get-Content CONTRIBUTING.md

    # After edits, sanity-check the referenced template paths exist
    Test-Path templates/monorepo-root/cookiecutter.json
    Test-Path 'templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md'
    Test-Path 'templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md'

## Validation and Acceptance

- A first-time reader can answer “what is this repo?” from the first screen of `README.md` (without scrolling to “Dev”).
- The root README explicitly distinguishes:
  - commands run in the template repo (this repo), and
  - commands run in the generated monorepo.
- The root README points to the generated monorepo docs (`README.md` and `tools/scaffold/README.md`) and also points to the preview copies under `templates/`.

## Idempotence and Recovery

This is a documentation-only change. Re-running the steps is safe. If wording is unclear, revise `README.md` without affecting runtime behavior.

## Artifacts and Notes

Source ticket: `BLG-018`  
Fingerprint: `a28a81f37504adb2`

## Interfaces and Dependencies

No new runtime dependencies. No changes to the scaffold tool or templates are required for this plan.
