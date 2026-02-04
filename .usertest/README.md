# `.usertest/`

This folder is for **external runner configuration** (e.g., the `usertest` runner). It is not used by the
`project_scaffold` runtime itself.

## `catalog.yaml`

`catalog.yaml` allows the external runner to discover **repo-specific personas, missions, and report schemas**.

- `.usertest/personas/` (`*.persona.md`)
- `.usertest/missions/` (`*.mission.md`)
- `.usertest/report_schemas/` (`*.schema.json`)
