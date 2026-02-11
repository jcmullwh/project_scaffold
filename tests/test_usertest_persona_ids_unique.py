from __future__ import annotations

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


def test_usertest_persona_ids_are_unique() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    personas_dir = repo_root / ".usertest" / "personas"
    paths = sorted(personas_dir.glob("*.persona.md"))
    assert paths, f"No persona files found under: {personas_dir}"

    seen: dict[str, Path] = {}
    for path in paths:
        persona_id = _extract_id_from_front_matter(path.read_text(encoding="utf-8"))
        assert persona_id is not None, f"Missing persona id in {path}"
        prev = seen.get(persona_id)
        assert prev is None, f"Duplicate persona id {persona_id!r} in {prev} and {path}"
        seen[persona_id] = path
