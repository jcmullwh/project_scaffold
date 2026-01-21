# Add Go/Rust/TypeScript generators and implement `scaffold add --dry-run`

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This repo includes an ExecPlan policy document at `.agents/PLANS.md` (from the repository root). This ExecPlan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

Downstream users of the generated monorepo want two concrete improvements:

First, they want more built-in project templates (specifically Go, Rust, and TypeScript) so they can scaffold common non-Python projects without hunting for external templates or wiring tasks manually. After this change, someone using a generated monorepo can run `python tools/scaffold/scaffold.py add lib mylib --generator <new-id>` and get a working skeleton with sensible `tasks.*` recorded into the monorepo manifest.

Second, they want a safe “preview” mode for `scaffold add`. After this change, `python tools/scaffold/scaffold.py add ... --dry-run` will print exactly what would happen (paths, generator, CI requirements, tasks that would be recorded, and key tool requirements), while making zero writes: no directories created, no generator executed, and no manifest edits.

Both changes should be demonstrably working via this repository’s existing integration tests, which render the Cookiecutter monorepo template into a temp directory and execute the generated monorepo’s `tools/scaffold/scaffold.py`.

## Progress

- [x] (2026-01-21) Authored this ExecPlan with repository-specific file paths, milestone breakdown, and acceptance criteria.
- [x] (2026-01-21) Moved this ExecPlan to `.agents/plans/3 - in_progress/` to begin implementation.
- [x] (2026-01-21) Add internal templates for Go, Rust, and TypeScript under the monorepo template’s `tools/templates/internal/`.
- [x] (2026-01-21) Register the new generators in the monorepo template’s `tools/scaffold/registry.toml`.
- [x] (2026-01-21) Update monorepo docs and CI workflow to recognize `toolchain = go|rust`.
- [x] (2026-01-21) Add offline tests in `tests/test_scaffold_monorepo_template.py` that prove the new generators scaffold correctly without requiring `go`, `cargo`, or `npm` on PATH.
- [x] (2026-01-21) Implement `scaffold add --dry-run` in the generated monorepo’s `tools/scaffold/scaffold.py`, ensuring it performs validations and prints a plan with zero writes.
- [x] (2026-01-21) Add tests that prove `--dry-run` prints an actionable plan, returns success on valid input, and does not create directories or modify `tools/scaffold/monorepo.toml`.
- [x] (2026-01-21) Run formatting, linting, type checking, and pytest for this repo and fix any regressions.

## Surprises & Discoveries

- Observation: (none yet; update during implementation)
  Evidence: (add short transcripts or diffs here when surprises are found)

## Decision Log

- Decision: Implement Go/Rust/TypeScript as “copy” generators with minimal, dependency-light skeletons and tasks that are useful but not overly opinionated.
  Rationale: Copy generators are deterministic, offline-friendly, and fit the existing internal-template model. Avoiding test-time execution of `go/cargo/npm` aligns with the repo’s “offline tests” constraint implied by downstream notes.
  Date/Author: 2026-01-21 / GPT-5.2 Pro

- Decision: `--dry-run` must fail only when the real `add` would fail with the same flags (unknown kind/generator, destination exists, trust/unpinned policy violation, missing required generator binary, missing install tool when install would run, missing required CI tasks unless `--allow-missing-ci-tasks`).
  Rationale: Users want an accurate preview, not a new stricter behavior. Additional “missing tool” findings for non-install tasks should be reported as warnings, not hard failures, to preserve existing semantics.
  Date/Author: 2026-01-21 / GPT-5.2 Pro

- Decision: Use `actions/setup-go@v5` (Go 1.22) and `dtolnay/rust-toolchain@stable` for conditional toolchain setup in the generated monorepo CI workflow.
  Rationale: Keep the workflow change minimal and consistent with existing conditional Node/Terraform setup, while ensuring Go/Rust projects can run their recorded tasks in CI.
  Date/Author: 2026-01-21 / GPT-5.2 Pro

- Decision: For cookiecutter generators with external sources, dry-run enforces trust and pinning policy and checks required tools, but does not fetch/clone templates or resolve commits.
  Rationale: Fetching/cloning would write to `.scaffold/cache` and may require network access; dry-run must guarantee zero writes.
  Date/Author: 2026-01-21 / GPT-5.2 Pro

## Outcomes & Retrospective

Milestone 1 shipped Go/Rust/TypeScript internal templates and copy-style generators, updated the generated monorepo CI
workflow to install Go/Rust when needed, and updated the generated monorepo docs. Integration tests assert these
generators scaffold and record tasks without requiring `go`, `cargo`, or `npm` on PATH.

Milestone 2 shipped `scaffold add --dry-run`, which performs the same validations (including CI task validation and the
install-tool preflight when applicable) while making zero writes. Integration tests assert dry-run prints a plan, leaves
the destination directory absent, leaves `tools/scaffold/monorepo.toml` unchanged, and fails cleanly when the
destination already exists.

As of 2026-01-21, `pdm run ruff check .`, `pdm run mypy .`, `pdm run deptry .`, and `pdm run pytest` all pass.

## Context and Orientation

This repository is not a normal application repo; it is a template repository.

Key concepts in plain language:

A “generated monorepo” is what Cookiecutter produces when you render `templates/monorepo-root/`. The directory `templates/monorepo-root/{{cookiecutter.repo_slug}}/` is a template folder whose name contains a Cookiecutter placeholder; it becomes a real folder like `demo-monorepo/` when rendered.

Inside the generated monorepo there is a small Python CLI at `tools/scaffold/scaffold.py`. This CLI is “stdlib-only”, meaning it uses only Python’s standard library and shells out to external tools only when a generator or task needs them.

The scaffold tool reads two TOML files in the generated monorepo:

- Registry: `tools/scaffold/registry.toml`. This defines “kinds” (high-level project categories like `app`, `lib`) and “generators” (how to create a project directory and what tasks it should have).
- Manifest: `tools/scaffold/monorepo.toml`. This is the source of truth for what projects exist in the monorepo. When you run `scaffold.py add`, the tool creates the directory and then writes a project entry into this manifest, including explicit `tasks.*` command arrays (for example `tasks.test = ["python","-m","pytest","-q"]`).

Generator types (as implemented in `tools/scaffold/scaffold.py`) are:

- `copy`: Copy a local directory tree and apply token substitutions in file names and file contents. Existing internal templates use tokens like `__NAME__` and `__NAME_SNAKE__`, which are replaced by the scaffolder’s context.
- `cookiecutter`: Run Cookiecutter against a local or git-accessible template, possibly external. External cookiecutter sources have a trust gate and a pinning policy.
- `command`: Run a command like `npm create ...` that creates the destination directory.

This repo’s tests are in `tests/test_scaffold_monorepo_template.py`. They render the monorepo template into a temp directory and then call the generated monorepo’s `tools/scaffold/scaffold.py` using `subprocess.run`. This means any changes to the scaffold CLI must be made in the template path:

- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/scaffold.py`

not in the root of this repository.

## Plan of Work

This work is split into two independently verifiable milestones.

### Milestone 1: Add built-in Go, Rust, and TypeScript templates and generators

At the end of this milestone, the generated monorepo will ship with three new internal templates and corresponding registry entries:

- A Go library skeleton generator (`go_stdlib_lib`)
- A Rust library skeleton generator (`rust_cargo_lib`)
- A TypeScript (Node + TypeScript compiler) library skeleton generator (`node_typescript_lib`)

Each generator must:

- Be defined in `tools/scaffold/registry.toml` inside the monorepo template.
- Scaffold into the appropriate kind output directory (for `lib`, that is `packages/<name>`).
- Define `tasks.lint` and `tasks.test` so it satisfies `kinds.lib.ci = { lint = true, test = true, build = false }`.
- Avoid requiring `go/cargo/npm` to run during this repository’s tests. The tests must always scaffold using `--no-install` and must not run `scaffold run test` for these new languages.

Also, because the generated monorepo CI workflow is driven by `toolchain`, and existing CI already sets up Python, Node, and Terraform conditionally, we will extend the template’s `.github/workflows/ci.yml` to also set up Go and Rust when `matrix.toolchain` is `go` or `rust`. This keeps the generated monorepo CI coherent when users add Go or Rust projects.

How to verify milestone 1:

- Run this repo’s tests from the repository root: `pdm run pytest`. The new tests must pass.
- Optionally, inspect a rendered monorepo and run `python tools/scaffold/scaffold.py generators` to see the new generator IDs listed.

### Milestone 2: Implement `scaffold add --dry-run` with zero writes

At the end of this milestone, `python tools/scaffold/scaffold.py add <kind> <name> --dry-run` in a generated monorepo will:

- Print a human-readable plan including: destination path, selected generator (id/type/source/origin), the `ci` flags implied by the kind, and the fully formatted `tasks.*` commands that would be written into the manifest.
- Perform the same validations the real add would perform (name validity, kind/generator existence, destination collision, trust and pinning policy for external cookiecutter generators, and required CI task presence), so the preview is accurate.
- Perform the same install-tool preflight that the real add performs when install would run (that is: only if `--no-install` is not set and the generator defines `tasks.install`).
- Make zero writes: it must not create any directories, must not run any generator, and must not modify `tools/scaffold/monorepo.toml`.

How to verify milestone 2:

- Add new tests that render a monorepo, capture the manifest text, run `scaffold.py add ... --dry-run`, and then assert that:
  - The destination directory does not exist afterward.
  - The manifest file contents are byte-for-byte unchanged.
  - The stdout contains expected plan lines (stable strings like “DRY RUN” and the repo-relative destination path).
- Run `pdm run pytest` from this repo root and ensure all tests pass.

## Concrete Steps

All commands below assume you are in the repository root of this template repo (the directory containing `pyproject.toml`).

If you do not have PDM installed, install it with:

  python -m pip install --upgrade pip
  python -m pip install pdm

Then install dev dependencies:

  pdm install

### Milestone 1 concrete steps

1) Add the internal Go template directory.

Create a new directory:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/templates/internal/go-stdlib-lib/

Add these files with the following minimal contents (use the tokens `__NAME__` and `__NAME_SNAKE__` exactly; the scaffold tool’s copy generator will replace them):

- `README.md`

    # __NAME__

    This project was created by `scaffold` using the `go_stdlib_lib` generator.

- `go.mod`

    module example.com/__NAME_SNAKE__

    go 1.22

- `adder.go`

    package __NAME_SNAKE__

    func Add(a int, b int) int {
        return a + b
    }

- `adder_test.go`

    package __NAME_SNAKE__

    import "testing"

    func TestAdd(t *testing.T) {
        if Add(2, 3) != 5 {
            t.Fatalf("expected 5, got %d", Add(2, 3))
        }
    }

2) Add the internal Rust template directory.

Create:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/templates/internal/rust-cargo-lib/

Add:

- `README.md`

    # __NAME__

    This project was created by `scaffold` using the `rust_cargo_lib` generator.

- `Cargo.toml`

    [package]
    name = "__NAME_SNAKE__"
    version = "0.1.0"
    edition = "2021"

    [lib]
    path = "src/lib.rs"

- `src/lib.rs` (create the `src/` directory)

    pub fn add(a: i32, b: i32) -> i32 {
        a + b
    }

    #[cfg(test)]
    mod tests {
        use super::*;

        #[test]
        fn test_add() {
            assert_eq!(add(2, 3), 5);
        }
    }

3) Add the internal TypeScript template directory.

Create:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/templates/internal/node-typescript-lib/

Add:

- `README.md`

    # __NAME__

    This project was created by `scaffold` using the `node_typescript_lib` generator.

- `package.json`

    {
      "name": "__NAME_SNAKE__",
      "version": "0.1.0",
      "private": true,
      "scripts": {
        "typecheck": "tsc -p tsconfig.json --noEmit",
        "build": "tsc -p tsconfig.json",
        "test": "npm run build && node --test dist/tests/test_basic.js"
      },
      "devDependencies": {
        "@types/node": "^20.0.0",
        "typescript": "^5.0.0"
      }
    }

- `tsconfig.json`

    {
      "compilerOptions": {
        "target": "ES2020",
        "module": "commonjs",
        "moduleResolution": "node",
        "rootDir": ".",
        "outDir": "dist",
        "strict": true,
        "esModuleInterop": true,
        "forceConsistentCasingInFileNames": true,
        "skipLibCheck": true
      },
      "include": ["src", "tests"]
    }

- `src/index.ts`

    export function add(a: number, b: number): number {
      return a + b;
    }

- `tests/test_basic.ts`

    import test from "node:test";
    import { equal } from "node:assert/strict";
    import { add } from "../src/index";

    test("add", () => {
      equal(add(2, 3), 5);
    });

4) Register the new generators in the monorepo template registry.

Edit:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/registry.toml

Append new generator blocks (placement does not affect functionality, but keep them near other generators for readability):

- Go:

    [generators.go_stdlib_lib]
    type = "copy"
    source = "tools/templates/internal/go-stdlib-lib"
    toolchain = "go"
    package_manager = "none"
    substitutions = { "__NAME__" = "{name}", "__NAME_SNAKE__" = "{name_snake}" }
    tasks.lint = ["go", "vet", "./..."]
    tasks.test = ["go", "test", "./..."]

- Rust:

    [generators.rust_cargo_lib]
    type = "copy"
    source = "tools/templates/internal/rust-cargo-lib"
    toolchain = "rust"
    package_manager = "cargo"
    substitutions = { "__NAME__" = "{name}", "__NAME_SNAKE__" = "{name_snake}" }
    tasks.lint = ["cargo", "check"]
    tasks.test = ["cargo", "test"]

- TypeScript:

    [generators.node_typescript_lib]
    type = "copy"
    source = "tools/templates/internal/node-typescript-lib"
    toolchain = "node"
    package_manager = "npm"
    substitutions = { "__NAME__" = "{name}", "__NAME_SNAKE__" = "{name_snake}" }
    tasks.install = ["npm", "install"]
    tasks.lint = ["npm", "run", "typecheck"]
    tasks.test = ["npm", "test"]
    tasks.build = ["npm", "run", "build"]

5) Update the generated monorepo CI workflow to support `toolchain = go|rust`.

Edit:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/.github/workflows/ci.yml

Add conditional setup steps similar to the existing Node/Terraform steps. The intent is:

- If `matrix.toolchain == 'go'`, install a Go toolchain (pin to 1.22 to match the template’s `go.mod` directive).
- If `matrix.toolchain == 'rust'`, install Rust (stable).

A minimal insertion near the existing toolchain setup steps:

  - uses: actions/setup-go@v5
    if: ${{ matrix.id != '__no_projects__' && matrix.toolchain == 'go' }}
    with:
      go-version: "1.22"

  - name: Setup Rust
    if: ${{ matrix.id != '__no_projects__' && matrix.toolchain == 'rust' }}
    run: |
      rustc --version

The exact Rust setup mechanism is a policy choice. If you prefer an explicit installer action, use one and ensure it is conditional on `matrix.toolchain == 'rust'`. Keep the workflow change minimal and consistent with how Node/Terraform are handled.

The observable goal is that Go/Rust projects do not fail CI immediately due to a missing compiler when their tasks run.

6) Update generated monorepo documentation so users can discover the new generators.

Edit:

- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md`
- `templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md`

In both places, expand the “Included generators” / “Other generators” section to mention the new generator IDs and show one example invocation, emphasizing `--no-install` for TypeScript when users want to generate without running npm immediately.

Example text to add (adapt to the surrounding style):

- Go (stdlib): `go_stdlib_lib`
- Rust (Cargo): `rust_cargo_lib`
- TypeScript (Node): `node_typescript_lib`

Example:

  python tools/scaffold/scaffold.py add lib my-go-lib --generator go_stdlib_lib --no-install

7) Add offline tests proving the new generators scaffold and record tasks.

Edit:

  tests/test_scaffold_monorepo_template.py

Add a new test function (or three separate ones) that:

- Renders a monorepo: `repo_root = _render_monorepo(tmp_path, repo_slug="demo-new-gens")`
- Runs add with `--no-install` for each generator
- Asserts created directories and key files exist
- Parses `tools/scaffold/monorepo.toml` and asserts generator IDs and task commands were recorded

Important constraint: do not run `scaffold.py run test` for these new generators, because CI for this template repo must not depend on `go`, `cargo`, or `npm` being installed.

A concrete shape for a single combined test:

- `go_stdlib_lib`: `python scaffold.py add lib golib --generator go_stdlib_lib --no-install`
  - assert `packages/golib/go.mod` exists
  - assert manifest tasks include `["go","test","./..."]`
- `rust_cargo_lib`: similarly assert `Cargo.toml` and `["cargo","test"]`
- `node_typescript_lib`: assert `package.json` and manifest `tasks.install == ["npm","install"]` and `tasks.test == ["npm","test"]`

### Milestone 2 concrete steps

1) Add a `--dry-run` flag to the `add` subcommand in the generated monorepo scaffold tool.

Edit:

  templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/scaffold.py

In `build_parser()`, on the `p_add` parser, add:

  p_add.add_argument(
      "--dry-run",
      action="store_true",
      help="Print what would be created/recorded without writing files or running generators.",
  )

2) Refactor `cmd_add` so it can compute a plan without writing.

The simplest safe structure is:

- Compute all inputs (kind, generator, dest path, user vars, context).
- Validate destination does not exist.
- Compute the tasks/toolchain/package_manager that would be recorded, without running generators.
- Validate CI task presence via `_validate_ci_tasks(...)`.
- Ensure project id uniqueness in the existing manifest (read-only).
- If `--dry-run`, print the plan and return 0.
- Otherwise, proceed with existing behavior (create dest parent, run generator, write manifest, run install).

To make copy generators work in dry-run (because `_generate_copy` currently copies files), introduce a helper that computes substitutions and formatted tasks without performing the copy:

In `templates/.../tools/scaffold/scaffold.py`, define:

  def _compute_copy_substitutions(*, generator: dict[str, Any], context: dict[str, str]) -> dict[str, str]:
      ...

This helper should mirror the substitutions handling in `_generate_copy`:

- Read `generators.<id>.substitutions` as a dict of string tokens to template strings.
- For each token, format the template string with `_format_with_context(...)` using `context`.
- Return the computed substitutions dict.

Then define:

  def _plan_generate_copy(...same inputs...) -> GeneratedProjectInfo:
      ...

It should:

- Validate `source` exists and is a local directory (same checks as `_generate_copy`).
- Call `_compute_copy_substitutions(...)`.
- Normalize and format tasks with `_normalize_tasks(...)` then `_format_tasks(..., substitutions=substitutions)`.
- Return `GeneratedProjectInfo` with `path`, `toolchain`, `package_manager`, and formatted `tasks`.
- Perform no filesystem writes.

For cookiecutter and command generators, create analogous “plan” helpers that perform only validations and task formatting:

  def _plan_generate_cookiecutter(...) -> GeneratedProjectInfo:
      ...

It should:

- Require `cookiecutter` on PATH (matching `_generate_cookiecutter`).
- Classify source and enforce trust and pinning policy (same gating logic), but do not clone or execute cookiecutter.
- If the source is local, ensure the template path exists (and `directory` if specified exists).
- Build tasks via `_normalize_tasks` and `_format_tasks` (substitutions None).
- Return `GeneratedProjectInfo` without running anything.

  def _plan_generate_command(...) -> tuple[GeneratedProjectInfo, list[str]]:
      ...

It should:

- Validate and format the `command` list the same way `_generate_command` formats it (apply `_format_with_context` to each arg).
- If formatted `command[0]` is not a path-like command, `_require_on_path(command[0], why="command generator selected")` so dry-run fails when the real generator would fail immediately.
- Build tasks with `_normalize_tasks` and `_format_tasks`.
- Return `GeneratedProjectInfo` and also return the formatted command list for printing (so users can see what would be executed).

3) Print a stable dry-run plan to stdout.

Add a helper:

  def _print_dry_run_add_plan(
      *,
      repo_root: Path,
      kind: str,
      name: str,
      dest_rel: Path,
      generator_id: str,
      generator: dict[str, Any],
      gen_origin: str,
      info: GeneratedProjectInfo,
      ci: dict[str, Any],
      would_run_install: bool,
      formatted_command: list[str] | None,
  ) -> None:
      ...

The output should be readable and easy to test. Use a small number of stable header lines and then indented blocks for details.

A recommended output shape:

- First line: `DRY RUN: scaffold add <kind> <name>`
- Destination: `Destination: <repo-relative path>`
- Generator: `Generator: <id> (type=<type>, origin=<local|external|...>)`
- If command generator: `Command: <argv joined by spaces>`
- CI flags: `CI: lint=<true/false> test=<true/false> build=<true/false>`
- “Would record in tools/scaffold/monorepo.toml:” and then print key/value pairs for:
  - id, kind, path, generator, toolchain, package_manager
  - ci = {...}
  - tasks.<name> = [...]
- “Would run install after generation:” yes/no, and if yes print the install command.

Avoid printing absolute filesystem paths (use repo-relative `dest_rel` formatted with forward slashes) because tests and cross-platform behavior are easier to maintain.

4) Ensure dry-run performs zero writes.

In `cmd_add`, ensure that when `args.dry_run` is true you do not:

- Create `dest_dir.parent` (avoid `mkdir`).
- Call `_generate_copy/_generate_cookiecutter/_generate_command`.
- Load and then write the manifest (loading is fine; writing is not).

Also ensure no other paths are created in dry-run (for example no cache dirs, no temp dirs).

5) Add tests covering dry-run behavior.

Edit:

  tests/test_scaffold_monorepo_template.py

Add a test that:

- Renders a monorepo.
- Reads `tools/scaffold/monorepo.toml` contents into a string `before`.
- Runs `scaffold add app dryrunproj --dry-run` (explicitly choose a generator if needed, but the default for `app` is `python_stdlib_copy` so it should work).
- Asserts returncode is 0.
- Asserts `apps/dryrunproj` does not exist.
- Reads the manifest again and asserts it matches `before` exactly.
- Asserts stdout contains:
  - `DRY RUN: scaffold add app dryrunproj`
  - `Destination: apps/dryrunproj`
  - `Would record in tools/scaffold/monorepo.toml:`

Add a second test that ensures dry-run still catches a real failure case with no writes. A good candidate is “destination already exists”:

- Create a real project `apps/existing` with `scaffold add app existing --no-install`.
- Capture manifest contents.
- Run `scaffold add app existing --dry-run` and assert non-zero return code (expected 2) and an error mentioning `Destination already exists`.
- Assert manifest unchanged by that dry-run attempt.

Optionally (but recommended), add a test that dry-run enforces the install-tool preflight when install would run:

- Append a temporary generator with `tasks.install = ["definitely-not-on-path", "install"]` (similar to the existing test `test_scaffold_add_preflights_missing_install_tool`).
- Run `scaffold add app bad --generator bad_install_tool --dry-run` (without `--no-install`) and assert it fails with the same error and does not create the directory.

6) Update docs in the generated monorepo to describe dry-run.

Edit:

- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md`
- Optionally also `templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md` in the “Golden path” section.

Add a short subsection “Dry run” that explains:

- `--dry-run` prints the plan and performs validations.
- It makes no writes and does not execute generators.
- It is useful for checking task/CI expectations and required tools before committing to generation.

## Validation and Acceptance

Acceptance for milestone 1 (templates + generators):

- Running `pdm run pytest` from the repo root passes.
- The new tests confirm that, in a rendered monorepo:
  - `python tools/scaffold/scaffold.py add lib golib --generator go_stdlib_lib --no-install` succeeds and creates `packages/golib/go.mod`.
  - `python tools/scaffold/scaffold.py add lib rustlib --generator rust_cargo_lib --no-install` succeeds and creates `packages/rustlib/Cargo.toml`.
  - `python tools/scaffold/scaffold.py add lib tslib --generator node_typescript_lib --no-install` succeeds and creates `packages/tslib/package.json`.
  - The manifest `tools/scaffold/monorepo.toml` records the expected generator IDs and task command arrays for each.
- The generated monorepo CI workflow template includes conditional setup for Go and Rust toolchains based on `matrix.toolchain`, consistent with existing conditional Node/Terraform setup.

Acceptance for milestone 2 (dry-run):

- Running `pdm run pytest` passes, including new dry-run tests.
- In a rendered monorepo, running:

  python tools/scaffold/scaffold.py add app dryrunproj --dry-run

  exits 0, prints a plan that includes the destination and the tasks that would be recorded, and does not create `apps/dryrunproj` nor modify `tools/scaffold/monorepo.toml`.
- Dry-run fails (with return code 2) in the same cases the real add would fail (for example, destination already exists), and still leaves the filesystem and manifest unchanged.

## Idempotence and Recovery

All changes are additive and safe to re-run:

- Adding internal template directories is idempotent as long as the directories and files are created at the specified paths.
- Updating `registry.toml` and docs is idempotent; re-running tests validates the end state.
- The dry-run feature must be safe to run repeatedly because it performs no writes.

If tests fail during implementation, the fastest recovery loop is:

- Run `pdm run ruff format .` to fix formatting issues.
- Run `pdm run ruff check .` and address lint errors.
- Run `pdm run mypy .` and fix typing issues in the modified scaffold tool and tests.
- Run `pdm run pytest` to confirm behavior end-to-end.

## Artifacts and Notes

Expected example of dry-run output (exact wording can vary, but keep the stable header lines used by tests):

  DRY RUN: scaffold add app dryrunproj
  Destination: apps/dryrunproj
  Generator: python_stdlib_copy (type=copy, origin=local)
  CI: lint=true test=true build=false
  Would record in tools/scaffold/monorepo.toml:
    id = "dryrunproj"
    kind = "app"
    path = "apps/dryrunproj"
    generator = "python_stdlib_copy"
    toolchain = "python"
    package_manager = "none"
    ci = { lint = true, test = true, build = false }
    tasks.lint = ["python", "-m", "compileall", "src"]
    tasks.test = ["python", "-m", "unittest", "discover", "-s", "tests"]
  Would run install after generation: no (no install task configured)

## Interfaces and Dependencies

New generator IDs (in the generated monorepo template’s `tools/scaffold/registry.toml`):

- `go_stdlib_lib`:
  - type: `copy`
  - toolchain: `go`
  - package_manager: `none`
  - tasks required by kind `lib` CI: `tasks.lint`, `tasks.test`

- `rust_cargo_lib`:
  - type: `copy`
  - toolchain: `rust`
  - package_manager: `cargo`
  - tasks required by kind `lib` CI: `tasks.lint`, `tasks.test`

- `node_typescript_lib`:
  - type: `copy`
  - toolchain: `node`
  - package_manager: `npm`
  - tasks required by kind `lib` CI: `tasks.lint`, `tasks.test`
  - includes `tasks.install` to run `npm install` (but tests and many users can use `--no-install`)

New CLI surface (in the generated monorepo’s `tools/scaffold/scaffold.py`):

- `scaffold add --dry-run`:
  - Must be implemented as an option on the existing `add` subcommand.
  - Must perform validations and print a plan.
  - Must do zero writes and execute no generator.

New helper functions to introduce inside `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/scaffold.py` (names are prescriptive for clarity and to keep the implementation readable):

- `_compute_copy_substitutions(*, generator: dict[str, Any], context: dict[str, str]) -> dict[str, str]`
- `_plan_generate_copy(...) -> GeneratedProjectInfo`
- `_plan_generate_cookiecutter(...) -> GeneratedProjectInfo`
- `_plan_generate_command(...) -> tuple[GeneratedProjectInfo, list[str]]`
- `_print_dry_run_add_plan(...) -> None`

These helpers must remain stdlib-only and must typecheck under this repo’s strict mypy configuration.

---

Plan revision note: Initial version authored on 2026-01-21 to cover two prioritized milestones (new Go/Rust/TypeScript templates and `scaffold add --dry-run`) requested by downstream users, with offline-friendly tests and novice-oriented repository context.
Plan revision note: (2026-01-21) Moved to `.agents/plans/3 - in_progress/` and removed the outer ```md fence to comply with `.agents/PLANS.md` guidance for single-ExecPlan `.md` files.
Plan revision note: (2026-01-21) Implemented both milestones, updated Progress/Decision Log/Outcomes to reflect shipped behavior and test coverage, and ran the full repo checks.
