# Todos

This repo tracks todo/spec documents in `.agents/todos/` and execution plans in `.agents/plans/`.

Directory structure:

- `.agents/todos/1 - ideas/`
- `.agents/todos/2 - ready/`
- `.agents/todos/3 - in_progress/`
- `.agents/todos/4 - for_review/`
- `.agents/todos/5 - complete/`

The current in-progress todo/spec document(s) should always live in `.agents/todos/3 - in_progress/`.

todos/specs are smaller items that can be completed in less than an hour.

Execution plans are larger items that may take multiple hours or days to complete. Execution plans should be tracked in `.agents/plans/` with the same directory structure concept as `.agents/todos/`.

When starting work on a new todo/spec or execution plan, move the document from the `ideas` or `ready` folder to the `in_progress` folder. When the work is complete, move the document to the `for_review` folder for review. After review and any necessary revisions, move the document to the `complete` folder.

Ideas require additional refinement. If directed to work on an item in an `ideas` folder, first move it to the `ready` folder and refine it into a plan or spec before starting work.
