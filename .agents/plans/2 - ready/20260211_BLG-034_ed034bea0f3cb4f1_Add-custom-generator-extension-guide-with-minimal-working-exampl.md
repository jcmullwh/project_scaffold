# Add a Custom Generator Extension Guide With a Minimal Working Example

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

After this change, a user can add a new custom generator to a generated monorepo by following documentation only. The docs must walk through:

- where generator configuration lives (registry vs manifest),
- what fields are required for a minimal generator, and
- how to validate the generator by listing it and scaffolding a project with it.

The guide must include a minimal working example that does not require network access and does not depend on non-Python toolchains.

## Progress

- [x] (2026-02-11) Create this ExecPlan from ticket `BLG-034` (fingerprint `ed034bea0f3cb4f1`).
- [ ] Review current generator documentation and identify what is missing for “do it yourself” extension.
- [ ] Add a step-by-step “Add your own generator” guide in the generated monorepo docs.
- [ ] Include a minimal working example generator definition and validation commands.
- [ ] Validate the guide by rendering a monorepo and executing the documented steps end-to-end.

## Surprises & Discoveries

- Observation: The generated scaffolder README already documents generator types (copy/cookiecutter/command) and includes TOML snippets, but does not provide a linear, “do these steps in this order” guide that ends with a working custom generator.
  Evidence: `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md` contains examples, but no extension walkthrough.

## Decision Log

- Decision: Put the extension guide in `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md` and link to it from the generated monorepo `README.md`.
  Rationale: Generator extension is performed in the generated monorepo by editing `tools/scaffold/registry.toml`, so the guide should live beside that file’s main documentation.
  Date/Author: 2026-02-11 / agent

- Decision: Use a minimal example that reuses an existing internal template source (no new files) and requires only Python.
  Rationale: This keeps the example deterministic, offline, and focused on the registry/manifest mechanics rather than template authoring.
  Date/Author: 2026-02-11 / agent

## Outcomes & Retrospective

- Outcome: (fill in after implementation)

## Context and Orientation

In a generated monorepo:

- “Registry” means `tools/scaffold/registry.toml`. It defines:
  - kinds (where projects go, default generators, CI expectations), and
  - generators (how to create a project, what tasks to record).
- “Manifest” means `tools/scaffold/monorepo.toml`. It records:
  - what projects exist, and
  - the exact task commands to run for each project.

The scaffolder CLI reads the registry and writes the manifest:

    python tools/scaffold/scaffold.py add <kind> <project_id> --generator <generator_id>

The template repo stores the generated monorepo docs and registry as template copies under:

- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md`
- `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/registry.toml`

## Plan of Work

1. Update `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md` to add a new section, for example:
   - `Extending the registry: adding your own generator`

2. In that section, write a linear guide that includes:
   - where to edit (`tools/scaffold/registry.toml`),
   - the minimal set of generator fields (`type`, `source` for copy/cookiecutter, or `command` for command generators, plus descriptive `toolchain`/`package_manager`),
   - a warning about kind CI requirements (if a kind has `ci.lint/test/build = true`, the generator must define corresponding `tasks.*` unless the user opts out), and
   - validation commands:
     - `python tools/scaffold/scaffold.py generators` (to list the generator),
     - `python tools/scaffold/scaffold.py add ... --generator <id> --no-install` (to scaffold without toolchain installs),
     - `python tools/scaffold/scaffold.py projects` (to confirm manifest entry).

3. Include a minimal working example that reuses an existing internal template source already present in the generated monorepo (for example, point a new generator id at `tools/templates/internal/python-stdlib-copy`). The example should be copy-pasteable TOML.

4. Add a short pointer in `templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md` linking to the new extension section.

## Concrete Steps

From repo root (`i:\\code\\project_scaffold`), validate the guide by actually doing it in a rendered monorepo:

    New-Item -ItemType Directory -Force .tmp | Out-Null
    pdm run cookiecutter templates/monorepo-root --no-input -o .tmp

    # Edit the generated repo's tools/scaffold/registry.toml to add the example generator,
    # then run:
    python .tmp/my-monorepo/tools/scaffold/scaffold.py generators
    python .tmp/my-monorepo/tools/scaffold/scaffold.py add app demo-app --generator <your_new_generator_id> --no-install
    python .tmp/my-monorepo/tools/scaffold/scaffold.py projects

## Validation and Acceptance

- The generated scaffolder README contains a step-by-step custom generator guide.
- Following the guide in a freshly generated monorepo results in:
  - the new generator appearing in `scaffold.py generators`, and
  - a project successfully scaffolded with that generator (directory exists and an entry exists in `tools/scaffold/monorepo.toml`).
- The guide is explicit about registry vs manifest responsibilities and about CI task requirements.

## Idempotence and Recovery

The validation steps write into `.tmp/`. Delete `.tmp/` and re-run. If a user makes a mistake editing `registry.toml`, the recovery is to revert the file (git) or fix the TOML and re-run `scaffold.py doctor` for validation.

## Artifacts and Notes

Source ticket: `BLG-034`  
Fingerprint: `ed034bea0f3cb4f1`

## Interfaces and Dependencies

No new runtime dependencies. Documentation-only change, validated by running the existing generated scaffolder.
