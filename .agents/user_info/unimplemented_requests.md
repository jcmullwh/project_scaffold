# Requested changes/features (not implemented)

This is a consolidated backlog of items requested or suggested during downstream use of `project_scaffold`.

These are inputs, not commitments; some items overlap or conflict.

## Scaffolder CLI (`tools/scaffold/scaffold.py`)

| Category | Request | Deferred because | Notes / dependencies |
|---|---|---|---|
| Significant Work | Make `scaffold add` atomic (no partial state) | Requires a transactional design across generator types and a safe rollback policy for side effects. | Partial mitigations exist: install-tool preflight, clear errors, and `scaffold remove` for recovery. |
| Design Needed | Add `scaffold add --dry-run` | Needs clear semantics for what can be predicted without running generators (especially `command`). | Could start as "print plan + required tools" with zero writes. |
| Design Needed | Add "adopt/register existing directory" | Needs a model for declaring/inferring kind/generator/tasks for an existing directory, with safety checks. | Would address "orphaned on-disk project not in manifest". |
| Safety/Risk | Add `scaffold add --force` / `--overwrite` | Destructive; needs explicit confirmation UX, safety rules, and cross-platform deletion tests. | Likely pairs with `remove --delete-dir`. |
| Policy Decision | Add a non-interactive mode / policy for interactive generators | Hard to detect/enforce interactivity generically across third-party tools; needs a policy decision + error contract. | Relevant to `npm create ...@latest` and other networked CLIs. |
| Conflicting | Add a lenient mode for missing toolchains (e.g., `doctor --lenient`, `run --skip-missing-tools`) | Conflicts with "no silent fallbacks"; would need explicit opt-in semantics that stays loud and auditable. | Different environments (dev vs CI) may want different strictness. |
| Env-dependent | `doctor` verifies `cookiecutter` CLI (e.g., `cookiecutter --version`) | Needs a decision: "CLI on PATH" vs "Python package importable"; tricky to test without assuming the CLI is always available. | Today: Cookiecutter generators fail fast at `add` time. |

## Generators and templates (`tools/templates/**`, `tools/scaffold/registry.toml`)

| Category | Request | Deferred because | Notes / dependencies |
|---|---|---|---|
| Scope Expansion | Built-in templates for Go, Rust, TypeScript | Each ecosystem needs conventions, tasks, and offline tests that don't rely on external binaries. | Also needs kind/CI policy decisions. |
| Significant Work | Workspace integration (Cargo workspaces, npm/pnpm workspaces) | Adds top-level opinions and cross-project coupling; needs design to keep the scaffold minimal and adaptable. | Likely touches generated root files + CI/task expectations. |
| Design Needed | Improve "production realism" of templates | Too broad without concrete requirements per template; needs focused template specs. | Best handled incrementally per template. |
| Policy Decision | Reproducible web scaffolding policy (pin/vendoring for Vite/create-vite) | Requires a policy decision on pinning/vendoring vs "networked by default", plus handling interactive prompts. | Current posture: command generators may be networked; docs call it out. |

## Cookiecutter inputs (`templates/monorepo-root/cookiecutter.json`)

| Category | Request | Deferred because | Notes / dependencies |
|---|---|---|---|
| Compatibility Risk | Rename/reshape root variables for ergonomics (e.g., `repo_slug` -> `project_name`) | Backward-compat risk; changes prompt surface and can break docs/tests/automation; needs a migration/alias plan. | Could support both names temporarily, but must be explicit and tested. |

## CI/runtime support policy

| Category | Request | Deferred because | Notes / dependencies |
|---|---|---|---|
| Policy Decision | Add/validate Python 3.13 in CI (repo CI and/or generated-monorepo CI), including Windows/macOS | Increases CI matrix/time and can surface dependency/tooling incompatibilities that require ongoing upkeep. | Needs a "required vs best-effort" matrix policy. |
| Policy Decision | Clarify the Windows/macOS "support contract" (dev only vs CI) | Policy decision, not a single code change; needs agreement on what is "supported" and tested. | Should then drive CI matrix and template guarantees. |

## Documentation gaps

| Category | Request | Deferred because | Notes / dependencies |
|---|---|---|---|
| Doc Work | Document per-project lockfile expectations (e.g., PDM often creates one lock per project) | Needs a decision on where this belongs (root docs vs generated-monorepo docs) and how opinionated to be across toolchains. | Downstream note: easy to miss if you expect a single monorepo lock. |

