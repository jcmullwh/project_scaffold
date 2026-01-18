# agents.md

## What this repo is

The primary “product” is not only the end result, but:
- a **repeatable run**
- **easy experimentation**
- a strong **audit trail** (what happened, why, with what inputs)

---

## General notes

### This file is binding
If you are implementing work here (human or agent), treat this document as **binding**.

If you believe it conflicts with another document:
1) **stop**, and  
2) **escalate** (do not “pick one” and continue).

### This is an experimental prototype
This project is a novel experimental prototype. That means:
- We do **not** know what will or won’t work.
- We also do **not** know which small assumptions will have outsized effects on prototype performance.

Therefore:
- Take a **first-principles** approach.
- Make assumptions only when necessary, and document them.
- Optimize for **accuracy and quality first**.
- Do **not** assume “typical” approaches are good enough.

### What we do not optimize for
We do not care about “scalability,” “shipping,” or “user experience” in the traditional product sense.

### No placeholder behavior in the real pipeline
Half-thought stand-ins (“toy implementations,” placeholders, stubs) add noise and unknown impacts. This is **unacceptable in the actual runtime pipeline**.

(Tests are a separate concern; see **Offline testability** below.)

### Everything is part of the chain
This system is a chain of parts. Unlike typical systems, every link matters, because we cannot predict which link will break the experiment.

### Defaults and fallbacks are dangerous
- Avoid “fallbacks.” **Never allow a silent fallback.** Prefer loud failures over quiet degradation.
- Avoid defaults. **Never allow a silent default.** Defaults hide decisions that affect experimental outcomes.

If a default or fallback is truly necessary, it must be:
- explicit,
- documented,
- logged loudly,
- and (for fallbacks) **human-approved**.

### Logging, docstrings, and docs
- **Log heavily.**
- **All functions must have clear docstrings.**
- Always check and update docs when behavior, invariants, inputs/outputs, or transcript contents change.

## Specific guidelines

### Use pdm
These instructions are for developing **this repository** (the template/scaffolding system repo). They do **not** imply that generated monorepos must use PDM.

- NEVER use `python -m` or `pip` directly in this repo’s development workflow.
- ALWAYS use `pdm run` or `pdm install` so the correct environment and dependencies are used.

Generated monorepos produced by this repo’s templates should treat Python environment management as a **per-project** choice (Poetry/uv/pip-tools/conda/PDM/etc.) expressed via explicit `tasks.*` commands in their `tools/scaffold/registry.toml` and recorded in `tools/scaffold/monorepo.toml`. The generated `tools/scaffold` CLI itself should run with plain `python` and must not assume PDM exists.


## Planning and tracking (required)

### Repository tracking structure

All work artifacts must be created, retained, and maintained under `.agents/`.

#### Ideas live in:
- `.agents/ideas/`

#### Plans live in:
- `.agents/plans/2 - ready/`
- `.agents/plans/3 - in_progress/`
- `.agents/plans/4 - for_review/`
- `.agents/plans/5 - complete/`

#### Todos/specs live in:
- `.agents/todos/2 - ready/`
- `.agents/todos/3 - in_progress/`
- `.agents/todos/4 - for_review/`
- `.agents/todos/5 - complete/`

### Definitions
- **Idea**: an early-stage concept that requires refinement into a spec/plan before work begins.
- **Todo/spec**: a small item that can be completed in **< 1 hour**.
- **Execution plan**: a larger item that may take **multiple hours or days**.

### Planning is mandatory
- When you are given work, you **must** create and use a plan.
- Use `.agents/PLANS.md` as the **template** for your plan document.
- Record decisions, assumptions, and roadblocks **in the plan document** as they occur.

### State transitions
When starting work:
- Move the relevant doc from `ideas` or `ready` → `in_progress`.

When implementation is complete:
- Move `in_progress` → `for_review`.

After review and revisions:
- Move `for_review` → `complete`.

If you are directed to work on something in an `ideas` folder:
- First move it to `ready` and refine it into a usable spec/plan **before** implementation work begins.

### Keep references current
Whenever you move a plan or todo, update any docs/links that reference its location.

---

## Core invariants

### 1) No silent fallbacks
If something is missing, invalid, or fails, the system must:
- **raise with a clear error** (preferred), OR
- **warn loudly** and follow a clearly documented, logged best-effort behavior  
  - Any fallback behavior must be **human-approved**.

Avoid patterns that:
- set required modules to `None` and continue,
- swallow exceptions and keep running,
- default output paths to CWD without warning.

### 2) Clarity beats cleverness
A reader should be able to understand “what runs” from the flow definition without decoding:
- opaque predicates,
- magic indices,
- hidden behavior.

### 3) No band-aids or whack-a-mole fixes
When solving a problem:
- Do not patch the symptom. Fix the **root cause**.
- Design for the **class of failure**, not the single observed instance.
- Think in **architecture terms**.

If a component is intended to be generic, the fix must remain generic. If the issue is user-specific, it belongs in user-specific layers/config—not shared pipeline logic.

Avoid anti-pattern fixes:
- hardcoded exceptions,
- one-off rules,
- narrowly scoped scoring knobs chasing a specific bug.

These accumulate, interact unpredictably, and regress elsewhere.

**Example (what not to do):**  
User preference: “I don’t like disembodied arms.”  
Bad outcome: pipeline starts injecting “well-rendered arms” into every prompt, creating irrelevant arms that are technically correct but narratively pointless.

**Incorrect fixes (not acceptable):**
- Adding “no arms” into the generic prompt pipeline. (Too specific to one preference.)
- Adding an “arm risk score” to the generic pipeline. (Narrow, brittle, noisy.)

**Correct fix (generic and scalable):**
- Add a rule that prevents the entire class of mistake:
  - “Respect dislikes by avoiding them; do not add the opposite of a dislike unless the scene genuinely requires it.”

This addresses the underlying failure mode: converting negative preferences into universal counter-instructions, which creates artificial artifacts.

### 4) Determinism when randomness is used
If randomness affects prompts or choices:
- the **seed must be recorded and logged**,
- the **seed must be stored in the transcript**,
- runs must be reproducible with the same seed.

### 5) The transcript is canonical for debugging
The transcript JSON must contain:
- step-by-step prompts/responses + parameters,
- nested pipeline paths,
- seed and selected concepts,
- error metadata on failure,
- **any new category of information introduced by the project** (update transcript schema/docs accordingly).

The transcript is **not** model context. It is a recorder.

### 6) Offline testability
All tests must run offline:
- mock/fake LLM and image backends,
- no network calls,
- no real external binaries (use fakes or platform-safe stubs).

(Using fakes/stubs in **tests** is encouraged; using placeholders/stubs in the **runtime pipeline** is not.)

---
