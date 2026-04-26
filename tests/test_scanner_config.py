from pathlib import Path

from repoguide import RepoGuide
from repoguide.config.config_loader import ConfigLoader


def test_config_ignore_dirs_affects_scan(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")

    ignored_dir = tmp_path / "custom_ignore"
    ignored_dir.mkdir()
    (ignored_dir / "hidden.py").write_text("print('ignored')", encoding="utf-8")

    config_dir = tmp_path / ".repoguide"
    config_dir.mkdir()

    (config_dir / "config.yml").write_text(
        """
scan:
  ignore_dirs:
    - custom_ignore
""",
        encoding="utf-8",
    )

    snapshot = RepoGuide.build_snapshot(str(tmp_path))
    paths = {file.path for file in snapshot.files}

    assert "main.py" in paths
    assert "custom_ignore/hidden.py" not in paths


def test_config_include_hidden_templates_affects_scan(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")
    (tmp_path / ".env.demo").write_text("KEY=value", encoding="utf-8")

    config_dir = tmp_path / ".repoguide"
    config_dir.mkdir()

    (config_dir / "config.yml").write_text(
        """
scan:
  include_hidden_templates:
    - .env.demo
""",
        encoding="utf-8",
    )

    snapshot = RepoGuide.build_snapshot(str(tmp_path))
    paths = {file.path for file in snapshot.files}

    assert "main.py" in paths
    assert ".env.demo" in paths


def test_config_project_name_affects_snapshot(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")

    config_dir = tmp_path / ".repoguide"
    config_dir.mkdir()

    (config_dir / "config.yml").write_text(
        """
project:
  name: custom-project-name
""",
        encoding="utf-8",
    )

    snapshot = RepoGuide.build_snapshot(str(tmp_path))

    assert snapshot.project_name == "custom-project-name"