---
id: project_scaffold_smoke
name: "project_scaffold: Smoke"
extends: first_output_smoke
tags: [project_scaffold, p0]
execution_mode: single_pass_inline_report
prompt_template: default_inline_report.prompt.md
report_schema: project_scaffold_report_v1.schema.json
---
Goal: produce a full e2e test of the system.

Do the most complete meaningful verification you can for your use case.
