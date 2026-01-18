# project-scaffold

This repo contains Cookiecutter templates and supporting tooling to generate a monorepo that can:

- bootstrap a new monorepo (“root scaffold”)
- add new subprojects over time
- use internal templates, external Cookiecutter templates, or command/copy generators
- remain toolchain-agnostic by defining per-project tasks explicitly in a manifest

Planning artifacts live in `.agents/`.

## Dev

This repo uses PDM for the development environment:

    pdm install
    pdm run pytest

