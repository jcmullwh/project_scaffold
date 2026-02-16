from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _extract_id_from_front_matter(text: str) -> str | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    for line in lines[1:]:
        if line.strip() == "---":
            return None
        if line.startswith("id:"):
            value = line.split(":", maxsplit=1)[1].strip()
            return value or None
    return None


def _scan_personas(personas_dir: Path) -> tuple[list[Path], dict[str, list[Path]]]:
    files = sorted(personas_dir.glob("*.persona.md"), key=lambda p: p.as_posix())
    missing_id_paths: list[Path] = []
    by_id: dict[str, list[Path]] = {}

    for path in files:
        persona_id = _extract_id_from_front_matter(path.read_text(encoding="utf-8"))
        if persona_id is None:
            missing_id_paths.append(path)
            continue
        by_id.setdefault(persona_id, []).append(path)

    duplicates = {
        persona_id: sorted(paths, key=lambda p: p.as_posix()) for persona_id, paths in by_id.items() if len(paths) > 1
    }
    return sorted(missing_id_paths, key=lambda p: p.as_posix()), duplicates


def _render_errors(
    *,
    personas_dir: Path,
    missing_id_paths: list[Path],
    duplicates: dict[str, list[Path]],
) -> str:
    lines: list[str] = []
    lines.append(f"Persona id validation failed for {personas_dir}")

    if missing_id_paths:
        lines.append("")
        lines.append("Files missing front-matter id:")
        for path in missing_id_paths:
            lines.append(f"  - {path}")

    if duplicates:
        lines.append("")
        lines.append("Duplicate persona ids:")
        for persona_id in sorted(duplicates):
            lines.append(f"  - {persona_id}")
            for path in duplicates[persona_id]:
                lines.append(f"    - {path}")

    lines.append("")
    lines.append("Remediation: give each persona a unique front-matter `id:` value.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate .persona.md files have unique front-matter ids.")
    parser.add_argument(
        "--personas-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / ".usertest" / "personas",
        help="Directory containing *.persona.md files.",
    )
    args = parser.parse_args(argv)

    personas_dir: Path = args.personas_dir
    if not personas_dir.exists() or not personas_dir.is_dir():
        print(f"ERROR: Personas directory not found: {personas_dir}", file=sys.stderr)
        return 1

    files = sorted(personas_dir.glob("*.persona.md"), key=lambda p: p.as_posix())
    if not files:
        print(f"ERROR: No persona files found under: {personas_dir}", file=sys.stderr)
        return 1

    missing_id_paths, duplicates = _scan_personas(personas_dir)
    if missing_id_paths or duplicates:
        print(
            _render_errors(
                personas_dir=personas_dir,
                missing_id_paths=missing_id_paths,
                duplicates=duplicates,
            ),
            file=sys.stderr,
        )
        return 1

    print(f"OK: {len(files)} persona files checked; all ids are unique.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
