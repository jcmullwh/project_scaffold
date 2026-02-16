from __future__ import annotations

from pathlib import Path


def _read(path: str) -> str:
    repo_root = Path(__file__).resolve().parents[1]
    return (repo_root / path).read_text(encoding="utf-8")


def test_root_readme_covers_repo_context_workflow_defaults_and_windows_fallback() -> None:
    readme = _read("README.md")

    assert "## What This Repo Is / Isn't" in readme
    assert "First success is always a three-step flow:" in readme
    assert "cookiecutter templates/monorepo-root --no-input -o .tmp" in readme
    assert "cd .tmp/my-monorepo" in readme
    assert "python tools/scaffold/scaffold.py doctor" in readme
    assert "Expected success signal: `doctor` prints `OK` and exits with code `0`." in readme

    assert "Recommended defaults:" in readme
    assert "evaluation and smoke validation" in readme
    assert "contributors and template CI parity" in readme

    assert "## If `pdm install` Hangs on Windows" in readme
    assert "no new output for 5 or more minutes" in readme
    assert "python -m pip install cookiecutter" in readme
    assert "python -m pytest -q tests/test_scaffold_monorepo_template.py" in readme

    assert "## Two CI Layers" in readme
    assert ".github/workflows/ci.yml" in readme
    assert "templates/monorepo-root/{{cookiecutter.repo_slug}}/.github/workflows/ci.yml" in readme

    assert "Get-Content -LiteralPath 'templates/monorepo-root/{{cookiecutter.repo_slug}}/README.md'" in readme


def test_contributing_and_troubleshooting_cover_dropins_and_windows_pdm_hang() -> None:
    contributing = _read("CONTRIBUTING.md")
    troubleshooting = _read("docs/TROUBLESHOOTING.md")

    assert "## If `pdm install` hangs on Windows" in contributing
    assert "no new output for 5 or more minutes" in contributing
    assert "python -m pip install cookiecutter pytest" in contributing
    assert "required tool excludes" in contributing

    assert "### `pdm install` hangs on Windows" in troubleshooting
    assert "python -m pip install cookiecutter" in troubleshooting
    assert 'See also the root README section "PowerShell Note for `{{cookiecutter...}}` Paths".' in troubleshooting


def test_architecture_and_workflows_document_dual_ci_layers() -> None:
    architecture = _read("docs/ARCHITECTURE.md")
    root_ci = _read(".github/workflows/ci.yml")
    generated_ci = _read("templates/monorepo-root/{{cookiecutter.repo_slug}}/.github/workflows/ci.yml")

    assert "## Two CI layers" in architecture
    assert ".github/workflows/ci.yml" in architecture
    assert "templates/monorepo-root/{{cookiecutter.repo_slug}}/.github/workflows/ci.yml" in architecture

    assert "# Scope: Template repository CI." in root_ci
    assert "# Scope: Generated monorepo CI." in generated_ci
    assert "Persona id guard" in root_ci
    assert "windows-smoke:" in root_ci
