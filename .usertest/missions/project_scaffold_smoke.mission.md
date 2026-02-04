---
id: project_scaffold_smoke
name: "project_scaffold: Smoke"
extends: first_output_smoke
tags: [project_scaffold, p0]
execution_mode: single_pass_inline_report
prompt_template: default_inline_report.prompt.md
report_schema: project_scaffold_report_v1.schema.json
---
Goal: produce a first useful, correct output for `project_scaffold` with minimal risk.

Do the smallest meaningful verification you can:

1) Identify what templates exist under `templates/` and how they're intended to be used.
2) Prefer `pdm run pytest` (or a narrower equivalent) if deps are already installed.
3) If execution is blocked, identify the minimal missing prereq(s) and exact remediation steps.
