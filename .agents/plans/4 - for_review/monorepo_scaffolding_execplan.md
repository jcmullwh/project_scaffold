# Monorepo scaffolding system (bootstrap, add projects, vendoring, multi-toolchain)

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

After this change, a user can create a new monorepo with one command, and then add new subprojects over time with one command, without hardcoding a specific repo layout (“apps/ and packages/”) or a specific Python package manager (“python == pdm”). Projects can be generated from in-repo templates, external Cookiecutter templates pinned to a specific upstream revision, or non-Cookiecutter generators (for ecosystems like Node/Rust/Go/Terraform). Every generated project is recorded in a TOML manifest that becomes the single source of truth for CI and repo-wide task execution.

The generated monorepo’s baseline requirement should be only a working `python` on PATH. Additional external tools (like `cookiecutter` and `git`) must be required only when the user selects generator types that need them, and this must be enforced by loud, actionable errors rather than silent fallbacks.

The user-visible proof is a generated monorepo that contains a small `tools/scaffold/` Python CLI and a `tools/scaffold/monorepo.toml` manifest. Running `scaffold add ...` creates a new project directory and updates the manifest. Running `scaffold run test --all` executes each project’s configured test command from the manifest. Running CI shows jobs created from the manifest and only runs tasks enabled by each project’s policy.

## Progress

- [x] (2026-01-18 19:59Z) Draft ExecPlan using `.agents/PLANS.md`.
- [x] (2026-01-18 20:05Z) Clarify minimal external requirements.
- [x] (2026-01-18) Add template repo layout and dev tooling (PDM, pytest, cookiecutter, docs).
- [x] (2026-01-18) Implement root Cookiecutter monorepo template and baseline docs (`templates/monorepo-root/`).
- [x] (2026-01-18) Implement core `tools/scaffold/scaffold.py` CLI with registry + manifest support.
- [x] (2026-01-18) Implement `copy`, local `cookiecutter`, and `command` generators, plus `scaffold run`.
- [x] (2026-01-18) Add external Cookiecutter support (trust gate, pinning by default, repo-local cache, resolved commit capture).
- [x] (2026-01-18) Add vendoring (`scaffold vendor import/update`) with `UPSTREAM.toml` + license capture.
- [x] (2026-01-18) Add manifest-driven CI workflow (`.github/workflows/ci.yml`) + matrix generator (`tools/scaffold/ci_matrix.py`).
- [x] (2026-01-18) Add offline acceptance tests covering render + copy + internal cookiecutter + command generator + external trust gate + vendoring.

## Surprises & Discoveries

- Observation: Cookiecutter CLI (2.6.0) does not support `--extra-context`; extra context must be passed as positional `k=v` pairs.
  Evidence: `tools/scaffold/scaffold.py` calls `cookiecutter <template> --no-input --output-dir ... k=v ...` and does not rely on `--extra-context`.
- Observation: GitHub Actions `${{ ... }}` syntax and nested Cookiecutter templates conflict with the root template’s Jinja rendering unless explicitly excluded from rendering.
  Evidence: The root template uses `_copy_without_render` for `.github/**` and `tools/templates/**`, and `tools/scaffold/ci_matrix.py` avoids `${{ ... }}` in docstrings.
- Observation: Vendoring must ignore `.git` directories when copying templates; copying them can fail on Windows (permission errors) and is not useful in the vendored snapshot.
  Evidence: `vendor import`/`vendor update` ignore `.git` via `shutil.copytree(..., ignore=...)`.

## Decision Log

- Decision: Treat “kinds”, “generators”, and “tasks” as separate first-class concepts, with tasks explicitly defined in configuration rather than inferred from toolchain.
  Rationale: This is the simplest way to support many package managers (Poetry/uv/pip-tools/conda) and non-Python ecosystems without baking assumptions into code.
  Date/Author: 2026-01-18 / Codex

- Decision: Implement the monorepo-internal `scaffold` CLI as a small Python program with stdlib-only parsing and subprocess execution, using `tomllib` (Python 3.11+) and optionally `tomli` when available.
  Rationale: The generated monorepo should not depend on a particular Python packaging tool to run the scaffolder; external tools like `cookiecutter` and `git` can be checked by `scaffold doctor`.
  Date/Author: 2026-01-18 / Codex

- Decision: When `scaffold vendor import` adds a new generator, append a new `[generators.<id>]` section to `tools/scaffold/registry.toml` instead of rewriting the file.
  Rationale: `registry.toml` is primarily human-authored; preserving comments and layout reduces accidental churn.
  Date/Author: 2026-01-18 / Codex

- Decision: Minimize always-required external dependencies in generated monorepos; treat `cookiecutter`, `git`, and toolchain/package-manager commands as conditional requirements that are checked at the point of use (or for existing projects in the manifest) with loud, actionable failures.
  Rationale: The scaffold system should be usable for copy/command generators without forcing users to install tools they do not need, while still making requirements explicit when a chosen generator or task needs them.
  Date/Author: 2026-01-18 / Codex

- Decision: Use root-template `_copy_without_render` for `.github/**` and `tools/templates/**` to avoid Jinja rendering collisions and preserve nested templates verbatim.
  Rationale: GitHub Actions and nested Cookiecutter templates contain `{{ ... }}`-like syntax that must survive as literal text in the generated monorepo.
  Date/Author: 2026-01-18 / Codex

- Decision: Pass Cookiecutter variables as positional `k=v` pairs to the `cookiecutter` CLI.
  Rationale: Cookiecutter CLI does not accept `--extra-context`; positional `k=v` is widely compatible and keeps the scaffolder stdlib-only.
  Date/Author: 2026-01-18 / Codex

- Decision: Ignore `.git` directories when copying external templates into `tools/templates/vendor/`.
  Rationale: Vendored templates are snapshots, not git clones; copying `.git` is unnecessary and can fail on Windows.
  Date/Author: 2026-01-18 / Codex

## Outcomes & Retrospective

- Outcome: This repo now contains a working root Cookiecutter template (`templates/monorepo-root/`) that generates a monorepo with `tools/scaffold/` scaffolding, internal templates (Python + Terraform), and a manifest-driven CI skeleton.
- Outcome: Generated monorepos require only `python` to run the scaffolder; `cookiecutter`, `git`, and toolchain/package-manager binaries are required only when using generators/tasks that need them, with loud errors.
- Outcome: External Cookiecutter templates are supported with a trust gate (`trusted=false` requires `--trust`) and pinning-by-default, plus vendoring (`vendor import`/`vendor update`) with `UPSTREAM.toml` metadata and basic license capture.
- Outcome: Offline tests validate end-to-end rendering, adding projects (copy/cookiecutter/command generators), external template trust behavior, and vendoring workflows.
- Outcome: The generated CI workflow runs an `install` task (when defined) before `lint/test/build` using `scaffold run install --skip-missing`.
- Outcome: `scaffold add` fails early if `kinds.<kind>.ci` enables `lint/test/build` but the chosen generator does not define the corresponding `tasks.*` (override via `--allow-missing-ci-tasks`).

## Context and Orientation

This repository now contains a working Cookiecutter root template under `templates/monorepo-root/`, a stdlib-only scaffold CLI that is embedded into generated monorepos, and offline tests under `tests/`. Planning artifacts live under `.agents/`.

Two different “roots” exist in this repository:

1. The template repository root (this repo), which contains the Cookiecutter template under `templates/monorepo-root/`.
2. The generated monorepo root, which is the rendered output of the template. Paths like `tools/scaffold/scaffold.py` refer to the generated monorepo; in this repo they will live under `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/scaffold.py`.

Key terms used in this plan:

- Monorepo: a single git repository that contains multiple subprojects in different directories.
- Subproject (or “project”): a directory inside the monorepo that is independently buildable/testable (a service, library, data notebook folder, infrastructure module, etc.).
- Kind: a category of subproject (for example `app`, `lib`, `data`, `infra`) that defines policy defaults such as output directory and CI task policy.
- Generator: a method of creating a new project directory. A generator can be Cookiecutter-based, command-based (runs an external scaffold command), or copy-based (copies a skeleton directory).
- Task: an explicit command to run in a project directory (for example `lint`, `test`, `build`, `install`). Tasks are configured per generator and recorded per project in the manifest so the scaffolder is toolchain-agnostic.
- Registry: `tools/scaffold/registry.toml` in the generated monorepo. This is human-authored configuration that defines kinds, generators, and vendoring settings.
- Manifest: `tools/scaffold/monorepo.toml` in the generated monorepo. This is machine-updated state that lists all projects, their paths, generator provenance, and the tasks CI should run.
- Cookiecutter: a template system (Python-based) that renders a directory tree from variables. Cookiecutter templates can execute code via hooks; this is why “trust” matters for external templates.
- External template: a Cookiecutter template sourced from outside the repo, typically a git URL. External templates are treated as untrusted by default.
- Ref: a git reference (tag/branch/commit). Pinning an external template to a ref makes generation reproducible. Where possible, the scaffolder should resolve the pinned ref to an immutable commit hash and record it in the manifest.
- Vendoring: copying an external template into the monorepo (under `tools/templates/vendor/`) so it can be modified locally, while tracking upstream URL/ref/license for compliance and future updates.

Python environment policy for the generated monorepo is intentionally minimal. The generated `tools/scaffold` CLI should run with plain `python` and must not require a repo-wide virtual environment. Python subprojects should generally use isolated environments (a virtual environment or conda env), but that choice is per project and is expressed via explicit `tasks.install` commands (Poetry/uv/pip-tools/conda/PDM/etc.). The scaffolder must not assume any particular tool, and it must report missing tools only when a selected generator or task requires them.

## Plan of Work

Implement the system in milestones so each milestone produces a working, observable capability in a freshly generated monorepo. Each milestone ends with offline tests and a manual “walkthrough” that proves behavior from a clean working directory.

Milestones are ordered to reduce risk:

- First, create the root template and a minimal scaffolder that supports internal templates and a copy-based generator.
- Then add external Cookiecutter support with strict trust and pinning rules.
- Then add vendoring (import/update) to allow bringing external templates into the repo for customization.
- Then add multi-toolchain examples by relying entirely on explicit task configuration rather than “magic” assumptions.
- Finally, add manifest-driven CI so the system proves itself end-to-end in automation.

### Milestone 1 — Core scaffolder + local internal templates

In the Cookiecutter monorepo template (`templates/monorepo-root/`), create a generated monorepo layout that includes:

- The scaffolder CLI under `tools/scaffold/` and its configuration files (`registry.toml`, `monorepo.toml`).
- A small set of internal templates under `tools/templates/internal/` (at minimum one Cookiecutter template and one copy skeleton).
- A baseline directory structure for kinds (for example `apps/`, `packages/`, `data/`, `experiments/`, `infra/`) that can be changed via `registry.toml`.
- Root documentation explaining how to run `scaffold` and how kinds/generators/tasks are configured.

Implement `tools/scaffold/scaffold.py` in the generated monorepo with these commands:

- `scaffold init`: ensure expected directories/files exist; do not overwrite existing config; print what was created.
- `scaffold kinds`: list kinds and their default output directories.
- `scaffold generators`: list generators, their type, and whether they are local or external.
- `scaffold add <kind> <name> [--generator GEN] [--no-install] [--vars k=v ...]`: create a project and update the manifest.
- `scaffold run <task> [--all | --kind K | --project ID]`: run a configured task command in each selected project.
- `scaffold doctor`: validate that config + manifest are consistent and required external tools exist on PATH.

Implement generator providers inside the scaffolder:

- Copy provider: copies a skeleton directory into the destination path. The source must be a local path inside the monorepo (typically `tools/templates/internal/...`).
- Cookiecutter provider (local only for this milestone): renders from a local path template using the `cookiecutter` CLI. This provider must be optional; if `cookiecutter` is not installed, `scaffold add` must fail only when a Cookiecutter generator is selected, and must print a clear error telling the user what to install. Variables come from `--vars` and generator `context_defaults`.

Implement manifest behavior:

- `tools/scaffold/monorepo.toml` is the single source of truth for “what projects exist”. Every successful `scaffold add` must append a new `[[projects]]` entry with `id`, `kind`, `path`, `generator`, `toolchain`, `package_manager`, `ci` booleans, and a per-project `tasks.*` command list.
- `scaffold run` must use the manifest’s `tasks.<task>` for each project; it must not infer commands from toolchain/package manager.

Acceptance tests for this milestone must be offline. Use temporary directories to:

- Render a monorepo from the root Cookiecutter template.
- Add a project using the copy provider and verify directory contents + manifest update.
- Add a project using the internal Cookiecutter template and verify directory contents + manifest update.
- Run `scaffold run` across all projects and verify it runs the configured commands in the correct working directories.

### Milestone 2 — External Cookiecutter support (trust + pinning)

Extend the Cookiecutter provider and registry schema to support external templates:

- In `registry.toml`, an external Cookiecutter generator has `type = "cookiecutter"`, a `source` that is a git URL (or a `gh:` shorthand), an optional `directory` for “template within repo”, a required `ref` when pinning is enforced, and `trusted = false` by default.
- In the CLI, `scaffold add` refuses to use an external generator with `trusted = false` unless the user passes `--trust` for that invocation.
- When pinning is enabled (default), `scaffold add` must fail if an external generator has no `ref`. Provide an explicit flag to override pinning (for development only) that prints a loud warning and records that the project was generated unpinned.

Implement reproducibility and traceability:

- For external templates, clone/fetch into a repo-local cache directory (for example `.scaffold/cache/`) so the scaffolder can resolve the checked-out commit hash.
- Record `generator_source`, `generator_ref`, and `generator_resolved_commit` in the manifest project entry.

Offline tests for this milestone must not use network. Create a local git repository fixture that contains a minimal Cookiecutter template and reference it via a `file://` URL so the scaffolder takes the “external” path. Verify:

- `scaffold add` fails without `--trust`.
- `scaffold add` succeeds with `--trust` and records the resolved commit.
- `scaffold add` fails when pinning is required and `ref` is missing.

### Milestone 3 — Vendoring/importing external templates

Implement template vendoring so teams can import external templates into the monorepo and customize them:

- Add `scaffold vendor import <generator_id> [--as NEW_ID] [--ref ...]`.
- `vendor import` clones/fetches the upstream template source, checks out the selected ref, and copies the template directory into `tools/templates/vendor/<vendor_id>/`.
- `vendor import` writes `tools/templates/vendor/<vendor_id>/UPSTREAM.toml` containing `upstream_url`, `upstream_ref`, `imported_at` (ISO 8601), and any license information that can be detected.
- If a license file is present in upstream (for example `LICENSE`, `LICENSE.md`, `COPYING`), copy it into the vendored directory and record its filename(s) in `UPSTREAM.toml`. If an SPDX identifier can be detected from the license text, record it; otherwise record `license_spdx = "unknown"`.
- `vendor import` appends a new generator entry to `tools/scaffold/registry.toml` that points to the vendored local path and sets `trusted = true` (it is now in-repo and reviewable).

Implement `scaffold vendor update <vendor_id>` as a minimal, safe workflow:

- Fetch upstream at a specified ref to a temporary directory.
- Produce a diff between the current vendored directory and the upstream snapshot (use `git diff --no-index` or a stdlib diff if needed).
- Write the upstream snapshot to a separate directory (for example `tools/templates/vendor/<vendor_id>.__upstream_tmp__/`) and print clear manual merge instructions.
- Do not overwrite the existing vendored directory automatically. The default should be “show diff and stage an upstream copy” so updates are deliberate and reviewable.

Offline tests should validate `vendor import` end-to-end using the same local git fixture from Milestone 2. Validate that after vendoring, a new project can be generated from the vendored generator without `--trust`.

### Milestone 4 — Multi-toolchain support (non-PDM Python + non-Python)

Prove toolchain-agnostic behavior by adding example generators and ensuring tasks run through configuration:

- Add at least one non-PDM Python generator (Poetry, uv, pip-tools, or conda) where `tasks.*` use that tool’s commands and the scaffolder does not special-case Python.
- Add at least one non-Python generator. Prefer a command-based generator and/or a copy-based generator (Terraform module skeleton is a good copy-based example).

Update `scaffold doctor` to report missing tools per project by checking the first element of each task command (for example `poetry`, `uv`, `npm`, `cargo`, `terraform`) and printing actionable instructions. This check must be a loud warning or hard error; it must not silently skip tasks.

Offline tests should cover the command provider using a local “fake generator command” (for example a small script checked into the test fixture) so no network calls are needed. The test should confirm that the command runs in the correct working directory and that created files appear in the destination.

### Milestone 5 — CI integration (manifest-driven)

Add a baseline CI workflow to the root monorepo template that runs tasks based on the manifest:

- The workflow reads `tools/scaffold/monorepo.toml`, builds a job matrix of projects, and runs `lint/test/build` based on each project entry’s `ci` booleans.
- Toolchain setup is based on `toolchain` (for example `python` uses `actions/setup-python`, `node` uses `actions/setup-node`). Keep the initial mapping small and explicit, and document how to extend it for new toolchains.
- CI runs tasks using the project working directory and the exact `tasks.*` command configured for that project.

Implement a small script (for example `tools/scaffold/ci_matrix.py` in the generated monorepo) that prints the JSON matrix for GitHub Actions. This script must be stdlib-only and use `tomllib` (or `tomli` fallback).

Acceptance for this milestone is a GitHub Actions run in a generated monorepo that demonstrates:

- Jobs are created from the manifest.
- Only tasks enabled by `ci` flags run.
- Failures are attributable to a specific project/task and do not silently degrade.

## Concrete Steps

All commands in this section assume the working directory is the root of this repository (the template repo) unless otherwise stated. Use `pdm` to manage the Python environment for development work in this repository.

1. Create development environment and run tests for this template repo:

    pdm install
    pdm run pytest

2. Render a monorepo from the root template into a temporary directory (example; adjust variables to match the template’s `cookiecutter.json`):

    pdm run cookiecutter templates/monorepo-root --no-input repo_slug=demo-monorepo --output-dir .tmp

   Expected output includes a created directory:

    demo-monorepo

3. Exercise the scaffolder in the generated monorepo:

    cd .tmp/demo-monorepo
    python tools/scaffold/scaffold.py doctor
    python tools/scaffold/scaffold.py kinds
    python tools/scaffold/scaffold.py generators

4. Add a project using an internal generator and verify the manifest updates:

    python tools/scaffold/scaffold.py add app billing-api

   Expected observable results:

    - The directory apps/billing-api exists (or the kind’s configured output dir).
    - tools/scaffold/monorepo.toml contains a new [[projects]] entry for billing-api.

5. Run tasks across all projects:

    python tools/scaffold/scaffold.py run lint --all

   Expected observable result: each project’s configured lint command is executed with the project path as the working directory.

## Validation and Acceptance

The system is accepted when all of the following behaviors are demonstrated in a freshly generated monorepo:

- Root bootstrap: running Cookiecutter once creates a monorepo root that contains `tools/scaffold/scaffold.py`, `tools/scaffold/registry.toml`, and `tools/scaffold/monorepo.toml`. A user can run `scaffold` commands that do not involve Cookiecutter (for example copy-based generators) with only `python` installed. When `cookiecutter`/`git` are required (due to the chosen generator type), the scaffolder fails loudly with clear, actionable errors.
- Project creation (internal): `scaffold add <kind> <name>` creates a project directory in the correct output dir for that kind and appends a correct entry to the manifest.
- Project creation (external trust): attempting to generate from an external generator marked `trusted=false` fails without `--trust` and succeeds with `--trust`, recording the pinned ref and resolved commit in the manifest.
- Vendoring: `scaffold vendor import <generator>` creates `tools/templates/vendor/<vendor_id>/` with `UPSTREAM.toml` and a copied license file when present, and adds a new local generator that can be used without `--trust`.
- Toolchain agnosticism: at least one non-PDM Python generator and one non-Python generator can be used, and `scaffold run <task>` runs only what is explicitly configured, with no inferred commands.
- CI integration: a GitHub Actions workflow in the generated monorepo creates jobs from the manifest and runs per-project tasks according to `ci` flags.

All automated tests added to this repository must run offline. Any tests that need an “external template” must use a local git repository fixture and `file://` URLs so they do not require network access.

## Idempotence and Recovery

The scaffolder commands must be safe to rerun and must fail loudly rather than silently falling back:

- `scaffold init` is idempotent: rerunning it should not overwrite `registry.toml` or `monorepo.toml`; it should print what already exists and exit successfully.
- `scaffold add` must refuse to write into an existing destination directory unless an explicit “overwrite” feature is added later. If a generation step fails after creating partial files, the error output must tell the user what directory was created so they can delete it and retry.
- `scaffold vendor import` must refuse to import into an existing vendor directory or reuse an existing generator id. Recovery is “delete the vendor dir and remove the appended registry entry, then rerun”.
- `scaffold vendor update` must not overwrite the current vendored template automatically. Recovery is “delete the temporary upstream snapshot directory and rerun”.

## Artifacts and Notes

Registry schema example (generated monorepo: `tools/scaffold/registry.toml`):

    [scaffold]
    templates_cache_dir = ".scaffold/cache"
    vendor_dir = "tools/templates/vendor"

    [kinds.app]
    output_dir = "apps"
    ci = { lint = true, test = true, build = true }

    [generators.python_poetry]
    type = "cookiecutter"
    source = "tools/templates/internal/python-poetry"
    toolchain = "python"
    package_manager = "poetry"
    tasks.install = ["poetry", "install"]
    tasks.test = ["poetry", "run", "pytest"]

UPSTREAM metadata example (generated monorepo: `tools/templates/vendor/<vendor_id>/UPSTREAM.toml`):

    upstream_url = "https://github.com/example/template.git"
    upstream_ref = "v1.2.3"
    imported_at = "2026-01-18T19:59:50Z"
    license_spdx = "MIT"
    license_files = ["LICENSE"]

Manifest example (generated monorepo: `tools/scaffold/monorepo.toml`):

    [[projects]]
    id = "billing-api"
    kind = "app"
    path = "apps/billing-api"
    generator = "python_poetry"
    toolchain = "python"
    package_manager = "poetry"
    ci = { lint = true, test = true, build = true }
    tasks.install = ["poetry", "install"]
    tasks.test = ["poetry", "run", "pytest"]

## Interfaces and Dependencies

External tools the generated monorepo may require (validated by `scaffold doctor`):

- `python` (always required to run the scaffolder itself).
- `cookiecutter` (required only when the selected generator is Cookiecutter-based).
- `git` (required only for external Cookiecutter sources and vendoring workflows that fetch upstream content).
- Toolchain-specific commands referenced in tasks (for example `poetry`, `uv`, `npm`, `cargo`, `terraform`), required only when running those tasks or using command-based generators that call them.

Within the generated monorepo, implement a provider interface in `tools/scaffold/scaffold.py` as plain Python classes or `Protocol`s:

- `GeneratorProvider.supports(generator_config) -> bool`
- `GeneratorProvider.generate(name, dest_path, vars, generator_config) -> GeneratedProjectInfo`
- `GeneratorProvider.describe(generator_config) -> str`

Define `GeneratedProjectInfo` as a simple dict or dataclass with:

- `path: str` (relative to repo root)
- `toolchain: str`
- `package_manager: str`
- `tasks: dict[str, list[str]]` (explicit task commands)
- `warnings: list[str]` (for example “external cookiecutter hooks may execute code”)
- Optional provenance fields for external sources (`source`, `ref`, `resolved_commit`).

Configuration parsing requirements:

- Parse `tools/scaffold/registry.toml` and `tools/scaffold/monorepo.toml` using `tomllib` (Python 3.11+) and fall back to `tomli` only when running on older Python and `tomli` is installed.
- Reject unknown generator types and missing required keys with clear, actionable errors.

CLI contract requirements (generated monorepo):

- The CLI entrypoint is `tools/scaffold/scaffold.py` with a `main(argv) -> int` function and `if __name__ == "__main__": raise SystemExit(main(sys.argv[1:]))`.
- All commands must print user-actionable errors and exit non-zero on failure. No silent fallbacks.

---

Plan revision note (2026-01-18 / Codex): Clarified that the generated monorepo should have only `python` as an always-required dependency, with `cookiecutter`, `git`, and toolchain commands treated as conditional requirements that are checked and reported loudly at the point of use. This change was made to match the goal of avoiding external requirements that are not strictly necessary.

Plan revision note (2026-01-18 / Codex): Updated the living-document sections (`Progress`, `Surprises & Discoveries`, `Decision Log`, `Outcomes & Retrospective`, and `Context and Orientation`) to reflect the completed implementation in this repo, including Cookiecutter CLI context-passing constraints, `_copy_without_render` requirements, and vendoring `.git` exclusion.

Plan revision note (2026-01-18 / Codex): Updated the generated CI workflow to run `install` (when present) via `--skip-missing`, and added early validation that CI-enabled tasks (`lint/test/build`) must exist on the chosen generator unless explicitly overridden.
