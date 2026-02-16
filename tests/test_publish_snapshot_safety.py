from __future__ import annotations

from pathlib import Path


def _read(path: str) -> str:
    repo_root = Path(__file__).resolve().parents[1]
    return (repo_root / path).read_text(encoding="utf-8")


def test_publish_workflow_is_safe_by_default_and_manual_for_real_uploads() -> None:
    workflow = _read("templates/monorepo-root/{{cookiecutter.repo_slug}}/.github/workflows/publish-snapshots.yml")

    assert "workflow_dispatch:" in workflow
    assert "confirm_publish:" in workflow
    assert "python tools/monorepo_publish/publish_snapshots.py --self-test" in workflow
    assert "python tools/monorepo_publish/publish_snapshots.py --dry-run" in workflow
    assert "inputs.confirm_publish == 'publish'" in workflow
    assert "python tools/monorepo_publish/publish_snapshots.py --confirm-publish" in workflow


def test_publish_script_requires_confirm_flag_for_real_publish() -> None:
    script = _read("templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/monorepo_publish/publish_snapshots.py")
    publish_readme = _read("templates/monorepo-root/{{cookiecutter.repo_slug}}/tools/monorepo_publish/README.md")

    assert "--confirm-publish" in script
    assert "Refusing to publish without --confirm-publish" in script
    assert "python tools/monorepo_publish/publish_snapshots.py --confirm-publish" in publish_readme
    assert "Safety default" in publish_readme
