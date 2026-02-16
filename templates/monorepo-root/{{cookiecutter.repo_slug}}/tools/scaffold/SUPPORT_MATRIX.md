# Support Matrix (Generators and Toolchains)

This document is a compatibility and prerequisites map for the built-in generators defined in
`tools/scaffold/registry.toml`.

It answers:

- What tools must be on PATH to run `scaffold.py add` for a given generator.
- What tools must be on PATH to run the generator's recorded `tasks.*` later.
- What is actually tested by the template repo that produced this monorepo.

## Baseline assumptions

- `python` must be on PATH to run `tools/scaffold/scaffold.py`. Python 3.11+ is recommended (so the stdlib `tomllib`
  module is available for TOML parsing). Older Pythons need `tomli` installed.
- Toolchains are not managed by the scaffolder. If a task references `pdm`, `poetry`, `uv`, `npm`, `go`, `cargo`, or
  `terraform`, you must install those tools separately.

## What is tested (and what is not)

The template repo that generated this monorepo (the Cookiecutter source) runs offline tests that:

- render the monorepo template, and
- exercise the generated scaffolder CLI against the rendered output.

Those tests validate that generators can be *planned* and (for copy/cookiecutter sources) that the scaffolder can
generate project directories. They typically use `--no-install`, so they do not require the external toolchains to be
present.

The tests do not run every generator's toolchain tasks end-to-end (for example they do not run `npm install`, `go test`,
or `cargo test` in CI).

## Generator matrix

Legend:

- "Add prereqs" = tools required to run `python tools/scaffold/scaffold.py add ...` for that generator.
- "Task prereqs" = tools required to run `python tools/scaffold/scaffold.py run <task> ...` for tasks recorded by that
  generator.

| Generator id | Type | Add prereqs | Task prereqs | Network | Tested by template repo |
| --- | --- | --- | --- | --- | --- |
| `python_stdlib_copy` | `copy` | `python` | `python` | No | Yes (offline; typically via `--no-install`) |
| `python_stdlib_cookiecutter` | `cookiecutter` | `python`, `cookiecutter` | `python` | No | Yes (offline) |
| `python_pdm_lib` | `cookiecutter` | `python`, `cookiecutter` | `python`, `pdm` | No | Yes (offline generation; tasks not run in CI) |
| `python_pdm_app` | `cookiecutter` | `python`, `cookiecutter` | `python`, `pdm` | No | Yes (offline generation; tasks not run in CI) |
| `python_poetry_app` | `copy` | `python` | `python`, `poetry` | No | Yes (offline generation; tasks not run in CI) |
| `python_uv_app` | `copy` | `python` | `python`, `uv` | No | Yes (offline generation; tasks not run in CI) |
| `node_vite` | `command` | `python`, `npm` | `python`, `npm` | Yes (first run can fetch packages) | Partially (registry shape only; command not executed in CI) |
| `node_typescript_lib` | `copy` | `python` | `python`, `npm` | No (tasks may download deps) | Yes (offline generation; tasks not run in CI) |
| `go_stdlib_lib` | `copy` | `python` | `python`, `go` | No | Yes (offline generation; tasks not run in CI) |
| `rust_cargo_lib` | `copy` | `python` | `python`, `cargo` | No | Yes (offline generation; tasks not run in CI) |
| `terraform_module` | `copy` | `python` | `python`, `terraform` | No | Yes (offline generation; tasks not run in CI) |

## Update policy

When you change `tools/scaffold/registry.toml` (add/remove generators, change task commands, or change toolchain
assumptions), update this document in the same change.
