"""
CI guard: ensure pytest config stays scoped to the real test suite.

This repository includes Cookiecutter templates under `templates/` that contain Jinja placeholders. If pytest's
collection scope drifts, pytest may try to collect template files and fail with confusing syntax errors.

We enforce `[tool.pytest.ini_options].testpaths = ["tests"]` in `pyproject.toml`.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    pyproject_path = repo_root / "pyproject.toml"

    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    testpaths = data.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("testpaths")

    expected = ["tests"]
    if testpaths != expected:
        print("ERROR: pytest config drift detected.", file=sys.stderr)
        print("", file=sys.stderr)
        print(
            "Expected pyproject.toml to contain:",
            file=sys.stderr,
        )
        print("  [tool.pytest.ini_options]", file=sys.stderr)
        print('  testpaths = ["tests"]', file=sys.stderr)
        print("", file=sys.stderr)
        print(f"Observed [tool.pytest.ini_options].testpaths = {testpaths!r}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
