# Monorepo snapshot publishing (GitHub Actions -> GitLab PyPI)

This folder is a drop-in "implementation kit" you can copy into an existing monorepo to add:

- `tools/monorepo_publish/`: a small Python utility that publishes snapshot (dev) builds of eligible monorepo Python packages to a GitLab PyPI registry
- `.github/workflows/publish-snapshots.yml`: a GitHub Actions workflow that runs the publisher on push to `main` (and on manual dispatch)
- `tools/requirements-publish.txt`: runtime deps for the publisher (`build`, `twine`, etc.)

## What to copy into the target repo

Copy the contents of `repo_root/` into the target repo root (merge directories):

- `repo_root/.github/workflows/publish-snapshots.yml` -> `.github/workflows/publish-snapshots.yml`
- `repo_root/tools/requirements-publish.txt` -> `tools/requirements-publish.txt`
- `repo_root/tools/monorepo_publish/` -> `tools/monorepo_publish/`

## Assumptions (what the tool expects)

- Python 3.11+ (uses `tomllib`).
- Monorepo Python packages live under `packages/<package>/pyproject.toml`.
- Each publishable package uses PEP 621 metadata under `[project]` (Poetry-style `[tool.poetry]` will fail loudly).
- Publishing is opt-in per package via:

      [tool.monorepo]
      status = "incubator"  # or: supported / stable

  `internal` (or missing `[tool.monorepo]`) is treated as "do not publish".

## CI secrets / variables required

The workflow (and the publisher) read:

- `GITLAB_PYPI_PROJECT_ID` (required)
- `GITLAB_PYPI_USERNAME` (required)
- `GITLAB_PYPI_PASSWORD` (required)
- `GITLAB_BASE_URL` (optional; defaults to `https://gitlab.com`)

For GitHub Actions, add these as GitHub repository secrets.

## Local validation commands

From the target repo root:

    python -m pip install -r tools/requirements-publish.txt
    python tools/monorepo_publish/publish_snapshots.py --self-test
    python tools/monorepo_publish/publish_snapshots.py --dry-run

## Notes for agents implementing this in a specific repo

1) Copy the files, then run `--self-test` and `--dry-run` in CI or locally.
2) If the repo does not use `packages/` for Python libs, update `tools/monorepo_publish/discover.py` accordingly.
3) If publishing from GitLab CI instead of GitHub Actions, reuse the tool and wire the same env vars (the tool can use `CI_PIPELINE_ID` for snapshot ids).
4) Read `tools/monorepo_publish/README.md` in the target repo for the GitLab deploy-token walkthrough and install instructions (`pip` / `pdm`).

## Suggested agent prompt (copy/paste)

Implement snapshot publishing using the drop-in kit at `.agents/dropins/monorepo_publish_snapshots/`:

- Copy everything under `.agents/dropins/monorepo_publish_snapshots/repo_root/` into the repo root (merge with existing `.github/` and `tools/`).
- Confirm there is at least one Python package under `packages/` that should publish snapshots; set `[tool.monorepo].status` to a non-`internal` value for eligible packages.
- Ensure the CI secrets/variables `GITLAB_PYPI_PROJECT_ID`, `GITLAB_PYPI_USERNAME`, `GITLAB_PYPI_PASSWORD` (and optional `GITLAB_BASE_URL`) are documented for this repo.
- Run `python tools/monorepo_publish/publish_snapshots.py --self-test` and `--dry-run`; fix any issues.
