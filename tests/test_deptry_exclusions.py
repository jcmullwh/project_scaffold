from __future__ import annotations

import re
import tomllib
from pathlib import Path


def test_pyproject_toml_parses_and_deptry_exclusions_cover_expected_paths() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    pyproject_path = repo_root / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    tool = pyproject.get("tool")
    assert isinstance(tool, dict)
    deptry = tool.get("deptry")
    assert isinstance(deptry, dict)
    patterns = deptry.get("extend_exclude")
    assert isinstance(patterns, list)

    pattern_strs = [p for p in patterns if isinstance(p, str) and p.strip()]
    assert pattern_strs

    samples = [
        ".agents/dropins/example.py",
        ".agents\\dropins\\example.py",
        "tools/templates/internal/python-pdm-lib/pyproject.toml",
        "tools\\templates\\internal\\python-pdm-lib\\pyproject.toml",
        "templates/monorepo-root/x/tools/monorepo_publish/publish_snapshots.py",
        "templates\\monorepo-root\\x\\tools\\monorepo_publish\\publish_snapshots.py",
    ]

    for sample in samples:
        assert any(re.search(pat, sample) for pat in pattern_strs), sample
