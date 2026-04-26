"""
ConfigLoader 测试。

覆盖：
1. 没有 config.yml 时使用默认配置。
2. 用户配置可以覆盖默认配置。
3. 深度合并不会丢失默认嵌套字段。
4. CLI init 后写出的配置能被读取。
"""

from pathlib import Path

from repoguide.config.config_loader import ConfigLoader


def test_config_loader_uses_default_when_missing(tmp_path: Path):
    """没有 .repoguide/config.yml 时，应该返回默认配置。"""
    config = ConfigLoader.load(tmp_path)

    assert config.version == 1
    assert ".git" in config.scan.ignore_dirs
    assert ".env.example" in config.scan.include_hidden_templates
    assert "pytest" in config.test.allowed_commands


def test_config_loader_reads_user_config(tmp_path: Path):
    """存在 config.yml 时，应该读取用户配置。"""
    config_dir = tmp_path / ".repoguide"
    config_dir.mkdir()

    (config_dir / "config.yml").write_text(
        """
version: 1

project:
  name: demo-project

scan:
  ignore_dirs:
    - custom_ignore

test:
  allowed_commands:
    - pytest -q
""",
        encoding="utf-8",
    )

    config = ConfigLoader.load(tmp_path)

    assert config.project.name == "demo-project"
    assert config.scan.ignore_dirs == ["custom_ignore"]
    assert config.test.allowed_commands == ["pytest -q"]


def test_config_loader_deep_merge_keeps_default_nested_fields(tmp_path: Path):
    """
    用户只覆盖 scan.ignore_dirs 时，
    默认 scan.include_hidden_templates 不应该丢失。
    """
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

    config = ConfigLoader.load(tmp_path)

    assert config.scan.ignore_dirs == ["custom_ignore"]
    assert ".env.example" in config.scan.include_hidden_templates


def test_create_default_config(tmp_path: Path):
    """create_default_config 应该创建 .repoguide/config.yml。"""
    config_path = ConfigLoader.create_default_config(tmp_path)

    assert config_path.exists()
    assert config_path.name == "config.yml"

    config = ConfigLoader.load(tmp_path)

    assert ".git" in config.scan.ignore_dirs
    assert "pytest" in config.test.allowed_commands


def test_create_default_config_force_overwrites(tmp_path: Path):
    """force=True 时应该覆盖已有 config.yml。"""
    config_path = ConfigLoader.create_default_config(tmp_path)

    config_path.write_text(
        """
version: 1
project:
  name: custom
""",
        encoding="utf-8",
    )

    ConfigLoader.create_default_config(tmp_path, force=True)

    config = ConfigLoader.load(tmp_path)

    assert config.project.name is None
    assert ".git" in config.scan.ignore_dirs