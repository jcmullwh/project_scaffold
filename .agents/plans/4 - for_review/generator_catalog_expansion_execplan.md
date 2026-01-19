# Expand generator catalog beyond PDM and harden scaffold + CI: Poetry/uv/node and manifest correctness

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`. If `.agents/agents.md` exists, it is binding.

## Purpose / Big Picture

This work makes the generated monorepo scaffolding system genuinely polyglot and robust.

After this change, a generated monorepo can:

- Scaffold Python projects managed by Poetry and/or uv (not just PDM).
- Scaffold non-Python projects such as Node (npm) using a command-based generator.
- Run CI for mixed toolchains by installing dependencies and running tasks per project.
- Maintain a correct, stable manifest (`tools/scaffold/monorepo.toml`) without losing user-added metadata, and fail early when CI expects tasks that are missing.

How to see it working: in a generated monorepo, you can add:

- a Poetry Python app and run install/test tasks
- a Node app and run install/build tasks

and CI will set up the right tools and run the configured tasks.

## Progress

- [x] (2026-01-19) Add at least one Poetry generator and one uv generator (either internal templates or documented external templates).
- [x] (2026-01-19) Add at least one Node generator using the command generator type (npm create).
- [x] (2026-01-19) Improve scaffold tool manifest writing to preserve unknown keys and add schema versioning.
- [x] (2026-01-19) Add strict validation: if a project kind enables CI for a task, the generator must define the task (or the add command must error loudly).
- [x] (2026-01-19) Extend generated monorepo CI to set up additional toolchains (at minimum terraform and node; optionally rust/go as examples).
- [x] (2026-01-19) Add template repo tests covering: manifest preservation, task/CI consistency, and at least one non-PDM generator being recorded correctly.

## Surprises & Discoveries

- Observation: Even “optional” metadata in `monorepo.toml` can be lost if the manifest writer only emits a fixed subset of keys.
  Evidence: The previous `_write_manifest` wrote only known keys and dropped unknown per-project metadata.

## Decision Log

- Decision: Add `python_poetry_app` and `python_uv_app` as internal copy generators.
  Rationale: Copy-based generators are offline-friendly to scaffold and don’t require `cookiecutter` for generation; tool-specific binaries are only needed when running tasks.
  Date/Author: 2026-01-19 / Codex
- Decision: Add `node_vite` as a command generator and introduce kind `web` with `ci.build=true` and `ci.lint/ci.test=false`.
  Rationale: Node projects can participate in CI with a realistic `install` + `build` path without assuming lint/test scripts exist out of the box.
  Date/Author: 2026-01-19 / Codex
- Decision: Add `schema_version = 1` to `tools/scaffold/monorepo.toml` and write manifests in a non-lossy way.
  Rationale: Enables future schema evolution and preserves user-added metadata across scaffold operations.
  Date/Author: 2026-01-19 / Codex
- Decision: Enforce task name validation (`^[a-zA-Z0-9_-]+$`) and reject dots.
  Rationale: Prevent ambiguous TOML dotted keys like `tasks.foo.bar` from creating unintended nesting and hard-to-debug manifest corruption.
  Date/Author: 2026-01-19 / Codex
- Decision: Keep template repo tests offline by validating recorded tasks and manifest structure without invoking Poetry/uv/npm.
  Rationale: Ensures the template repo’s CI remains deterministic and does not depend on network or external tool installs.
  Date/Author: 2026-01-19 / Codex

## Outcomes & Retrospective

- Outcome: The default registry now includes Poetry (`python_poetry_app`), uv (`python_uv_app`), and Node (`node_vite`) generators and a `web` kind for build-focused Node CI.
- Outcome: The scaffold tool preserves unknown manifest keys and records a `schema_version`, enabling stable, evolvable manifest semantics.
- Outcome: Generated monorepo CI sets up Terraform conditionally and continues to set up Node/Python per project.
- Outcome: Offline template repo tests cover manifest preservation, CI/task strictness enforcement, and non-PDM generator recording.

## Context and Orientation

The generated monorepo contains a scaffold CLI at:

- `tools/scaffold/scaffold.py`

This CLI reads:

- `tools/scaffold/registry.toml` (kinds + generators)
and writes/reads:
- `tools/scaffold/monorepo.toml` (projects + tasks)

A “generator” is a config entry that describes how to create a project and what tasks exist. Supported generator types are:

- `copy`: copies an internal skeleton directory with token substitutions
- `cookiecutter`: runs cookiecutter on a local or external template; external templates are gated by trust/pinning
- `command`: runs a command (argv list) to generate a project (for example, `npm create`), with context available via format strings and environment variables

A “task” is an explicit command array stored in the manifest per project, such as:

- `tasks.install = ["poetry", "install"]`
- `tasks.test = ["poetry", "run", "pytest"]`
- `tasks.build = ["npm", "run", "build"]`

The monorepo CI uses a matrix generated by `tools/scaffold/ci_matrix.py` and runs tasks via `scaffold.py run <task>`.

Current known limitations to address (based on existing implementation patterns):

- Manifest writing is “lossy”: it may rewrite only a fixed subset of keys and discard additional metadata a human added.
- CI/task strictness is enforced at scaffold time for `lint/test/build` (kinds with CI enabled require corresponding generator `tasks.*`), but remaining validations and manifest preservation are still needed.
- CI toolchain setup is minimal (python and node only); other toolchains need conditional setup actions.

This plan fixes those issues and adds additional generators.

## Plan of Work

Part A: Add non-PDM and non-Python generators.

1) Poetry generator:

Create an internal copy skeleton or internal cookiecutter template for Poetry-based Python. Keep it minimal and offline-friendly, but realistic. It should produce:

- `pyproject.toml` with `[tool.poetry]` and a minimal dependency set
- `src/<package_name>/__init__.py`
- `tests/` with one passing test
- a `.gitignore` suitable for Python

Registry entry should define tasks:

- install: `["poetry", "install"]`
- test: `["poetry", "run", "pytest", "-q"]`
- lint: `["poetry", "run", "ruff", "check", "."]` (if ruff included) or omit lint and set `ci.lint=false` for kinds that use it.

2) uv generator (optional but recommended):

Provide either:
- a copy-based skeleton using `uv` conventions, or
- an external template that users can vendor

Tasks might be:

- install: `["uv", "sync"]`
- test: `["uv", "run", "pytest", "-q"]`

3) Node generator using `command` type:

Add a generator that runs `npm create` and produces the project at `{dest_dir}`. Because `npm create` prompts by default, choose a command that supports non-interactive scaffolding, or accept interactive usage and document it. For CI, you must at least define:

- install: `["npm", "install"]`
- build: `["npm", "run", "build"]` (if the scaffold includes build script)
- test: optional depending on template

Part B: Harden manifest correctness and validations.

1) Manifest schema version:

Add a top-level key in `tools/scaffold/monorepo.toml`, for example:

- `schema_version = 1`

Update the scaffold tool to read it (default to 1 if missing) and write it when rewriting.

2) Preserve unknown keys:

Update `_write_manifest` so it does not discard keys it does not recognize. A straightforward approach:

- When loading projects, keep each project entry dict as-is.
- When updating/adding keys, only modify the keys owned by scaffold (`id`, `kind`, `path`, `generator`, `toolchain`, `package_manager`, `ci`, `tasks`, provenance keys).
- When writing, serialize all keys, including nested tables, in a stable order.

If preserving arbitrary TOML structure becomes too complex with a hand-rolled writer, change the manifest format from TOML to JSON and keep TOML only for registry. If you choose this, record the decision and provide migration logic.

3) Enforce CI/task consistency at scaffold time:

In `cmd_add`, after `info.tasks` is known and before writing the manifest:

- If kind’s CI config includes `lint=true`, require that `tasks.lint` exists.
- If `test=true`, require `tasks.test`.
- If `build=true`, require `tasks.build`.
- If a required task is missing, fail loudly with an error that explains how to fix (update generator tasks or adjust kind CI policy).

This prevents “CI fails later” surprises.

Also validate task names. For example:

- Task names must match `^[a-zA-Z0-9_-]+$`

Reject task names containing dots, since writing `tasks.<name>` in TOML will treat dots as nesting and can create invalid/unexpected keys.

Part C: Improve CI toolchain setup.

Update the generated monorepo CI template to install tools for toolchains you want to support. At minimum:

- node: already present (`actions/setup-node`)
- terraform: add `hashicorp/setup-terraform` when `matrix.toolchain == 'terraform'`
- python: already present (`actions/setup-python`)

CI should run:

- doctor
- install (skip-missing)
- lint/test/build as dictated by matrix flags

Part D: Update tests.

Extend template repo tests to cover:

- Manifest preservation: manually add an extra key under a project entry (e.g. `owner = "team-x"`) and ensure subsequent `scaffold add ...` does not erase it.
- CI/task consistency: define a kind with `ci.test=true` and a generator missing `tasks.test`; verify `scaffold add` fails loudly.
- Generator registration: add a Poetry generator entry and ensure `scaffold add` records it correctly in manifest.

Keep tests offline and avoid requiring Poetry/npm installed. These tests should verify that tasks are recorded, not that external tools run.

## Concrete Steps

All changes in this plan affect the root template files under:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/...

and may also require updating the template repo tests under `tests/`.

1) Add internal template(s) for Poetry and optionally uv.

Create directories under:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/templates/internal/

For example:

- `python-poetry-cookiecutter/` (cookiecutter template)
or
- `python-poetry-copy/` (copy skeleton)

2) Add generator entries in registry:

Edit:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/registry.toml

Add entries like:

- `[generators.python_poetry]` (type cookiecutter or copy)
- `[generators.node_vite]` (type command)

Make sure tasks are defined so the manifest can drive CI.

3) Harden scaffold tool:

Edit:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/scaffold.py

Implement:

- schema_version write/read
- manifest preservation
- CI/task consistency validation in `cmd_add`
- task name validation (reject invalid names)

4) Improve generated monorepo CI toolchain setup:

Edit:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/.github/workflows/ci.yml

Add conditional terraform setup if you support terraform projects in CI:

  - uses: hashicorp/setup-terraform@v3
    if: ${{ matrix.id != '__no_projects__' && matrix.toolchain == 'terraform' }}

5) Update template repo tests:

Edit:

  tests/test_scaffold_monorepo_template.py

Add new tests as described. Ensure they remain offline and do not require Poetry/npm to be present.

6) Run template repo tests:

From template repo root:

  pdm install
  pdm run pytest

7) Manual smoke in rendered monorepo (optional):

Render a monorepo and run:

  python tools/scaffold/scaffold.py generators
  python tools/scaffold/scaffold.py kinds

Then add a project with the new generator using `--no-install` and confirm it is recorded in manifest.

## Validation and Acceptance

Acceptance is achieved when:

1) A generated monorepo contains new generator entries for at least:
- one non-PDM Python manager (Poetry or uv)
- one non-Python toolchain (Node command generator)

2) The scaffold tool prevents inconsistent configurations:

- If `ci.test=true` for a kind and the generator does not define `tasks.test`, `scaffold add` fails with a clear error.

3) The scaffold tool preserves unknown manifest metadata:

- Adding a manual metadata key to a project entry is not erased by subsequent scaffold operations.

4) Template repo tests pass offline.

5) Generated monorepo CI template includes toolchain setup for at least terraform and node (if those toolchains are supported in registry examples), plus doctor + install steps from Plan 2.

## Idempotence and Recovery

- Changes to templates are safe; regenerate a monorepo in a temp directory to test.
- Manifest changes: if you change schema, provide a migration step or backward-compatible reader behavior.
- If new validations block existing workflows, adjust defaults in `registry.toml` so the out-of-the-box kinds and generators are consistent.

## Artifacts and Notes

Keep internal templates small and explicit. The goal is to provide paved paths without assuming one package manager across the entire monorepo.

## Interfaces and Dependencies

This plan changes the behavior of the generated monorepo scaffold CLI (`tools/scaffold/scaffold.py`) by adding stricter validation and more stable manifest writing.

It also introduces new generator IDs in `tools/scaffold/registry.toml` for Poetry/uv/node, and potentially adds CI toolchain setup steps for new toolchains.

---

Plan update (2026-01-19): Marked milestones complete and recorded decisions after adding new generators, manifest schema/preservation, CI toolchain setup, and offline regression tests.
