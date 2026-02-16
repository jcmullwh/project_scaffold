# Publish Constraints, Failure Modes, and Troubleshooting Guidance

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan must be maintained in accordance with `.agents/PLANS.md`.

## Purpose / Big Picture

After this change, a user can find a single, consolidated troubleshooting page that answers:

- What platforms/runtimes/tools are required for the template repo vs the generated monorepo.
- The most common failure modes (missing tools, trust gate, networked generators, partial adds, CI mismatch).
- Concrete recovery steps that get them unstuck without needing to read source code or interpret raw tracebacks.

The goal is to reduce repeated “avoidable setup” issues and increase evaluator confidence by making constraints explicit and recovery paths obvious.

## Progress

- [x] (2026-02-11) Create this ExecPlan from ticket `BLG-033` (fingerprint `af73f93a2f3fcc28`).
- [x] (2026-02-11) Inventory existing constraint notes scattered across docs (root README, generated monorepo READMEs, and `USERS.md`).
- [x] (2026-02-11) Write a consolidated troubleshooting doc with prerequisites, common failures, and recovery steps.
- [x] (2026-02-11) Link to the troubleshooting doc from the root `README.md`.
- [x] (2026-02-11) Validate that referenced paths exist and that guidance matches current behavior.

## Surprises & Discoveries

- Observation: Many “failure mode” explanations already exist in the generated monorepo’s `tools/scaffold/README.md` (install tool preflight, `--no-install`, trust gate, vendoring), but the template repo’s root docs do not point to them and there is no single consolidated troubleshooting index.
  Evidence: `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md` contains scattered notes; `README.md` is minimal.

## Decision Log

- Decision: Create a dedicated `docs/TROUBLESHOOTING.md` page in the template repo and link to it from both the root README and the generated docs.
  Rationale: A single page is easier to find and maintain than sprinkling “gotchas” across multiple READMEs; links keep the entry points short.
  Date/Author: 2026-02-11 / agent

## Outcomes & Retrospective

- Outcome:
  - Added `docs/TROUBLESHOOTING.md` as a consolidated prerequisites + failure-modes + recovery guide.
  - Linked `docs/TROUBLESHOOTING.md` from the root `README.md` so evaluators and contributors can find it quickly.

## Context and Orientation

This repo has two distinct environments and sets of constraints:

- Template repo development (this repo):
  - Uses PDM (`pdm install`, `pdm run pytest`, etc.).
  - CI is defined in `.github/workflows/ci.yml`.
- Generated monorepo usage (output of Cookiecutter):
  - Uses plain `python tools/scaffold/scaffold.py ...` and does not assume PDM exists.
  - Has additional external toolchain dependencies depending on which generators you use (npm/go/cargo/terraform/poetry/uv/etc.).

Existing docs that already describe some constraints and recovery paths:

- Template repo:
  - `README.md`, `CONTRIBUTING.md`, `USERS.md`
- Generated monorepo (template preview copies):
  - `templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md`
  - `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md`
  - `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/monorepo_publish/README.md` (publishing snapshots)

## Plan of Work

1. Create `docs/TROUBLESHOOTING.md` in the template repo. Keep it prose-first and structured around questions a user asks when stuck. It must include:
   - Prerequisites, separated into:
     - “Template repo development prerequisites” (PDM, Python version).
     - “Generated monorepo prerequisites” (Python; optional tools by generator type; cookiecutter/git requirements).
   - Common failure modes and recovery steps, including at least:
     - “Command not found on PATH” for toolchains referenced by tasks.
     - Cookiecutter missing / Git missing for external template operations.
     - Trust gate failures for external templates and how to use `--trust` safely.
     - Install failures after generation and how to recover (`--no-install`, `scaffold.py run install`, `scaffold.py remove`).
     - Network-restricted environments and command-based generators (like `npm create ...`).
     - PowerShell path quoting pitfalls for brace placeholder directories.
   - A short “What is tested” section that states what the template repo CI covers (Linux in GitHub Actions; Python versions), and what is not yet covered.

2. Link to the troubleshooting doc:
   - Add a link near the top of the root `README.md` under the evaluator/contributor fork.
   - Add a short “Troubleshooting” link section in `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md` pointing back to the generated repo’s local docs (or to a section within that README), and optionally also link to the template repo doc for deeper explanation.

3. Validate that every referenced command name exists in the generated scaffolder CLI and that every referenced path exists in this repository.

## Concrete Steps

From repo root (`i:\\code\\project_scaffold`):

    # Sanity-check existing docs we will link from/to.
    Test-Path README.md
    Test-Path USERS.md
    Test-Path templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md
    Test-Path templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/monorepo_publish/README.md

    # (After implementation) smoke-check that the troubleshooting doc exists.
    Test-Path docs/TROUBLESHOOTING.md

## Validation and Acceptance

- There is a single consolidated troubleshooting doc at `docs/TROUBLESHOOTING.md`.
- The root `README.md` links to it in a place a first-time user will see.
- The troubleshooting doc contains:
  - explicit prerequisites (platform/runtime/tooling),
  - at least five common failure modes, each with a concrete recovery path, and
  - explicit support expectations (“what is tested in CI”).

## Idempotence and Recovery

Documentation-only change. Revisions are safe and should be made whenever behavior or constraints change.

## Artifacts and Notes

Source ticket: `BLG-033`
Fingerprint: `af73f93a2f3fcc28`

## Interfaces and Dependencies

No new dependencies. This plan only adds/updates documentation files.
