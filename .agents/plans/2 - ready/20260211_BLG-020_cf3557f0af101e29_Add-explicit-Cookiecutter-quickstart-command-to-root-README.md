# Add Explicit Cookiecutter Quickstart Command to Root README

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

After this change, the root `README.md` contains a single copy-pasteable Cookiecutter command that generates a monorepo from this repo’s template. A new evaluator should be able to reach “first success” (a generated repo exists on disk) without searching tests or template internals to guess the right command shape.

This plan focuses only on making the first generation step obvious and correct. It does not attempt to redesign the rest of the documentation structure (other plans may do that).

## Progress

- [x] (2026-02-11) Create this ExecPlan from ticket `BLG-020` (fingerprint `cf3557f0af101e29`).
- [ ] Add a `Quick Start` section near the top of `README.md` with an explicit `cookiecutter templates/monorepo-root ...` command.
- [ ] Document the two prompt variables (`repo_slug`, `repo_name`) and what they do, using the template’s `cookiecutter.json` as the source of truth.
- [ ] Validate that the documented command works (at least via a no-input render in a temp folder).

## Surprises & Discoveries

- Observation: The current root `README.md` does not contain any `cookiecutter ...` invocation, even though the repo’s primary output is a Cookiecutter template.
  Evidence: `README.md` contains only a short description and a `## Dev` section.

## Decision Log

- Decision: Use Cookiecutter’s built-in `-o/--output-dir` flag in the quickstart command and show a deterministic `--no-input` variant.
  Rationale: `-o` is the standard, discoverable way to control where the generated repo lands, and `--no-input` provides a stable “smoke render” that does not depend on interactive prompts.
  Date/Author: 2026-02-11 / agent

## Outcomes & Retrospective

- Outcome: (fill in after implementation)

## Context and Orientation

The Cookiecutter template entry point is the directory `templates/monorepo-root/`. Its prompt variables are defined in `templates/monorepo-root/cookiecutter.json`.

The repository currently uses PDM for development of the template repo itself, but generating a monorepo via Cookiecutter is an evaluator workflow that should not require understanding PDM. The quickstart should therefore mention `cookiecutter` as the required tool and keep the command self-contained.

## Plan of Work

Edit `README.md` and add a `Quick Start: Generate a monorepo` section near the top (above contributor/dev checks). The section must include:

1. A copy-pasteable command that works from the template repo root, using a local template path and `-o` to place the generated repo under a destination directory.
2. A short note describing the two prompt variables (`repo_slug` and `repo_name`), where they come from (`templates/monorepo-root/cookiecutter.json`), and what they affect.
3. A deterministic “smoke render” variant using `--no-input`, so a user can validate generation without being prompted.

Keep the command examples shell-friendly. If the quickstart references brace-containing paths under `templates/`, use quotes in the example to avoid PowerShell parsing issues.

## Concrete Steps

From repo root (`i:\\code\\project_scaffold`):

    # Confirm the template entrypoint exists and see the prompt variables.
    Get-Content templates/monorepo-root/cookiecutter.json

    # After editing README.md, do a no-input render into a temp directory (safe to delete).
    New-Item -ItemType Directory -Force .tmp | Out-Null
    pdm run cookiecutter templates/monorepo-root --no-input -o .tmp

    # Expect a repo at .tmp/my-monorepo (because repo_slug defaults to "my-monorepo").
    Test-Path .tmp/my-monorepo/README.md

## Validation and Acceptance

- Root `README.md` contains an explicit Cookiecutter generation command that is copy-pasteable.
- The README explains what `repo_slug` and `repo_name` are and where they are defined.
- Running the documented `--no-input` command successfully generates a repo directory under the chosen output directory.

## Idempotence and Recovery

The no-input smoke render writes into a new directory under `.tmp/`. It is safe to delete `.tmp/` and re-run.

## Artifacts and Notes

Source ticket: `BLG-020`  
Fingerprint: `cf3557f0af101e29`

## Interfaces and Dependencies

No runtime code changes. This plan only edits documentation and uses the existing Cookiecutter template at `templates/monorepo-root/`.
