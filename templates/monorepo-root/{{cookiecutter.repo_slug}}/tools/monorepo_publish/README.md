# `tools/monorepo_publish`

This folder contains a small Python utility for publishing “snapshot” (dev) builds of monorepo Python packages to a GitLab PyPI registry.

It is intended for monorepos where Python libraries live under `packages/` (the default for kind `lib` in `tools/scaffold/registry.toml`).

## What it does

`publish_snapshots.py`:

- discovers Python packages in `packages/*/pyproject.toml`
- decides which packages are eligible for publishing based on `[tool.monorepo].status`
- computes a snapshot version like `1.2.3.dev123456`
- rewrites internal monorepo dependencies to pinned snapshot versions (so the published dists install cleanly)
- builds sdists/wheels and uploads them to a GitLab PyPI registry

## Package eligibility (`[tool.monorepo].status`)

Each Python package can set:

    [tool.monorepo]
    status = "internal"  # or: incubator / supported / stable

This publisher currently expects PEP 621 metadata under a `[project]` table. If a package uses Poetry-style
`[tool.poetry]` metadata, publishing will fail with an explicit error.

Rules:

- `status = "internal"` means **not published** (the default if the table is missing).
- Any non-`internal` status (`incubator`, `supported`, `stable`) makes the package eligible.
- If an eligible package depends on another monorepo package that is *not* eligible, publishing fails loudly (you must opt in the dependency too, or remove the dependency).

## Local usage

Install the publisher dependencies into whatever Python environment you want to run publishing from:

    python -m pip install -r tools/requirements-publish.txt

Self-test (does not require a repo):

    python tools/monorepo_publish/publish_snapshots.py --self-test

Dry run against this monorepo (prints the publish order + versions; validates rewrites; does not upload):

    python tools/monorepo_publish/publish_snapshots.py --dry-run

Publish (uploads to GitLab; requires env vars below):

    python tools/monorepo_publish/publish_snapshots.py

## Required env vars for publishing

`publish_snapshots.py` reads these environment variables:

- `GITLAB_PYPI_PROJECT_ID` (required): GitLab numeric project ID (or URL-encoded `group%2Fproject` path).
- `GITLAB_PYPI_USERNAME` (required): GitLab deploy token username, personal access token name, or `gitlab-ci-token`.
- `GITLAB_PYPI_PASSWORD` (required): the token value (deploy token / personal access token / `$CI_JOB_TOKEN`).
- `GITLAB_BASE_URL` (optional): defaults to `https://gitlab.com` (set this for self-hosted GitLab).

The upload URL is:

    ${GITLAB_BASE_URL}/api/v4/projects/${GITLAB_PYPI_PROJECT_ID}/packages/pypi

## GitHub Actions workflow

This template includes `.github/workflows/publish-snapshots.yml`, which runs on:

- push to `main`
- manual `workflow_dispatch`

It expects GitHub secrets:

- `GITLAB_BASE_URL` (optional)
- `GITLAB_PYPI_PROJECT_ID`
- `GITLAB_PYPI_USERNAME`
- `GITLAB_PYPI_PASSWORD`

## GitLab walkthrough (deploy token recommended)

Goal: publish *from CI* to a GitLab PyPI registry using a least-privilege token.

1) In GitLab, pick the project that will host the PyPI registry (often the same repo mirrored into GitLab).

2) Get the project ID:
   - GitLab UI: **Settings → General → Project ID**
   - Or use the project path as a URL-encoded string like `my-group%2Fmy-project`

3) Create a **deploy token** with scopes:
   - `read_package_registry`
   - `write_package_registry`

   Record:
   - deploy token username (looks like `gitlab+deploy-token-12345`)
   - deploy token value (the secret)

4) Provide the values to CI:

- For GitHub Actions: add the four values above as GitHub repository secrets.
- For GitLab CI: add them as CI/CD variables (mask the password/token).

### GitLab CI example job

If you prefer to publish from GitLab CI (instead of GitHub Actions), this job uses the built-in job token:

    publish:snapshots:
      image: python:3.11
      rules:
        - if: $CI_COMMIT_BRANCH == "main"
      variables:
        GITLAB_BASE_URL: $CI_SERVER_URL
        GITLAB_PYPI_PROJECT_ID: $CI_PROJECT_ID
        GITLAB_PYPI_USERNAME: "gitlab-ci-token"
        GITLAB_PYPI_PASSWORD: $CI_JOB_TOKEN
      script:
        - python -m pip install --upgrade pip
        - python -m pip install -r tools/requirements-publish.txt
        - python tools/monorepo_publish/publish_snapshots.py --self-test
        - python tools/monorepo_publish/publish_snapshots.py

## Installing from GitLab PyPI

GitLab’s “simple index” URL is:

    ${GITLAB_BASE_URL}/api/v4/projects/${GITLAB_PYPI_PROJECT_ID}/packages/pypi/simple

### `pip`

Install a specific version from the GitLab project registry:

    pip install --no-index --index-url "https://${GITLAB_PYPI_USERNAME}:${GITLAB_PYPI_PASSWORD}@gitlab.example.com/api/v4/projects/<project_id>/packages/pypi/simple" <package_name>==<version>

Notes:

- `--no-index` prevents a fallback to public PyPI. Without it, GitLab may forward requests to `pypi.org` when a package is missing.
- If you use multiple `--index-url/--extra-index-url` entries for the *same host* with different credentials, `pip` can behave unexpectedly; prefer using a single token per host.

### `pdm`

Option A (env var expansion; don’t commit secrets):

1) Add an index source to `pyproject.toml`:

        [[tool.pdm.source]]
        name = "gitlab"
        url = "https://${GITLAB_PYPI_USERNAME}:${GITLAB_PYPI_PASSWORD}@gitlab.example.com/api/v4/projects/${GITLAB_PYPI_PROJECT_ID}/packages/pypi/simple"

2) Set `GITLAB_PYPI_*` in your shell and run:

        pdm add --source gitlab <package_name>

Option B (store credentials locally via `pdm config`):

1) Commit only the URL (no credentials) in `pyproject.toml`:

        [[tool.pdm.source]]
        name = "gitlab"
        url = "https://gitlab.example.com/api/v4/projects/<project_id>/packages/pypi/simple"

2) Configure credentials in your local PDM config (not in git):

        pdm config pypi.gitlab.username "<username>"
        pdm config pypi.gitlab.password "<token>"
