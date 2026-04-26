"""
CLI 测试。

当前只测试 v2.1 的基础命令：
- version
- map
- init

测试目标不是验证输出样式，而是确认命令可以正常执行。
"""

from pathlib import Path

from typer.testing import CliRunner

from repoguide.cli.app import app


runner = CliRunner()


def test_cli_version():
    """repoguide version 应该正常输出版本号。"""
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "RepoGuide" in result.output


def test_cli_map_current_repo():
    """repoguide map . 应该能输出项目地图。"""
    result = runner.invoke(app, ["map", "."])

    assert result.exit_code == 0
    assert "RepoGuide v0 Project Map" in result.output
    assert "Project Root:" in result.output
    assert "Detected Project Type:" in result.output


def test_cli_init_creates_repoguide_dir(tmp_path: Path):
    """repoguide init <path> 应该创建 .repoguide 目录结构。"""
    result = runner.invoke(app, ["init", str(tmp_path)])

    assert result.exit_code == 0

    base_dir = tmp_path / ".repoguide"
    assert base_dir.exists()
    assert (base_dir / "config.yml").exists()
    assert (base_dir / "indexes").exists()
    assert (base_dir / "cache").exists()
    assert (base_dir / "overlays").exists()
    assert (base_dir / "traces").exists()
    assert (base_dir / "patches").exists()
    assert (base_dir / "logs").exists()


def test_cli_init_existing_dir_does_not_fail(tmp_path: Path):
    """重复执行 init 不应该失败。"""
    first = runner.invoke(app, ["init", str(tmp_path)])
    second = runner.invoke(app, ["init", str(tmp_path)])

    assert first.exit_code == 0
    assert second.exit_code == 0
    assert "Skipped existing config" in second.output