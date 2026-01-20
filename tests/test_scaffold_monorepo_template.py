import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from cookiecutter.main import cookiecutter


def _template_root() -> Path:
    return Path(__file__).resolve().parents[1] / "templates" / "monorepo-root"


def _run_scaffold(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    scaffold_py = repo_root / "tools" / "scaffold" / "scaffold.py"
    assert scaffold_py.exists()

    env = os.environ.copy()
    scripts_dir = str(Path(sys.executable).resolve().parent)
    env["PATH"] = scripts_dir + os.pathsep + env.get("PATH", "")

    return subprocess.run(
        [sys.executable, str(scaffold_py), *args],
        cwd=str(repo_root),
        env=env,
        text=True,
        capture_output=True,
    )


def _render_monorepo(tmp_path: Path, *, repo_slug: str = "demo-monorepo") -> Path:
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    created_path = cookiecutter(
        str(_template_root()),
        no_input=True,
        extra_context={"repo_slug": repo_slug, "repo_name": repo_slug},
        output_dir=str(out_dir),
    )
    repo_root = Path(created_path)
    assert repo_root.exists()
    return repo_root


def _git_available() -> bool:
    return shutil.which("git") is not None


def _create_upstream_cookiecutter_repo(tmp_path: Path) -> tuple[Path, str, str]:
    repo_dir = tmp_path / "upstream_template"
    repo_dir.mkdir()

    # Minimal cookiecutter template with python stdlib tests.
    (repo_dir / "cookiecutter.json").write_text(
        '{\n  "project_slug": "my-project",\n  "package_name": "my_project"\n}\n', encoding="utf-8"
    )
    tmpl_root = repo_dir / "{{cookiecutter.project_slug}}"
    (tmpl_root / "src" / "{{cookiecutter.package_name}}").mkdir(parents=True)
    (tmpl_root / "tests").mkdir(parents=True)

    (tmpl_root / "src" / "{{cookiecutter.package_name}}" / "__init__.py").write_text(
        "def add(a: int, b: int) -> int:\n    return a + b\n",
        encoding="utf-8",
    )
    (tmpl_root / "tests" / "test_basic.py").write_text(
        "import pathlib\n"
        "import sys\n"
        "import unittest\n"
        "\n"
        "PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]\n"
        "sys.path.insert(0, str(PROJECT_ROOT / 'src'))\n"
        "\n"
        "class TestBasic(unittest.TestCase):\n"
        "    def test_add(self) -> None:\n"
        "        import {{ cookiecutter.package_name }}\n"
        "        self.assertEqual({{ cookiecutter.package_name }}.add(2, 3), 5)\n"
        "\n"
        "if __name__ == '__main__':\n"
        "    unittest.main()\n",
        encoding="utf-8",
    )
    (tmpl_root / "README.md").write_text("# {{ cookiecutter.project_slug }}\n", encoding="utf-8")

    (repo_dir / "LICENSE").write_text("MIT License\n\nPermission is hereby granted...\n", encoding="utf-8")

    subprocess.run(["git", "init"], cwd=str(repo_dir), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(repo_dir), check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(repo_dir), check=True)
    subprocess.run(["git", "add", "."], cwd=str(repo_dir), check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(repo_dir), check=True, capture_output=True)
    rev = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(repo_dir), check=True, text=True, capture_output=True
    ).stdout.strip()
    return repo_dir, rev, repo_dir.as_uri()


def test_template_renders_and_internal_templates_are_not_rendered(tmp_path: Path) -> None:
    repo_root = _render_monorepo(tmp_path, repo_slug="demo-1")

    # Root exists and includes scaffold tool.
    assert (repo_root / "tools" / "scaffold" / "scaffold.py").exists()
    assert (repo_root / "tools" / "scaffold" / "registry.toml").exists()
    assert (repo_root / "tools" / "scaffold" / "monorepo.toml").exists()

    workflow_path = repo_root / ".github" / "workflows" / "ci.yml"
    assert workflow_path.exists()
    workflow = workflow_path.read_text(encoding="utf-8")
    assert "scaffold.py doctor" in workflow
    assert "scaffold.py run install" in workflow

    # Internal cookiecutter template should be copied without render (literal {{cookiecutter.*}} path exists).
    internal_cc = (
        repo_root
        / "tools"
        / "templates"
        / "internal"
        / "python-stdlib-cookiecutter"
        / "{{cookiecutter.project_slug}}"
        / "README.md"
    )
    assert internal_cc.exists()


def test_scaffold_add_copy_and_run_task(tmp_path: Path) -> None:
    repo_root = _render_monorepo(tmp_path, repo_slug="demo-2")

    cp = _run_scaffold(repo_root, "doctor")
    assert cp.returncode == 0, cp.stderr

    cp = _run_scaffold(repo_root, "add", "app", "billing-api")
    assert cp.returncode == 0, cp.stderr
    assert (repo_root / "apps" / "billing-api").exists()

    cp = _run_scaffold(repo_root, "run", "test", "--project", "billing-api")
    assert cp.returncode == 0, cp.stderr


def test_scaffold_add_internal_cookiecutter(tmp_path: Path) -> None:
    repo_root = _render_monorepo(tmp_path, repo_slug="demo-3")

    cp = _run_scaffold(repo_root, "add", "app", "ccproj", "--generator", "python_stdlib_cookiecutter")
    assert cp.returncode == 0, cp.stderr
    assert (repo_root / "apps" / "ccproj").exists()

    cp = _run_scaffold(repo_root, "run", "test", "--project", "ccproj")
    assert cp.returncode == 0, cp.stderr


def test_registry_node_vite_uses_dest_path(tmp_path: Path) -> None:
    repo_root = _render_monorepo(tmp_path, repo_slug="demo-registry-vite")

    import tomllib

    registry = tomllib.loads((repo_root / "tools" / "scaffold" / "registry.toml").read_text(encoding="utf-8"))
    node_vite = registry["generators"]["node_vite"]
    assert node_vite["type"] == "command"
    assert node_vite["command"][3] == "{dest_path}"
    assert "{dest_dir}" not in node_vite["command"]


def test_scaffold_add_pdm_generators_no_install(tmp_path: Path) -> None:
    repo_root = _render_monorepo(tmp_path, repo_slug="demo-pdm")

    cp = _run_scaffold(
        repo_root,
        "add",
        "lib",
        "mylib",
        "--generator",
        "python_pdm_lib",
        "--no-install",
    )
    assert cp.returncode == 0, cp.stderr
    assert (repo_root / "packages" / "mylib" / "pyproject.toml").exists()

    cp = _run_scaffold(
        repo_root,
        "add",
        "app",
        "myapp",
        "--generator",
        "python_pdm_app",
        "--no-install",
    )
    assert cp.returncode == 0, cp.stderr
    assert (repo_root / "apps" / "myapp" / "pyproject.toml").exists()

    import tomllib

    lib_pyproject = tomllib.loads((repo_root / "packages" / "mylib" / "pyproject.toml").read_text(encoding="utf-8"))
    assert lib_pyproject["tool"]["pdm"]["distribution"] is True

    app_pyproject = tomllib.loads((repo_root / "apps" / "myapp" / "pyproject.toml").read_text(encoding="utf-8"))
    assert app_pyproject["tool"]["pdm"]["distribution"] is True

    manifest = tomllib.loads((repo_root / "tools" / "scaffold" / "monorepo.toml").read_text(encoding="utf-8"))
    projects = manifest.get("projects", [])
    assert isinstance(projects, list)

    by_id = {p.get("id"): p for p in projects if isinstance(p, dict)}
    assert by_id["mylib"]["generator"] == "python_pdm_lib"
    assert by_id["mylib"]["package_manager"] == "pdm"
    assert by_id["mylib"]["tasks"]["install"] == ["pdm", "install"]
    assert by_id["mylib"]["tasks"]["test"] == ["pdm", "run", "pytest", "-q"]

    assert by_id["myapp"]["generator"] == "python_pdm_app"
    assert by_id["myapp"]["package_manager"] == "pdm"
    assert by_id["myapp"]["tasks"]["install"] == ["pdm", "install"]
    assert by_id["myapp"]["tasks"]["test"] == ["pdm", "run", "pytest", "-q"]


def test_manifest_preserves_unknown_project_keys(tmp_path: Path) -> None:
    repo_root = _render_monorepo(tmp_path, repo_slug="demo-manifest-preserve")

    cp = _run_scaffold(repo_root, "add", "app", "billing-api")
    assert cp.returncode == 0, cp.stderr

    manifest_path = repo_root / "tools" / "scaffold" / "monorepo.toml"
    original = manifest_path.read_text(encoding="utf-8")
    lines = original.splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == "[[projects]]":
            lines.insert(idx + 1, 'owner = "team-x"')
            break
    manifest_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    cp = _run_scaffold(repo_root, "add", "app", "payments-api")
    assert cp.returncode == 0, cp.stderr

    import tomllib

    manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    projects = manifest.get("projects", [])
    assert isinstance(projects, list)
    by_id = {p.get("id"): p for p in projects if isinstance(p, dict)}
    assert by_id["billing-api"]["owner"] == "team-x"


def test_scaffold_add_fails_when_ci_task_missing(tmp_path: Path) -> None:
    repo_root = _render_monorepo(tmp_path, repo_slug="demo-missing-ci-task")

    registry_path = repo_root / "tools" / "scaffold" / "registry.toml"
    registry_path.write_text(
        registry_path.read_text(encoding="utf-8")
        + "\n"
        + "\n"
        + "[kinds.badkind]\n"
        + 'output_dir = "apps"\n'
        + 'default_generator = "bad_gen"\n'
        + "ci = { lint = false, test = true, build = false }\n"
        + "\n"
        + "[generators.bad_gen]\n"
        + 'type = "copy"\n'
        + 'source = "tools/templates/internal/python-stdlib-copy"\n'
        + 'toolchain = "python"\n'
        + 'package_manager = "none"\n'
        + 'substitutions = { "__NAME__" = "{name}", "__NAME_SNAKE__" = "{name_snake}" }\n'
        + 'tasks.lint = ["python", "-m", "compileall", "src"]\n',
        encoding="utf-8",
    )

    cp = _run_scaffold(repo_root, "add", "badkind", "oopsproj")
    assert cp.returncode != 0
    assert "tasks.test" in (cp.stdout + cp.stderr)


def test_scaffold_add_records_poetry_generator(tmp_path: Path) -> None:
    repo_root = _render_monorepo(tmp_path, repo_slug="demo-poetry")

    cp = _run_scaffold(repo_root, "add", "app", "poetry-app", "--generator", "python_poetry_app", "--no-install")
    assert cp.returncode == 0, cp.stderr
    assert (repo_root / "apps" / "poetry-app" / "pyproject.toml").exists()

    import tomllib

    manifest = tomllib.loads((repo_root / "tools" / "scaffold" / "monorepo.toml").read_text(encoding="utf-8"))
    projects = manifest.get("projects", [])
    assert isinstance(projects, list)
    by_id = {p.get("id"): p for p in projects if isinstance(p, dict)}
    assert by_id["poetry-app"]["generator"] == "python_poetry_app"
    assert by_id["poetry-app"]["package_manager"] == "poetry"
    assert by_id["poetry-app"]["tasks"]["install"] == ["poetry", "install"]


def test_scaffold_add_command_generator(tmp_path: Path) -> None:
    repo_root = _render_monorepo(tmp_path, repo_slug="demo-cmd")

    generator_script = repo_root / "tools" / "scaffold" / "test_command_generator.py"
    generator_script.write_text(
        "import pathlib\n"
        "import sys\n"
        "\n"
        "dest_dir = pathlib.Path(sys.argv[1])\n"
        "dest_dir.mkdir(parents=True, exist_ok=True)\n"
        "(dest_dir / 'CREATED_BY_COMMAND.txt').write_text('ok\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )

    check_created = "import pathlib, sys; sys.exit(0 if pathlib.Path('CREATED_BY_COMMAND.txt').exists() else 1)"
    registry_path = repo_root / "tools" / "scaffold" / "registry.toml"
    registry_path.write_text(
        registry_path.read_text(encoding="utf-8")
        + "\n"
        + "\n"
        + "[generators.command_py]\n"
        + 'type = "command"\n'
        + 'toolchain = "generic"\n'
        + 'package_manager = "none"\n'
        + 'command = ["python", "tools/scaffold/test_command_generator.py", "{dest_dir}"]\n'
        + f'tasks.lint = ["python", "-c", "{check_created}"]\n'
        + f'tasks.test = ["python", "-c", "{check_created}"]\n',
        encoding="utf-8",
    )

    cp = _run_scaffold(repo_root, "add", "app", "cmdproj", "--generator", "command_py")
    assert cp.returncode == 0, cp.stderr
    assert (repo_root / "apps" / "cmdproj" / "CREATED_BY_COMMAND.txt").exists()

    cp = _run_scaffold(repo_root, "run", "test", "--project", "cmdproj")
    assert cp.returncode == 0, cp.stderr


@pytest.mark.skipif(not _git_available(), reason="git is required for external template tests")
def test_external_cookiecutter_trust_gate_and_vendoring(tmp_path: Path) -> None:
    repo_root = _render_monorepo(tmp_path, repo_slug="demo-4")
    upstream_dir, upstream_rev, upstream_uri = _create_upstream_cookiecutter_repo(tmp_path)

    registry_path = repo_root / "tools" / "scaffold" / "registry.toml"
    registry_path.write_text(
        registry_path.read_text(encoding="utf-8")
        + "\n"
        + "\n"
        + "[generators.external_local]\n"
        + 'type = "cookiecutter"\n'
        + f'source = "{upstream_uri}"\n'
        + f'ref = "{upstream_rev}"\n'
        + "trusted = false\n"
        + 'name_var = "project_slug"\n'
        + 'context_defaults = { package_name = "{name_snake}" }\n'
        + 'toolchain = "python"\n'
        + 'package_manager = "none"\n'
        + 'tasks.lint = ["python", "-m", "compileall", "src"]\n'
        + 'tasks.test = ["python", "-m", "unittest", "discover", "-s", "tests"]\n',
        encoding="utf-8",
    )

    cp = _run_scaffold(repo_root, "add", "app", "extproj", "--generator", "external_local")
    assert cp.returncode != 0
    assert "--trust" in (cp.stderr + cp.stdout)

    cp = _run_scaffold(repo_root, "add", "app", "extproj", "--generator", "external_local", "--trust")
    assert cp.returncode == 0, cp.stderr
    assert (repo_root / "apps" / "extproj").exists()

    # Vendoring should import the template, write UPSTREAM.toml, and append a new generator.
    cp = _run_scaffold(repo_root, "vendor", "import", "external_local", "--as", "vendored_local")
    assert cp.returncode == 0, cp.stderr

    vendored_dir = repo_root / "tools" / "templates" / "vendor" / "vendored_local"
    assert vendored_dir.exists()
    assert (vendored_dir / "UPSTREAM.toml").exists()
    assert (vendored_dir / "LICENSE").exists()

    cp = _run_scaffold(repo_root, "add", "app", "vendoredproj", "--generator", "vendored_local")
    assert cp.returncode == 0, cp.stderr
    assert (repo_root / "apps" / "vendoredproj").exists()

    # Vendor update should stage temp dirs (manual merge flow).
    # Make a new upstream commit to diff against.
    (upstream_dir / "{{cookiecutter.project_slug}}" / "README.md").write_text("# updated\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=str(upstream_dir), check=True)
    subprocess.run(["git", "commit", "-m", "update"], cwd=str(upstream_dir), check=True, capture_output=True)
    new_rev = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(upstream_dir),
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()

    cp = _run_scaffold(repo_root, "vendor", "update", "vendored_local", "--ref", new_rev)
    assert cp.returncode == 0, cp.stderr
    assert (repo_root / "tools" / "templates" / "vendor" / "vendored_local.__current_tmp__").exists()
    assert (repo_root / "tools" / "templates" / "vendor" / "vendored_local.__upstream_tmp__").exists()

    # Clean up staged dirs so rerunning tests is safe.
    shutil.rmtree(repo_root / "tools" / "templates" / "vendor" / "vendored_local.__current_tmp__")
    shutil.rmtree(repo_root / "tools" / "templates" / "vendor" / "vendored_local.__upstream_tmp__")
