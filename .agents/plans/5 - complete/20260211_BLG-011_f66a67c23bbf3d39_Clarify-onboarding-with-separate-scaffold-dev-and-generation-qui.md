# Clarify Onboarding With Separate Template-Repo Dev vs Generated-Monorepo Tracks

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

After this change, the root `README.md` immediately offers two clearly labeled onboarding tracks:

1. “Generate and use a monorepo” (evaluator/end-user path).
2. “Contribute to the template repo” (developer path for this repository).

Each track has a short, self-contained “first success” command sequence and an explicit success checkpoint. The intent is to stop users from running commands in the wrong directory and mistaking predictable context errors for broken setup.

## Progress

- [x] (2026-02-11) Create this ExecPlan from ticket `BLG-011` (fingerprint `f66a67c23bbf3d39`).
- [x] (2026-02-11) Restructure `README.md` so the first screen offers two tracks with explicit “run this in directory X” context labels.
- [x] (2026-02-11) Add an end-to-end generation-first quickstart (template repo -> generated monorepo -> `scaffold.py doctor`) with copy-paste commands and an explicit success checkpoint.
- [x] (2026-02-11) Ensure contributor/dev setup remains correct and points to `CONTRIBUTING.md` for details.
- [x] (2026-02-11) Validate that both tracks are runnable (no-input render + `doctor`, and `pdm run pytest`).

## Surprises & Discoveries

- Observation: The current root `README.md` only documents template-repo development (PDM + checks) and does not contain a generation-first evaluator path.
  Evidence: `README.md` includes `## Dev` and no “generate a monorepo” instructions.

## Decision Log

- Decision: Structure the root README as “choose your goal” rather than a linear narrative.
  Rationale: The dominant failure mode here is running a correct command in the wrong repo. A forced fork makes the context boundary explicit.
  Date/Author: 2026-02-11 / agent

## Outcomes & Retrospective

- Outcome:
  - `README.md` now begins with a “Choose Your Path” fork that separates evaluator vs contributor workflows.
  - The evaluator track is end-to-end and includes a concrete success checkpoint (`doctor` prints `OK`).
  - The contributor track contains a minimal “first success” (`pdm run pytest`) and points to `CONTRIBUTING.md` for the full suite.

## Context and Orientation

This repo is a Cookiecutter template repository. It generates a monorepo whose primary CLI is `tools/scaffold/scaffold.py` (stdlib-only Python, designed to run with plain `python`).

Relevant files:

- Template repo docs:
  - `README.md` (to restructure).
  - `CONTRIBUTING.md` (dev workflow; PDM; quality checks).
- Template entry point:
  - `templates/monorepo-root/` and `templates/monorepo-root/cookiecutter.json`.
- Generated monorepo docs (as template preview copies in this repo):
  - `templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md`
  - `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md`

The generated monorepo is a different repository on disk after Cookiecutter runs. Commands like `python tools/scaffold/scaffold.py ...` are meant to run in the generated monorepo, not in this template repo.

## Plan of Work

Edit `README.md` so the top of the file (before any contributor tooling) is an explicit fork. The fork should be short and action-oriented:

1. Track A: “Generate and use a monorepo (recommended for evaluation)”
   - Provide a copy-paste Cookiecutter command (refer to the plan in `BLG-020` if implemented; otherwise add it here).
   - Tell the reader what directory to `cd` into after generation.
   - Provide the first success command: `python tools/scaffold/scaffold.py doctor`.
   - Include a success checkpoint describing what they should see (for example: “doctor prints OK and lists detected tools/config; exit code 0”).

2. Track B: “Contribute to the template repo (develop templates/tests)”
   - Provide the minimal PDM setup and “first success” test command (for example `pdm install` then `pdm run pytest`).
   - Link to `CONTRIBUTING.md` for the full lint/typecheck/deptry suite.

Keep commands labeled with their required working directory, using short context tags like “(template repo)” and “(generated repo)”.

## Concrete Steps

From repo root (`i:\\code\\project_scaffold`):

    # Inspect current docs to understand what is currently missing.
    Get-Content README.md
    Get-Content CONTRIBUTING.md

After editing `README.md`, run a no-input render as a smoke test and then run the generated doctor command:

    New-Item -ItemType Directory -Force .tmp | Out-Null
    pdm run cookiecutter templates/monorepo-root --no-input -o .tmp
    python .tmp/my-monorepo/tools/scaffold/scaffold.py doctor

## Validation and Acceptance

- The first screen of `README.md` forces an explicit choice between “Generate/use monorepo” and “Contribute to template repo.”
- Each track has:
  - at least one copy-paste command sequence,
  - an explicit “run this in directory X” label, and
  - a concrete success checkpoint.
- A no-input render to `.tmp/` succeeds and `python .../tools/scaffold/scaffold.py doctor` runs with exit code 0.

## Idempotence and Recovery

The generation smoke test writes under `.tmp/`. It is safe to delete `.tmp/` and re-run.

## Artifacts and Notes

Source ticket: `BLG-011`  
Fingerprint: `f66a67c23bbf3d39`

## Interfaces and Dependencies

No runtime behavior changes required. This plan is documentation-only and uses existing Cookiecutter and scaffold tool entry points.
