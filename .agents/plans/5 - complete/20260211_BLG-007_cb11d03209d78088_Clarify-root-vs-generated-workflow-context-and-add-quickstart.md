# Clarify Template-Repo vs Generated-Monorepo Context and Add Cross-Linked Quickstarts

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

After this change, the documentation makes it difficult to confuse the two workflow contexts:

- the template repository (this repo), where you develop templates and tests, and
- the generated monorepo, where you run `tools/scaffold/scaffold.py` to add projects and run tasks.

The docs should explicitly label which directory each command is intended to be run from, and they should cross-link between “generate a repo” and “use the generated repo” so a reader can follow an end-to-end path without guessing.

## Progress

- [x] (2026-02-11) Create this ExecPlan from ticket `BLG-007` (fingerprint `cb11d03209d78088`).
- [x] (2026-02-11) Audit `README.md` and the generated-monorepo template docs for implicit context switches.
- [x] (2026-02-11) Update root `README.md` to include a generation-to-first-scaffold quickstart with explicit working-directory labels.
- [x] (2026-02-11) Update generated monorepo docs (`templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md` and `.../tools/scaffold/README.md`) with a short “what repo am I in?” note.
- [x] (2026-02-11) Validate the full path (generate -> `scaffold.py doctor` -> add a project) is readable and copy-pasteable.

## Surprises & Discoveries

- Observation: The root README currently does not provide an end-to-end “generate then run scaffold” quickstart.
  Evidence: `README.md` contains no Cookiecutter or generated-monorepo command examples.

## Decision Log

- Decision: Treat “working directory” as a first-class part of every command snippet and repeat it even when it feels redundant.
  Rationale: The most common failure here is a correct command in the wrong directory; repetition is cheaper than confusion.
  Date/Author: 2026-02-11 / agent

## Outcomes & Retrospective

- Outcome:
  - Root `README.md` now explicitly labels template-repo vs generated-repo contexts and includes a “first scaffold” command (`scaffold.py add ... --no-install`).
  - Generated monorepo docs now state that commands are run from the generated monorepo root and clarify the template-repo vs generated-repo split.

## Context and Orientation

Two key READMEs exist in this repository:

- Template repo README (this repo): `README.md`
- Generated monorepo README (template copy): `templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md`

The generated monorepo’s scaffolder is documented at:

- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md`

Those `templates/...` files are the exact files that will appear in a generated monorepo after Cookiecutter runs, except that the placeholder paths contain literal `{{cookiecutter...}}` braces because this repository is the template source.

## Plan of Work

1. In `README.md`, add (or refine) a short end-to-end quickstart that begins in the template repo and ends in the generated repo:
   - Step 1 (template repo): run Cookiecutter to generate a repo into an output directory.
   - Step 2 (generated repo): `cd` into the generated repo.
   - Step 3 (generated repo): run `python tools/scaffold/scaffold.py doctor`.
   - Step 4 (generated repo): add a small project using a safe generator and `--no-install` (so success does not depend on additional toolchains).

2. In `templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md`, add a short note near the top clarifying:
   - “This is the generated repo; scaffold commands are run here.”
   - “If you are looking for the template repo that generated this, see the template repo’s root README.”
   Keep the reference generic (do not hardcode local paths). A short sentence is enough; the goal is to stop accidental back-navigation into the template repo.

3. In `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md`, ensure command examples assume they are run in the generated repo, and add a single line at the top stating that explicitly.

If other plans already added similar quickstarts, this plan should focus on making the context labels and cross-links unambiguous rather than duplicating content.

## Concrete Steps

From repo root (`i:\\code\\project_scaffold`):

    # Render the monorepo into .tmp/ and run a minimal end-to-end path.
    New-Item -ItemType Directory -Force .tmp | Out-Null
    pdm run cookiecutter templates/monorepo-root --no-input -o .tmp
    python .tmp/my-monorepo/tools/scaffold/scaffold.py doctor
    python .tmp/my-monorepo/tools/scaffold/scaffold.py add lib demo-lib --generator python_stdlib_copy --no-install

## Validation and Acceptance

- Root `README.md` contains an end-to-end quickstart with explicit working-directory labels for every command.
- Generated monorepo docs contain a short “you are in the generated repo” statement and avoid implying that scaffold commands belong in the template repo.
- Following the docs results in:
  - a generated repo directory on disk, and
  - `scaffold.py doctor` succeeding, and
  - one scaffolded project directory created with an entry recorded in `tools/scaffold/monorepo.toml` (in the generated repo).

## Idempotence and Recovery

The test render writes into `.tmp/`. Delete `.tmp/` to clean up and re-run. The `scaffold.py add ... --no-install` step can be repeated with a new project id (or remove the generated repo directory and regenerate).

## Artifacts and Notes

Source ticket: `BLG-007`  
Fingerprint: `cb11d03209d78088`

## Interfaces and Dependencies

No runtime logic changes required. This plan is documentation-only and uses existing Cookiecutter/scaffold entry points.
