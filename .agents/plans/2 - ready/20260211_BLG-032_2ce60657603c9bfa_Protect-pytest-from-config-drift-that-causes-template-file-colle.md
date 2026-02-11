# Protect Pytest From Config Drift That Causes Template File Collection Errors

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

After this change, if the repository’s pytest configuration drifts (for example, `testpaths` is removed or changed), pytest fails early with a clear, targeted error message explaining that collection outside `tests/` can pick up template files under `templates/` that contain Cookiecutter/Jinja placeholders and are not valid Python.

This turns a confusing “syntax error while collecting templates” failure into an actionable “fix your pytest config” failure.

## Progress

- [x] (2026-02-11) Create this ExecPlan from ticket `BLG-032` (fingerprint `2ce60657603c9bfa`).
- [ ] Codify the expected pytest config invariants (at minimum `testpaths = ["tests"]`).
- [ ] Add a runtime guard that checks the effective pytest config at startup and fails with a targeted message when misconfigured.
- [ ] Add a CI check that asserts the expected pytest config keys exist in `pyproject.toml`.
- [ ] Add/adjust tests if needed and run `pdm run pytest`.

## Surprises & Discoveries

- Observation: The current `pyproject.toml` already sets `testpaths = ["tests"]`, which is the desired behavior, but nothing prevents a future edit from removing it and causing template collection failures.
  Evidence: `pyproject.toml` contains `[tool.pytest.ini_options]` with `testpaths = ["tests"]`.

## Decision Log

- Decision: Enforce the invariant in two places: a pytest startup hook (to protect local runs) and a dedicated CI check script (to protect the config file itself).
  Rationale: The startup hook prevents confusing template collection failures even if CI is not run; the CI check prevents drift from landing unnoticed.
  Date/Author: 2026-02-11 / agent

## Outcomes & Retrospective

- Outcome: (fill in after implementation)

## Context and Orientation

Template files live under `templates/` and include non-Python placeholders like `{{cookiecutter.project_slug}}`. If pytest is allowed to recurse the repo, it can try to collect those files as tests or Python modules and fail with syntax errors that look unrelated to the real test suite.

Current pytest configuration is defined in `pyproject.toml`:

- `pyproject.toml` -> `[tool.pytest.ini_options]` -> `testpaths = ["tests"]`

The CI workflow for this template repo runs `pdm run pytest` as part of `.github/workflows/ci.yml`.

## Plan of Work

1. Add a pytest startup guard in a root-level `conftest.py` (repo root, not under `tests/`), so it is loaded even if test collection settings change. In that file:
   - Implement `pytest_configure(config)` (or a similarly early hook).
   - Read the effective `testpaths` via `config.getini("testpaths")`.
   - If `testpaths` is not exactly `["tests"]`, raise a `pytest.UsageError` with a message that:
     - explains why this invariant exists (avoid collecting `templates/`),
     - points to the correct location in `pyproject.toml`, and
     - suggests the fix (restore `testpaths = ["tests"]`).

2. Add a small CI check script under a stable path (for example `tools/check_pytest_config.py`) that:
   - parses `pyproject.toml` with the stdlib `tomllib`,
   - asserts that `[tool.pytest.ini_options].testpaths` exists and equals `["tests"]`, and
   - exits non-zero with a clear error message if it does not.

3. Update `.github/workflows/ci.yml` to run the new check script before `pdm run pytest`.

4. Add a small unit test that validates the guard’s error message shape (optional but preferred), and run `pdm run pytest`.

## Concrete Steps

From repo root (`i:\\code\\project_scaffold`):

    # Run the test suite (baseline).
    pdm run pytest

    # After implementation, validate the new CI check script locally.
    pdm run python tools/check_pytest_config.py

## Validation and Acceptance

- Local behavior:
  - With correct config, `pdm run pytest` passes.
  - If `testpaths` is removed or changed, pytest fails early with a message that explicitly mentions `testpaths = ["tests"]` and explains that template files under `templates/` are not valid Python for collection.
- CI behavior:
  - `.github/workflows/ci.yml` runs the config check script before pytest, and fails with a targeted message if the config drifts.

## Idempotence and Recovery

The guard is purely defensive. If it blocks a legitimate workflow, the remedy is to adjust the invariant intentionally (and update both the guard and the CI script together), rather than weakening it silently.

## Artifacts and Notes

Source ticket: `BLG-032`  
Fingerprint: `2ce60657603c9bfa`

## Interfaces and Dependencies

No new third-party dependencies. The CI check script should use the Python standard library (`tomllib`) and the guard should only depend on pytest’s public hooks.
