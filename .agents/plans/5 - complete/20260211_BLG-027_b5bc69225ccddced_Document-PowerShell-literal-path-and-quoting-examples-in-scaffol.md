# Document PowerShell Literal Path and Quoting Examples in Scaffold Docs

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

After this change, users on Windows using PowerShell have copy-pasteable examples for:

- quoting `--vars k=v` pairs safely (especially when values contain spaces), and
- interacting with template paths that include special characters, using PowerShell’s `-LiteralPath` parameters where applicable.

The outcome is fewer “shell parsing” onboarding failures that look like product failures.

## Progress

- [x] (2026-02-11) Create this ExecPlan from ticket `BLG-027` (fingerprint `b5bc69225ccddced`).
- [x] (2026-02-11) Identify doc locations where command examples are fragile in PowerShell.
- [x] (2026-02-11) Add a Windows/PowerShell note section with tested examples (quote rules for `--vars`, and `-LiteralPath` usage for cmdlets).
- [x] (2026-02-11) Validate the examples in a PowerShell session against the actual repo layout.

## Surprises & Discoveries

- Observation: The generated monorepo scaffolder docs already contain one PowerShell quoting example for `--vars`, but do not explain literal-path handling for brace-containing template directories.
  Evidence: `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md` includes “quote values that contain spaces” but does not mention `-LiteralPath`.

- Observation: Unescaped `{{...}}` sequences in generated-doc templates can break monorepo generation because Cookiecutter/Jinja2 will attempt to render them.
  Evidence: Adding a literal ``{{cookiecutter...}}`` example caused `cookiecutter templates/monorepo-root --no-input ...` to fail with a Jinja2 `TemplateSyntaxError` until the placeholder examples were wrapped in `{% raw %}...{% endraw %}`.

## Decision Log

- Decision: Put PowerShell-specific guidance in the generated monorepo’s scaffold docs (where users actually run `scaffold.py`) and add a short pointer in the template repo’s root README if it links to brace-containing template paths.
  Rationale: The friction shows up when running real commands in the generated repo; guidance should be closest to the user’s workflow.
  Date/Author: 2026-02-11 / agent

## Outcomes & Retrospective

- Outcome:
  - `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md` now contains PowerShell-specific guidance for quoting `--vars` and inspecting brace-placeholder template paths with `-LiteralPath`.
  - The PowerShell `-LiteralPath` example was validated against an actual generated monorepo render.

## Context and Orientation

Where docs live:

- Generated monorepo scaffolder docs (template copy in this repo):
  - `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md`

PowerShell parsing pitfalls relevant to this project:

- Unquoted `{ ... }` in arguments is a script block in PowerShell; this matters when paths contain `{{cookiecutter...}}`.
- PowerShell cmdlets like `Get-Content`, `Get-ChildItem`, and `Set-Location` have `-LiteralPath` parameters that avoid wildcard/pattern interpretation and treat special characters as literal path characters.
- For external/native commands (like `python ...`), quoting the argument with single quotes is usually sufficient.

## Plan of Work

1. Update `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md`:
   - Add a `PowerShell notes` section (or expand the existing `Template variables (--vars)` section) with:
     - a recommended quoting style for `--vars` (single quotes around `k=v` when values can contain spaces), and
     - a note that brace-containing internal templates exist under `tools/templates/.../{{cookiecutter...}}/...` and should be referenced with quotes in PowerShell when used as arguments to commands or when inspecting with cmdlets.
   - Include at least one `Get-Content -LiteralPath '...'` example that demonstrates reading a file under a brace-containing directory.

2. If the root `README.md` links to template paths containing braces (for example `templates/monorepo-root/{{cookiecutter.repo_slug}}/...`), add a short inline note like “On PowerShell, quote brace-containing paths” and link to the generated scaffolder doc section.

## Concrete Steps

From repo root (`i:\\code\\project_scaffold`), validate examples with real paths:

    # Example: reading a generated-doc file under a brace-containing path (PowerShell cmdlet).
    Get-Content -LiteralPath 'templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md' | Select-Object -First 5

    # Example: quoting vars with spaces (native command).
    python -c "print('example only')"
    # (When validating in a generated repo, the command becomes:)
    # python tools/scaffold/scaffold.py add app my-app --vars 'description=My App'

## Validation and Acceptance

- The generated scaffolder README contains an explicit PowerShell section with:
  - at least one tested `--vars` quoting example, and
  - at least one tested `-LiteralPath` example for reading/inspecting a brace-containing path.
- The docs clearly separate “PowerShell cmdlet literal path” vs “native command argument quoting” guidance.

## Idempotence and Recovery

Documentation-only change. If examples are incorrect or confusing, revise them and re-validate by running the listed PowerShell commands.

## Artifacts and Notes

Source ticket: `BLG-027`
Fingerprint: `b5bc69225ccddced`

## Interfaces and Dependencies

No runtime code changes required. This plan only updates documentation.
