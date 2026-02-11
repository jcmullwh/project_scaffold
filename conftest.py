"""
Pytest configuration guard for the template repo.

This repository contains Cookiecutter templates under `templates/` that include Jinja placeholders (for example
`{{cookiecutter.project_slug}}`). If pytest is misconfigured to collect outside `tests/`, it can attempt to import or
collect those template files and fail with confusing syntax errors unrelated to the actual test suite.

We enforce `testpaths = ["tests"]` so collection stays scoped to the real tests.
"""

from __future__ import annotations

from typing import Any, Protocol

_EXPECTED_TESTPATHS = ["tests"]


class _PytestConfig(Protocol):
    def getini(self, name: str) -> Any:  # pragma: no cover
        ...


class _PytestUsageError(Exception):
    """Raised when pytest is configured in an unsafe way for this repository."""


def pytest_configure(config: _PytestConfig) -> None:
    """Fail early with an actionable error if pytest collection scope drifts."""

    # `getini("testpaths")` returns a list-like value, or an empty list if unset.
    testpaths = list(config.getini("testpaths") or [])
    if testpaths != _EXPECTED_TESTPATHS:
        raise _PytestUsageError(
            "Pytest is misconfigured for this repository.\n"
            "\n"
            "Expected [tool.pytest.ini_options] testpaths = ['tests'] in pyproject.toml.\n"
            "Collecting outside tests/ can pick up Cookiecutter template files under templates/ that contain\n"
            "Jinja placeholders (for example '{{cookiecutter.project_slug}}') and are not valid Python.\n"
            "\n"
            f"Observed testpaths = {testpaths!r}\n"
        )
