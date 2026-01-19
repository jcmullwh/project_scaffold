# Contributing

This repository is the source for Cookiecutter templates and the generated monorepo scaffold tooling.

## Development environment

This repo uses PDM for development.

    pdm install

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
