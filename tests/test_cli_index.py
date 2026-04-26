"""
CLI v2.2 索引命令测试。

覆盖：
- repoguide index <path>
- repoguide map <path>
- repoguide map <path> --refresh
"""

from pathlib import Path

from typer.testing import CliRunner

from repoguide.cli.app import app


runner = CliRunner()


def make_sample_project(root: Path) -> None:
    """构造一个最小 Python 项目。"""
    (root / "main.py").write_text("print('hello')", encoding="utf-8")
    (root / "README.md").write_text("# Demo", encoding="utf-8")


def test_cli_index_creates_local_index(tmp_path: Path):
    """repoguide index <path> 应该创建本地索引文件。"""
    make_sample_project(tmp_path)

    result = runner.invoke(app, ["index", str(tmp_path)])

    assert result.exit_code == 0
    assert "Index completed" in result.output

    index_dir = tmp_path / ".repoguide" / "indexes"
    assert (index_dir / "repo_snapshot.json").exists()
    assert (index_dir / "project_map.json").exists()


def test_cli_map_uses_cached_index_after_index(tmp_path: Path):
    """先 index 再 map，map 应该使用缓存索引。"""
    make_sample_project(tmp_path)

    index_result = runner.invoke(app, ["index", str(tmp_path)])
    map_result = runner.invoke(app, ["map", str(tmp_path)])

    assert index_result.exit_code == 0
    assert map_result.exit_code == 0
    assert "Using cached index" in map_result.output
    assert "RepoGuide v0 Project Map" in map_result.output


def test_cli_map_without_index_uses_temporary_scan(tmp_path: Path):
    """没有索引时，map 应该临时扫描并提示用户 index。"""
    make_sample_project(tmp_path)

    result = runner.invoke(app, ["map", str(tmp_path)])

    assert result.exit_code == 0
    assert "No cached index found" in result.output
    assert "RepoGuide v0 Project Map" in result.output

    # 普通 map 不应主动写入索引
    assert not (tmp_path / ".repoguide" / "indexes" / "project_map.json").exists()


def test_cli_map_refresh_updates_index(tmp_path: Path):
    """map --refresh 应该强制扫描并写入索引。"""
    make_sample_project(tmp_path)

    result = runner.invoke(app, ["map", str(tmp_path), "--refresh"])

    assert result.exit_code == 0
    assert "Index refreshed" in result.output

    index_dir = tmp_path / ".repoguide" / "indexes"
    assert (index_dir / "repo_snapshot.json").exists()
    assert (index_dir / "project_map.json").exists()