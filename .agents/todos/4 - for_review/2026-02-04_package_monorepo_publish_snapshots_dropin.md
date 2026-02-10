## Spec template for this project

### Task
Package a drop-in folder containing the `publish-snapshots` CI workflow plus the `tools/monorepo_publish` utility (and its deps) with a README so it can be copied into another repo and handed to an agent to implement.

### Goal
Produce a self-contained kit at `.agents/dropins/monorepo_publish_snapshots/` that:

- includes the exact files an agent should copy into a target repo (under `repo_root/`)
- includes a top-level `README.md` with copy/merge instructions, assumptions, required CI secrets, validation commands, and a suggested agent prompt

### Context
Canonical source material currently lives in the monorepo template:

- `templates/monorepo-root/{{cookiecutter.repo_slug}}/.github/workflows/publish-snapshots.yml`
- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/requirements-publish.txt`
- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/monorepo_publish/`

### Constraints
- Keep the kit copy/paste friendly and repo-agnostic.
- Do not include ephemeral build artifacts (virtualenvs, caches).

### Functional requirements
1) The kit contains these paths under `repo_root/`:
   - `.github/workflows/publish-snapshots.yml`
   - `tools/requirements-publish.txt`
   - `tools/monorepo_publish/**` (including `README.md`)

2) The kit README documents:
   - where each file is copied to in the target repo
   - tool assumptions (Python 3.11+, `packages/*/pyproject.toml`, PEP 621 metadata, `[tool.monorepo].status`)
   - required CI secrets/variables for publishing to GitLab PyPI
   - local validation commands (`--self-test`, `--dry-run`)
   - a suggested agent prompt

### Proposed flow (most important section)
Drop `.agents/dropins/monorepo_publish_snapshots/` into a target repo, then:

1) Copy everything under `repo_root/` into the repo root (merge `.github/` and `tools/`).
2) Ensure at least one monorepo Python package opts in to publishing via `[tool.monorepo].status != "internal"`.
3) Configure CI secrets/variables for GitLab PyPI.
4) Run the validation commands and fix any issues.

### Implementation plan
1) Create `.agents/dropins/monorepo_publish_snapshots/repo_root/` with `.github/` and `tools/` subtrees.
2) Copy the workflow, requirements file, and `tools/monorepo_publish/` from the monorepo template into the kit.
3) Add `.agents/dropins/monorepo_publish_snapshots/README.md` with the handoff instructions.

### Testing requirements (pytest, offline)
Not applicable. Minimal manual validation:

- `python tools/monorepo_publish/publish_snapshots.py --self-test`
- Create a minimal `packages/` with two eligible packages and run `--dry-run`

### Documentation updates
None outside the kit.

### Acceptance criteria
- The kit exists under `.agents/dropins/monorepo_publish_snapshots/` and is self-contained.
- No ephemeral artifacts are added to git status (no virtualenvs, caches, temp repos).

