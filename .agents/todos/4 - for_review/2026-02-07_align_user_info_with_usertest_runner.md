## Spec template for this project

### Task
Align `.agents/user_info/` with the latest `usertest` runner expectations from `I:\\code\\test_and_throwaway\\user_agent_implementation_1` by making `USERS.md` the canonical repo-root user context file and keeping `.agents/user_info/` focused on templates/supporting docs.

### Goal
- The repo root contains a rich `USERS.md` suitable for external runners/tools that read `USERS.md`.
- `.agents/user_info/` contains a clearly named template for `USERS.md`, plus a short README explaining the layout.
- The feature/request backlog is not stored under `user_info/`.

### Context
The `agentic-usertest-monorepo` runner reads (and can optionally pass through) `USERS.md` from a target repo workspace, so
keeping user context at repo root is the most interoperable structure.

### Constraints
- Keep changes doc-only (no runtime behavior changes).
- Preserve existing user notes content.
- Update any internal `.agents/*` references when moving/renaming files.

### Functional requirements
1) The canonical user context file is `USERS.md` at repo root.
2) `.agents/user_info/` contains:
   - `.agents/user_info/USERS.template.md`
   - `.agents/user_info/README.md`
3) The backlog file lives outside `user_info/` (under `.agents/todos/`).
4) Any `.agents/` plan/spec references are updated to the new paths.

### Testing requirements (pytest, offline)
Not applicable (docs-only change). Verify by checking paths exist and `rg` finds no stale references.

### Acceptance criteria
- `USERS.md` exists at repo root and contains the prior detailed user notes.
- `.agents/user_info/users*.md` and `.agents/user_info/unimplemented_requests.md` no longer exist.
- `.agents/user_info/USERS.template.md` exists and includes a brief note that it is a template for repo-root `USERS.md`.
- `.agents/todos/1 - ideas/unimplemented_requests.md` exists.

