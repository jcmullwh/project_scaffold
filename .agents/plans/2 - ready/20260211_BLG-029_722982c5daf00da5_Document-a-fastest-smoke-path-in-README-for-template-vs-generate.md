# Document a “Fastest Smoke Path” With Explicit Template vs Generated Context

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

After this change, the root `README.md` provides a short “fastest smoke path” that explicitly separates:

- commands run in the template repo (this repository), and
- commands run in a generated monorepo (the output of Cookiecutter).

The smoke path is intentionally brief. Its purpose is to give a new reader a reliable first success that confirms they are in the right workflow context before they attempt deeper setup.

## Progress

- [x] (2026-02-11) Create this ExecPlan from ticket `BLG-029` (fingerprint `722982c5daf00da5`).
- [ ] Add a `Fastest smoke path` section near the top of `README.md`.
- [ ] Include two clearly separated tracks with explicit working-directory labels.
- [ ] Validate the described steps locally and ensure they do not rely on implicit context.

## Surprises & Discoveries

- Observation: The current root README does not provide any “fastest path” framing and does not mention generated-repo commands at all.
  Evidence: `README.md` contains only PDM dev commands.

## Decision Log

- Decision: Keep the smoke path minimal and safe by using `--no-input` Cookiecutter render + `scaffold.py doctor` for the generated track, and `pdm run pytest` for the contributor track.
  Rationale: These are low-ambiguity, high-signal checks: they validate the template can render and the generated scaffolder can run, and they validate the template repo’s tests run in the dev environment.
  Date/Author: 2026-02-11 / agent

## Outcomes & Retrospective

- Outcome: (fill in after implementation)

## Context and Orientation

The root README (`README.md`) currently reads like a developer README for this template repo. This repo’s actual output is a separate generated monorepo. The generated monorepo’s first command is typically:

    python tools/scaffold/scaffold.py doctor

But that command must be run in the generated monorepo root, not in this template repo.

## Plan of Work

Edit `README.md` and add a `Fastest smoke path` section near the top that contains two explicitly separated tracks, each with:

- a label for the required working directory (template repo vs generated repo),
- a short command sequence, and
- a concrete success checkpoint.

Track A (generated-monorepo evaluator path) should render a monorepo into `.tmp/` and run `doctor`. Track B (template repo contributor path) should set up the PDM environment and run `pdm run pytest` as the first success check, with a pointer to `CONTRIBUTING.md` for the full suite.

If other plans already added a similar section, this plan should ensure the section exists and that both tracks are present and clearly labeled, rather than duplicating content.

## Concrete Steps

From repo root (`i:\\code\\project_scaffold`), validate both tracks:

    # Generated monorepo smoke (no input render)
    New-Item -ItemType Directory -Force .tmp | Out-Null
    pdm run cookiecutter templates/monorepo-root --no-input -o .tmp
    python .tmp/my-monorepo/tools/scaffold/scaffold.py doctor
    Remove-Item -Recurse -Force .tmp

    # Template repo contributor smoke
    pdm install
    pdm run pytest

## Validation and Acceptance

- `README.md` includes a `Fastest smoke path` section near the top.
- The section contains two clearly separated tracks (template repo vs generated repo), each with explicit “run from here” labeling.
- Following the generated track results in a repo rendered under `.tmp/` and a successful `doctor` run.
- Following the contributor track results in a successful `pdm run pytest`.

## Idempotence and Recovery

The generated smoke writes into `.tmp/` and is safe to delete. PDM install can be re-run safely; if environment state is broken, delete the local venv and re-run `pdm install`.

## Artifacts and Notes

Source ticket: `BLG-029`  
Fingerprint: `722982c5daf00da5`

## Interfaces and Dependencies

No runtime code changes required. This plan is documentation-only.
