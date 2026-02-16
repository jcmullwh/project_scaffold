from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run_check_personas(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    script = repo_root / "tools" / "check_persona_ids.py"
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(repo_root),
        text=True,
        capture_output=True,
    )


def test_usertest_persona_ids_are_unique() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    cp = _run_check_personas(repo_root)
    assert cp.returncode == 0, cp.stderr
    assert "all ids are unique" in cp.stdout


def test_check_persona_ids_reports_deterministic_collisions(tmp_path: Path) -> None:
    personas_dir = tmp_path / "personas"
    personas_dir.mkdir(parents=True)

    (personas_dir / "b.persona.md").write_text(
        "---\nid: same-id\nname: B\n---\n",
        encoding="utf-8",
    )
    (personas_dir / "a.persona.md").write_text(
        "---\nid: same-id\nname: A\n---\n",
        encoding="utf-8",
    )
    (personas_dir / "missing.persona.md").write_text(
        "---\nname: Missing\n---\n",
        encoding="utf-8",
    )

    repo_root = Path(__file__).resolve().parents[1]
    cp = _run_check_personas(repo_root, "--personas-dir", str(personas_dir))

    assert cp.returncode == 1
    out = cp.stderr
    assert "Files missing front-matter id:" in out
    assert f"  - {personas_dir / 'missing.persona.md'}" in out
    assert "Duplicate persona ids:" in out
    assert "  - same-id" in out
    assert out.index(f"    - {personas_dir / 'a.persona.md'}") < out.index(f"    - {personas_dir / 'b.persona.md'}")
