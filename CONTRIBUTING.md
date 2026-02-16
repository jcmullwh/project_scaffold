# Contributing

This repository is the source for Cookiecutter templates and the generated monorepo scaffold tooling.

## Development environment

This repo uses PDM for development.

    pdm install

## If `pdm install` hangs on Windows

Treat "hang" as no new output for 5 or more minutes.

Try:

    pdm info
    pdm install

If you need an immediate first-success fallback (without PDM), run:

    python -m pip install --upgrade pip
    python -m pip install cookiecutter pytest
    cookiecutter templates/monorepo-root --no-input -o .tmp
    python .tmp/my-monorepo/tools/scaffold/scaffold.py doctor
    python -m pytest -q tests/test_scaffold_monorepo_template.py

This fallback is for unblocking only; return to the PDM workflow for normal contribution and full checks.

## Quality checks

Run all checks locally:

    pdm run ruff format --check .
    pdm run ruff check .
    pdm run mypy .
    pdm run deptry .
    pdm run pytest

Auto-format:

    pdm run ruff format .

## pre-commit (optional)

Install hooks:

    pdm run pre-commit install

Run hooks on all files:

    pdm run pre-commit run --all-files

## Drop-ins (`.agents/dropins/`)

This repo includes transplantable "drop-in" bundles under `.agents/dropins/` that are meant to be copied into other
repos/templates and are not part of this template repo's runtime.

See `.agents/dropins/README.md` for purpose and maintenance rules (including required tool excludes).
