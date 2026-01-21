# Users

> Purpose: Capture intent (why someone reaches for this repo, what they are trying to decide/do, and what counts as
> evidence), and provide a foundation for discovery-oriented user simulation.
>
> This is not a spec of exact steps. It should stay valid even as the UI/API changes.

## Status

- Owner(s): Jason (GitHub: `jcmullwh`)
- Last reviewed: 2026-01-20
- Scope: template repo that generates a monorepo scaffold (Cookiecutter template + generated-repo `tools/scaffold` CLI)
- Where this file is used: agent context, prioritization, docs roadmap, discovery-oriented user simulation

---

## Why this project exists

### Motivating problems (the "before" cost)

Describe the real-world costs that cause someone to look for a project like this.

- Bootstrapping a new monorepo repeatedly is expensive (structure, CI, conventions, and "what do we run?" decisions).
- Adding subprojects over time tends to devolve into copy/paste drift without an explicit registry/manifest as source of
  truth.
- CI often hardcodes a single toolchain, which breaks down in polyglot monorepos or mixed Python toolchains.
- Teams need explicit, reproducible per-project task commands (install/lint/test/build) rather than tribal knowledge.
- External templates can run code (Cookiecutter hooks); safe defaults require a trust model and a vendoring story.
- Cross-platform sharp edges are easy to miss (Windows `.cmd` shims, third-party generators that mishandle absolute paths,
  doc encoding issues).

### What this project is (in one sentence)

- A Cookiecutter monorepo scaffold plus a small Python CLI that adds projects and runs per-project tasks recorded in a
  manifest (toolchain-agnostic by design).

### Non-goals

Explicitly state what this project is *not* trying to do (prevents accidental scope creep).

- Not a full build system (e.g., Bazel/Pants) and not a monorepo-wide dependency manager.
- Not a virtual-environment manager; projects choose their own approach (PDM/Poetry/uv/venv/conda/etc.).
- Not offline-first for every generator: some command-based generators (e.g. `npm create ...@latest`) can require network.
- Not a promise of exhaustive OS/runtime coverage by default; expand support when there is a concrete need and evidence.

---

## Who this is for

> Personas here are "roles + context." Avoid assuming exact tactics.

For each persona, fill in only what you actually know; leave unknowns when you don't.

### Persona: Monorepo bootstrapper/maintainer (tech lead / platform engineer)

- Situation / trigger:
  - Starting a new monorepo (or rebooting one) and wants a credible baseline quickly.
- Job to be done:
  - Generate a repo scaffold, establish conventions, and make it easy to add new projects with repeatable CI behavior.
- Motivating pain (why they would adopt this category of tool):
  - Losing days to yak-shaving and then re-losing days later when local vs CI workflows diverge or drift.
- Constraints (shaping context, not complaints):
  - Mixed OS developers (Windows/macOS/Linux); limited appetite for adding new "platform" dependencies.
  - Security review concerns around templating systems that can execute code.
  - Needs an audit trail for what was generated and why.
- What counts as evidence (to decide it's a fit):
  - Generated monorepo can add multiple kinds of projects; task commands are explicit in a manifest; CI consumes the
    manifest; docs show a "golden path" to reproduce CI locally.
  - External template trust model works: untrusted generators are gated and can be vendored into the repo.
  - `tools/scaffold/scaffold.py run <task>` can target `--project`/`--kind`/`--all`, and `--skip-missing` makes mixed
    toolchains practical (some projects won't define every task).
- Deal-breakers:
  - Hidden toolchain assumptions, silent fallbacks, or a scaffold that cannot be adapted without rewriting everything.
  - Cross-platform failures that are common in practice (e.g., Windows command shims, path handling).
- Unknowns (things we suspect but haven't validated):
  - How often Windows/macOS CI is required vs just "developer workstation support".
  - Which ecosystems will be needed long-term beyond Python/Node/Terraform.

### Persona: Subproject owner (application/library developer)

- Situation / trigger:
  - Needs a new service/library/site inside an existing monorepo and wants it created consistently.
- Job to be done:
  - Add a new project, run install/lint/test/build, and get passing CI with minimal ceremony.
- Motivating pain (why they would adopt this category of tool):
  - Copy/paste scaffolds break subtly; CI failures are hard to interpret; tasks differ per project with no documentation.
- Constraints (shaping context, not complaints):
  - Wants to use the toolchain that fits the project (not the monorepo's choice).
  - May be in a restricted environment (offline, corporate proxy, missing toolchains).
- What counts as evidence (to decide it's a fit):
  - `tools/scaffold/scaffold.py add ...` creates a working project in the expected location.
  - `tools/scaffold/scaffold.py run ...` reproduces what CI runs for that project (no hidden behavior).
  - Selectors (`--project`/`--kind`/`--all`) plus `--skip-missing` are enough to run useful cross-repo checks even when
    projects intentionally define different task sets.
- Deal-breakers:
  - "Works on Linux only" in practice when their workstation is Windows/macOS.
  - Tasks that look present but fail due to missing toolchain with unclear messaging.
- Unknowns (things we suspect but haven't validated):
  - Whether they need project-to-project dependency wiring patterns beyond "create and run tasks".

### Persona: Automation/agent runner (CI operator / Codex user)

- Situation / trigger:
  - Running `scaffold.py doctor` / `scaffold.py run ...` as part of CI or via an agentic tool, and needs failures to be
    deterministic and debuggable.
- Job to be done:
  - Validate tool availability and run the same per-project tasks CI will enforce, without interactive prompts.
- Motivating pain (why they would adopt this category of tool):
  - Per-project tasks are often undocumented; automation needs a single, explicit entry point.
- Constraints (shaping context, not complaints):
  - Often non-interactive execution (no ability to answer prompts from tools like `npm create ...`).
  - Approvals/sandboxing can be tool-specific (e.g., `codex exec` approvals are fixed; sandboxing is controlled via
    `--sandbox`).
- What counts as evidence (to decide it's a fit):
  - Missing toolchain failures surface as clear `ScaffoldError` messages (not Python tracebacks).
  - The manifest is sufficient to generate CI matrices and run tasks without additional glue scripts.
- Deal-breakers:
  - Interactive generators that block automation, or failures that are hard to attribute to missing prerequisites.
- Unknowns (things we suspect but haven't validated):
  - Whether non-interactive "scaffold add" is a real requirement vs a developer-only workflow.

### Persona: Generator/template contributor (maintainer / power user)

- Situation / trigger:
  - Wants to add a new generator or improve an internal template while keeping the system testable and reliable.
- Job to be done:
  - Extend the registry/templates, keep the manifest model consistent, and ensure changes are covered by offline tests.
- Motivating pain (why they would adopt this category of tool):
  - Template repos rot quickly without strong invariants and tests; changes are hard to audit later.
- Constraints (shaping context, not complaints):
  - Prefers loud failures; no silent defaults; tests must run offline.
  - Needs to keep generated output toolchain-agnostic (tasks recorded explicitly).
- What counts as evidence (to decide it's a fit):
  - Adding a generator is straightforward; trust/vendoring behavior is clear; the manifest remains a useful audit trail.
- Deal-breakers:
  - Changes are not reproducible or not observable (no clear errors, no manifest records, CI doesn't reflect reality).
- Unknowns (things we suspect but haven't validated):
  - Which future generator "kinds" matter most and what baseline tasks should be required for CI.

---

## What they care about

> Prefer outcomes, tradeoffs, and decision criteria over UX opinions.

### Outcomes

- A monorepo scaffold that can evolve: projects can be added/changed without turning CI into a brittle pile of scripts.
- Explicit per-project task commands (install/lint/test/build), recorded in a manifest and runnable both locally and in CI.
- Safe defaults for external templates (trust gate + vendoring).
- Cross-platform behavior for common workflows (at least developer workstation support on Windows/macOS/Linux).

### Acceptable tradeoffs

- Accepts a registry/manifest configuration model in exchange for reproducibility and clarity.
- Accepts that toolchains must be installed separately (the scaffold tool does not manage environments).
- Accepts that some generators are inherently networked unless pinned/vendored.

### Decision criteria (how they judge fit)

- Can generate the monorepo and understand where to customize it (templates, registry, manifest).
- Can add at least one project and run its tasks end-to-end with clear failures when prerequisites are missing.
- Command generators behave sensibly cross-platform:
  - repo-relative destination paths work (avoids third-party "absolute path treated as relative" bugs)
  - Windows command shims (e.g., `npm.cmd`) are runnable
- The PDM app baseline works out of the box (imports work; `.venv/` is not accidentally committed).
- Docs call out "gotchas" that look like failures but are intentional (internal templates copied without render).

---

## How they interact with the project

> Interaction modes, not scripts.

- Entry points:
  - Repo-level docs: `README.md`, `CONTRIBUTING.md`, `.agents/agents.md`
  - Generated-monorepo docs: `templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md`,
    `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/README.md`
  - Source of truth/config: `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/registry.toml`,
    `templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/scaffold/monorepo.toml`
- Adoption modes:
  - Big-bang: generate a new monorepo via Cookiecutter.
  - Incremental: add projects over time via `tools/scaffold/scaffold.py add ...`.
- Typical working style:
  - Start from the "golden path" commands, then customize generators/registry as needs emerge.

---

## Critical missions

> "Missions" are intent-based journeys: what they're trying to decide/do, with room for variation.

### Mission: Evaluate and generate a new monorepo scaffold

- Intent:
  - Decide whether this scaffold is a good starting point and generate a repo that can be extended.
- Starting state:
  - Fresh clone; has `python` available; can install this repo's dev deps via `pdm`.
- Variations worth exploring:
  - With and without `cookiecutter` installed on PATH (cookiecutter generators should fail fast with clear errors).
  - Windows vs Linux path/encoding differences (docs should remain readable; paths should be handled predictably).
- What counts as success (evidence):
  - Cookiecutter template renders.
  - Generated monorepo can run `python tools/scaffold/scaffold.py doctor`.
  - Adding a project records tasks in the manifest; generated CI workflow is manifest-driven.
  - Docs explain that internal templates under `tools/templates/internal/` are intentionally copied without render.
- Likely forks:
  - Choosing default generators/kinds; deciding whether to include/allow external Cookiecutter sources.
- Failure meaning:
  - Could indicate missing docs, missing prerequisites, or a true limitation in the scaffold model.
- Unknowns this mission is meant to surface:
  - Which parts are too opinionated vs appropriately generic.

### Mission: Add a Vite web project on Windows without surprises

- Intent:
  - Add a web project and avoid "created in the wrong place" or "command not found" failures.
- Starting state:
  - Generated monorepo; Node + npm installed.
- Variations worth exploring:
  - `npm` is a `.cmd` shim on PATH (common on Windows).
  - Network-restricted environments where `npm create ...@latest` cannot fetch dependencies.
  - Non-interactive execution (agents/CI) where `npm create ...` can prompt and fail.
- What counts as success (evidence):
  - `scaffold.py add web my-site` creates `apps/my-site` (no nested/duplicated absolute-path artifacts).
  - The command runner can execute `npm` on Windows (shim handling).
- Likely forks:
  - Pinning versions for reproducibility vs accepting networked scaffolding.
- Failure meaning:
  - Could indicate a cross-platform path handling issue, missing toolchain, or a network/reproducibility mismatch.
- Unknowns this mission is meant to surface:
  - Whether "web kind" should be treated as inherently networked and version-pinned by policy.

### Mission: Add Python projects (PDM/Poetry/uv) and run quality gates

- Intent:
  - Add a Python project with the chosen toolchain and have install/lint/test tasks work as recorded.
- Starting state:
  - Generated monorepo; chosen toolchain installed on PATH (e.g., `pdm`/`poetry`/`uv`).
- Variations worth exploring:
  - PDM user config enabling venv mode (creates `.venv/` by default).
  - Lockfile/tooling group expectations (dev tools present vs missing).
  - Per-project lockfiles (e.g., one `pdm.lock` per project) vs expecting a single monorepo-level lock.
  - Missing toolchain on PATH (e.g., `uv` missing causes install/task failures unless using `--no-install`).
- What counts as success (evidence):
  - `scaffold.py add app myapp --generator python_pdm_app` creates an importable package (no "distribution = false" import
    surprises).
  - `.venv/` is ignored at the repo level so it is not accidentally committed.
  - `scaffold.py run install/lint/test` behaves the same locally and in CI.
- Likely forks:
  - Standardizing on one toolchain vs allowing each project to choose; deciding what tasks must exist for CI-enabled kinds.
- Failure meaning:
  - Could indicate missing toolchain, misconfigured tasks, or unclear docs about project manager behavior.
- Unknowns this mission is meant to surface:
  - Which baseline tasks (format/typecheck/depcheck/etc.) should be standardized across generators.

### Mission: Recover from partial adds (manifest vs on-disk state)

- Intent:
  - Recover cleanly when `scaffold.py add` fails partway through (missing tool, install failure, interactive generator).
- Starting state:
  - Generated monorepo; a project directory may exist on disk; the project may or may not be recorded in
    `tools/scaffold/monorepo.toml`.
- Variations worth exploring:
  - Project recorded, but install failed (tool missing, network, bad config).
  - Project created on disk, but not recorded in the manifest (command generator side effects after an error).
- What counts as success (evidence):
  - If recorded: user can fix prerequisites and re-run `scaffold.py run install --project <id>`, or unregister via
    `scaffold.py remove <id>`.
  - If not recorded: the recovery path is documented (manual manifest edit or a future "adopt/register existing" flow).
- Likely forks:
  - Delete the directory vs keep it and repair.
  - Use `--no-install` to separate generation from installation when prerequisites are uncertain.
- Failure meaning:
  - Could indicate missing preflight checks, overly interactive generators, or gaps in "how to recover" documentation.
- Unknowns this mission is meant to surface:
  - Whether the tool should grow a first-class "adopt/register existing directory" command.

### Mission: Use an external Cookiecutter template safely (trust + vendoring)

- Intent:
  - Adopt an external template without silently trusting arbitrary code execution.
- Starting state:
  - Generated monorepo; has `git` and `cookiecutter` on PATH.
- Variations worth exploring:
  - Template is untrusted by default; running once with `--trust`; then vendoring for long-lived use.
- What counts as success (evidence):
  - Untrusted generator refuses to run without `--trust`.
  - Vendoring creates `tools/templates/vendor/<id>/` with `UPSTREAM.toml`, and the manifest captures generator metadata
    (source/ref/resolved commit).
- Likely forks:
  - Whether to allow external templates at all vs requiring vendoring.
- Failure meaning:
  - Could indicate missing prerequisites (`git`/`cookiecutter`) or unclear trust model ergonomics.
- Unknowns this mission is meant to surface:
  - Which metadata is most useful to record for auditing and upgrades.

---

## User-journey metrics (observed signals)

> No budgets here by default. These are measurements used to learn and compare over time.

- Time-to-decision:
  - Definition: time from first opening `README.md` to being able to generate a monorepo and run `doctor`, with evidence of
    how to add/run a project.
- Evidence coverage:
  - Definition: fraction of key claims backed by runnable commands and referenced paths in the repo (docs/tests/templates).
- Backtracking / reversals:
  - Definition: times a user abandons one generator/toolchain approach and switches due to friction.
- Fix-forward cost:
  - Definition: effort to recover from common mistakes (missing toolchain, wrong generator, network restrictions).
- Surprise discovery rate:
  - Definition: new constraints/assumptions discovered during the first scaffold/add/project run (OS/path/encoding/tooling).
- Doc reliance map:
  - Definition: which docs were consulted, and at what decision point (repo README vs template README vs scaffold README).

---

## Open questions & unknowns backlog

- Field notes from downstream usage (generated repos) have highlighted common sharp edges; this repo now mitigates several:
  - Command generators: use repo-relative `{dest_path}` for Vite by default; scaffold runner handles Windows `.cmd` shims.
  - Tool availability + recovery: missing commands raise `ScaffoldError` (no tracebacks); `scaffold add` preflights the
    install tool when install will run; `scaffold remove` can unregister projects (optionally deleting the directory).
  - Manifest ergonomics: `scaffold projects` lists what is recorded in `tools/scaffold/monorepo.toml`.
  - Task templating: generator task commands support substitutions/placeholders so recorded task paths match generated
    file/layout substitutions (no leftover `__NAME_SNAKE__` / `{name_snake}` when used).
  - Python/PDM: PDM app template installs as a package (avoids import surprises); generated `.gitignore` ignores `.venv/`.
  - Docs: generated template docs avoid smart-quote mojibake and call out "internal templates copied without render".
- Should `scaffold add` be "atomic" (only write to `monorepo.toml` after install succeeds), or keep the current behavior
  (record the project even if install fails) as an audit trail?
- Should `scaffold add` grow a `--dry-run` mode that prints tool requirements + planned actions without touching disk?
- Should the scaffolder support an "adopt/register existing directory" flow to resolve orphaned on-disk projects that are
  not in the manifest?
- Should command generators be required to be non-interactive by policy, or should the tool add a `--non-interactive`
  mode that rejects/polices interactive commands?
- Should `doctor` proactively check `cookiecutter` availability (or only enforce it at `scaffold add` time)?
- Should the default `web` generator pin `create-vite`/Vite versions for reproducibility, or treat it as inherently
  networked?
- What is the minimum support contract for Windows/macOS (developer workstations only vs CI coverage)?
- What is the Python version policy for the template repo CI (e.g., when to add 3.13)?
- What is the desired policy for template upgrades in already-generated monorepos (if any)?
- Which ecosystems need first-class generators next (beyond Python/Node/Terraform), and what baseline tasks should be
  required?
