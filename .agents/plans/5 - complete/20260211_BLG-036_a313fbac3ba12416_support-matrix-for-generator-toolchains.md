# Document a Compatibility/Support Matrix for Generator Toolchains

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

After this change, adopters can quickly answer “will this work in my environment?” by reading a support matrix that maps:

- generator ids (as defined in `tools/scaffold/registry.toml`),
- the OS/platform expectation (Linux/macOS/Windows),
- required external tools (python, cookiecutter, git, node/npm, go, cargo, terraform, pdm/poetry/uv),
- whether the generator is inherently networked (for example `npm create ...@latest`), and
- what is actually tested in this repository’s CI.

This reduces avoidable trial-and-error and makes support expectations explicit.

## Progress

- [x] (2026-02-11) Create this ExecPlan from ticket `BLG-036` (fingerprint `a313fbac3ba12416`).
- [x] (2026-02-11) Inventory built-in generators and their dependencies from the generated registry template.
- [x] (2026-02-11) Decide where the matrix lives (doc location) and how it is kept current.
- [x] (2026-02-11) Author the support matrix with explicit “tested vs not tested” statements and version guidance where we have evidence.
- [x] (2026-02-11) Link to the matrix from root docs and the generated monorepo scaffolder docs.

## Surprises & Discoveries

- Observation: The generated scaffolder docs already list included generators and minimal requirements, but not in a “matrix” form and without explicit OS/testing statements.
  Evidence: `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md` lists generators and requirements in prose.

## Decision Log

- Decision: Create the matrix as `tools/scaffold/SUPPORT_MATRIX.md` in the generated monorepo template, and link to it from both the generated scaffolder README and the template repo root README (as a preview path under `templates/`).
  Rationale: The support matrix is most useful when it ships with the generated monorepo (where adopters will look for it), while the template repo can still point at the preview copy.
  Date/Author: 2026-02-11 / agent

- Decision: Be explicit about what we do and do not test: use “tested in CI” vs “not covered by template repo CI” rather than making unsupported version claims.
  Rationale: Guessing tool versions undermines trust; a truthful “not tested here” is more actionable than a fake baseline.
  Date/Author: 2026-02-11 / agent

## Outcomes & Retrospective

- Outcome:
  - Added `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/SUPPORT_MATRIX.md` with a generator-by-generator toolchain matrix.
  - Linked the matrix from `tools/scaffold/README.md` and from the template repo root `README.md` (preview path).

## Context and Orientation

Generator definitions live in the generated monorepo registry template:

- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/registry.toml`

That file defines generator ids like `python_stdlib_copy`, `python_pdm_lib`, `node_vite`, etc. Each generator implies external tools via:

- the generator type (`copy`, `cookiecutter`, `command`),
- its `source` (local, external),
- its `command` (for `command` generators), and
- its recorded `tasks.*` (install/lint/test/build/etc.), which reference commands that must exist on PATH when executed.

The template repo CI (see `.github/workflows/ci.yml`) validates:

- Python-based template repo checks (ruff/mypy/deptry/pytest) on Ubuntu with Python 3.11/3.12.

It does not currently execute every generator’s external toolchain (node/go/rust/terraform) end-to-end.

## Plan of Work

1. Create `tools/scaffold/SUPPORT_MATRIX.md` in the generated monorepo template at `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/SUPPORT_MATRIX.md`. The doc should include:
   - A short explanation of what the matrix covers (generator toolchains, not “all possible templates”).
   - A statement of what platforms are intended to work (developer workstation support) and what CI currently tests.
   - A support matrix that includes, for each built-in generator id:
     - required tools on PATH to generate and to run tasks,
     - whether the generator may require network access,
     - any known constraints we can assert from the repo (for example “Python 3.11+ recommended for the scaffolder because of `tomllib`”).
   A table is acceptable here because the whole point is scannability; keep it concise.

2. Add links to the matrix:
   - Root `README.md` should link to the preview copy in `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/SUPPORT_MATRIX.md`.
   - `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md` should include a short “Support matrix” pointer to `tools/scaffold/SUPPORT_MATRIX.md` (in the generated monorepo).

3. Add a small “update policy” paragraph in `tools/scaffold/SUPPORT_MATRIX.md`:
   - When a generator is added/changed, update the matrix.
   - When CI coverage changes (new OS or toolchain tested), update the “tested in CI” column.

## Concrete Steps

From repo root (`i:\\code\\project_scaffold`):

    # Inventory built-in generators for the matrix.
    Get-Content -Path 'templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/registry.toml'

    # (After implementation) confirm the new doc exists.
    Test-Path 'templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/SUPPORT_MATRIX.md'

## Validation and Acceptance

- There is a support matrix doc at `docs/SUPPORT_MATRIX.md`.
- The matrix includes all generator ids present in `templates/.../tools/scaffold/registry.toml`.
- Each generator entry includes explicit:
  - required tools on PATH,
  - network expectations (if applicable), and
  - a truthful “tested in CI” statement (or “not tested here”).
- Root and generated docs link to the matrix.

## Idempotence and Recovery

Documentation-only change. If the matrix becomes stale, the fix is to update it alongside generator/CI changes.

## Artifacts and Notes

Source ticket: `BLG-036`  
Fingerprint: `a313fbac3ba12416`

## Interfaces and Dependencies

No new runtime dependencies. Documentation-only change.
