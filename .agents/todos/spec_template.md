## Spec template for this project

### Task
One sentence. Example: “Threaded enclave opinions: one response per artist, independent threads, then consensus.”

### Goal
Describe user-visible and developer-visible outcomes.

- What changes in outputs (transcript structure, prompts, images, manifest rows)?
- What becomes easier to experiment with?

### Context
What exists now and why it’s insufficient.

If pipeline-related, state:
- where the steps are defined (usually a pipeline spec or pipeline construction function),
- what is currently captured in the transcript/logs/DB,
- what currently gets merged/returned as outputs.

### Constraints
Include the ones that apply:

- No silent fallbacks
- Offline tests
- Deterministic randomness
- Cross-platform behavior
- Backwards compatibility for artifact schemas (if applicable)

### Non-goals
Explicitly list what you are not doing.

### Functional requirements
Numbered FRs. Each FR must specify:

- behavior
- inputs/outputs
- failure behavior (raise vs warn)
- observability (what will appear in transcript/logs)

#### Project-specific FR items to include when relevant
- Config validation (define paths/types; fail on invalid types)
- Pipeline paths (ensure transcript path uniqueness)
- Error attribution (error_code + details + stderr refs where applicable)

### Proposed flow (most important section)
Show “just the flow”. Use the same Step/Block shape as code/config.

### Implementation plan
Ordered steps, including which files change.

### Error handling + observability contract
For each new failure point:
- What exception is raised?
- What error fields are recorded?
- What transcript/log events appear?

### Data/artifact changes
Document new/changed artifact or entity schemas and compatibility.

### Testing requirements (pytest, offline)
Rules:
- No network
- Default test suite runs without external binaries
- Integration tests (if any) must be opt-in via env var

### Documentation updates
What docs must be updated and where.

### Acceptance criteria
Concrete, verifiable outcomes.

