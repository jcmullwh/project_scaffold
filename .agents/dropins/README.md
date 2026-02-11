# `.agents/dropins/`

This directory contains "drop-in" bundles: self-contained code and configuration that can be copied ("transplanted") into
other repositories or into generated templates.

Drop-ins are not part of this template repo's runtime. They may:

- target different dependency sets than this repo,
- include their own `requirements-*.txt` files, and
- import third-party modules that are intentionally not declared in this repo's `pyproject.toml`.

## How to use a drop-in

Each drop-in folder should include its own README describing what to copy and how to validate it in the target repo.

Current drop-ins:

- `monorepo_publish_snapshots/`: snapshot (dev) publishing to GitLab PyPI.

## Maintenance rules (important)

Because drop-ins are transplantable assets, they must not cause this template repo's CI to fail due to dependency or
type-check mismatches.

When you add or change Python code under `.agents/dropins/`, ensure the template repo excludes it from:

- Deptry: `[tool.deptry].extend_exclude` in `pyproject.toml`
- Mypy: `[tool.mypy].exclude` in `pyproject.toml`
- Ruff: `[tool.ruff].exclude` in `pyproject.toml`

If you add a new drop-in directory, also add (or update) a short README in that directory explaining what it is and how
to validate it in the target repo.

