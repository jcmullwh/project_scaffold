from __future__ import annotations

import re
from pathlib import Path


def _extract_hook_exclude(config_text: str, hook_id: str) -> str:
    marker = f"- id: {hook_id}"
    start = config_text.find(marker)
    assert start != -1, f"Missing hook: {hook_id}"

    next_hook = config_text.find("\n      - id: ", start + len(marker))
    if next_hook == -1:
        next_hook = len(config_text)
    block = config_text[start:next_hook]

    match = re.search(r"exclude:\s*'([^']+)'", block)
    assert match is not None, f"Missing exclude for hook: {hook_id}"
    return match.group(1)


def test_ruff_hooks_exclude_cookiecutter_and_dropins_paths() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config_text = (repo_root / ".pre-commit-config.yaml").read_text(encoding="utf-8")

    positives = [
        ".agents/dropins/example.py",
        ".agents\\dropins\\example.py",
        "templates/monorepo-root/x/tools/templates/internal/foo.py",
        "templates\\monorepo-root\\x\\tools\\templates\\internal\\foo.py",
    ]
    negatives = [
        "tests/test_scaffold_monorepo_template.py",
        "tools/check_pytest_config.py",
    ]

    for hook_id in ("ruff", "ruff-format"):
        pattern = _extract_hook_exclude(config_text, hook_id)
        regex = re.compile(pattern)

        for sample in positives:
            assert regex.search(sample), f"{hook_id} should exclude: {sample}"
        for sample in negatives:
            assert not regex.search(sample), f"{hook_id} should not exclude: {sample}"
