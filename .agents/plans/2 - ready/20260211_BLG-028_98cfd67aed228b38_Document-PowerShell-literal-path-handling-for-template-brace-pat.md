# Document PowerShell Literal-Path Handling for Template Brace Paths (`{{...}}`)

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

After this change, documentation that references template placeholder directories like `{{cookiecutter.repo_slug}}` is safe to follow on Windows PowerShell. Users should be able to copy/paste path examples that contain `{{...}}` without PowerShell treating them as script blocks or otherwise mis-parsing them.

This plan focuses specifically on brace-containing *paths*. General PowerShell quoting guidance for `--vars` is covered by a separate plan (or can be referenced if already implemented).

## Progress

- [x] (2026-02-11) Create this ExecPlan from ticket `BLG-028` (fingerprint `98cfd67aed228b38`).
- [ ] Enumerate docs that mention brace-containing paths (especially under `templates/` and `tools/templates/`).
- [ ] Add PowerShell-safe examples that use single-quoted paths and `-LiteralPath` for cmdlets.
- [ ] Add a short cross-shell note (bash/cmd/PowerShell) that clarifies why braces require quoting in PowerShell.
- [ ] Validate examples in PowerShell against the current repo contents.

## Surprises & Discoveries

- Observation: This repo contains many literal brace placeholder directories under both `templates/` and the generated monorepo’s internal template trees.
  Evidence: `templates/monorepo-root/{{cookiecutter.repo_slug}}/...` and `.../tools/templates/internal/.../{{cookiecutter.project_slug}}/...` exist in the template source.

## Decision Log

- Decision: Prefer single-quoted string literals for brace paths in examples and use `-LiteralPath` when the command is a PowerShell cmdlet.
  Rationale: Single quotes prevent interpolation; `-LiteralPath` avoids wildcard/pattern processing and makes intent explicit.
  Date/Author: 2026-02-11 / agent

## Outcomes & Retrospective

- Outcome: (fill in after implementation)

## Context and Orientation

Brace placeholder paths occur because this repository stores templates. Examples:

- Template preview paths:
  - `templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md`
  - `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md`
- Generated monorepo internal templates (copied without render):
  - `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/templates/internal/python-stdlib-cookiecutter/{{cookiecutter.project_slug}}/...`

On PowerShell, an unquoted `{ ... }` sequence is parsed as a script block. Paths containing `{{...}}` must therefore be wrapped in quotes whenever they appear as command arguments. When using PowerShell cmdlets (like `Get-Content` or `Set-Location`), `-LiteralPath` should be used with such paths.

## Plan of Work

1. Update root `README.md` (if it references preview copies under `templates/.../{{cookiecutter...}}/...`):
   - Ensure every brace-containing path in examples is quoted for PowerShell (single quotes).
   - Add a short “PowerShell note” callout near the first brace path: “On PowerShell, quote paths with `{{...}}`.”

2. Update generated monorepo docs where appropriate:
   - `templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md` and/or `.../tools/scaffold/README.md` should include a short section that shows how to inspect internal template directories on PowerShell safely (using `Get-ChildItem -LiteralPath` or `Set-Location -LiteralPath`).

3. Validate every example by executing it in PowerShell against real paths in this template repo.

## Concrete Steps

From repo root (`i:\\code\\project_scaffold`), validate brace-path examples:

    # Cmdlet examples should use -LiteralPath.
    Get-Content -LiteralPath 'templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md' | Select-Object -First 3
    Get-ChildItem -LiteralPath 'templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/templates/internal' | Select-Object -First 5

    # For navigation, prefer -LiteralPath as well.
    Set-Location -LiteralPath 'templates/monorepo-root/{{cookiecutter.repo_slug}}'
    Set-Location -LiteralPath 'i:\\code\\project_scaffold'

## Validation and Acceptance

- Any documentation that contains brace placeholder paths includes PowerShell-safe variants.
- At least one doc page shows working PowerShell cmdlet examples using `-LiteralPath` against a `{{...}}` path.
- Copy/pasting the documented PowerShell examples executes without parse errors.

## Idempotence and Recovery

Documentation-only change. If examples are incorrect, fix the doc and re-run the listed PowerShell commands.

## Artifacts and Notes

Source ticket: `BLG-028`  
Fingerprint: `98cfd67aed228b38`

## Interfaces and Dependencies

No runtime code changes required. This plan only updates documentation.
