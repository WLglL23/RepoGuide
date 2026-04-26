"""
RepoGuide v2.2 索引能力测试。

测试目标：
1. RepoGuide.index() 能生成并保存本地索引。
2. RepoGuide.map() 能读取已有 project_map.json。
3. RepoGuide.map(refresh=True) 能强制刷新索引。
"""

from pathlib import Path

from repoguide import RepoGuide
from repoguide.core.models.project_map import ProjectMap


def test_repoguide_index_creates_local_index(tmp_path: Path):
    """
    RepoGuide.index(path) 应该创建 .repoguide/indexes 下的两个 JSON 文件。
    """
    # 构造一个最小 Python 项目
    (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Demo", encoding="utf-8")

    project_map = RepoGuide.index(str(tmp_path))

    assert isinstance(project_map, ProjectMap)
    assert project_map.file_count >= 2

    index_dir = tmp_path / ".repoguide" / "indexes"
    assert (index_dir / "repo_snapshot.json").exists()
    assert (index_dir / "project_map.json").exists()


def test_repoguide_map_loads_existing_index(tmp_path: Path):
    """
    RepoGuide.map(path) 在索引存在时应该能读取 project_map.json。
    """
    (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Demo", encoding="utf-8")

    indexed_map = RepoGuide.index(str(tmp_path))
    loaded_map = RepoGuide.map(str(tmp_path))

    assert isinstance(loaded_map, ProjectMap)
    assert loaded_map.root_path == indexed_map.root_path
    assert loaded_map.file_count == indexed_map.file_count
    assert loaded_map.project_type == indexed_map.project_type


def test_repoguide_map_refresh_rebuilds_index(tmp_path: Path):
    """
    RepoGuide.map(path, refresh=True) 应该重新扫描并更新索引。
    """
    (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")

    first_map = RepoGuide.index(str(tmp_path))

    # 新增文件后，如果 refresh=True，新的 ProjectMap 应该包含更多文件
    (tmp_path / "README.md").write_text("# Demo", encoding="utf-8")

    refreshed_map = RepoGuide.map(str(tmp_path), refresh=True)

    assert refreshed_map.file_count >= first_map.file_count
    assert "README.md" in refreshed_map.important_files


def test_repoguide_map_without_index_falls_back_to_scan(tmp_path: Path):
    """
    没有本地索引时，RepoGuide.map(path) 应该临时扫描并返回 ProjectMap。
    但不应该主动创建 .repoguide/indexes。
    """
    (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")

    project_map = RepoGuide.map(str(tmp_path))

    assert isinstance(project_map, ProjectMap)
    assert project_map.file_count >= 1

    # 普通 map 不负责保存索引
    assert not (tmp_path / ".repoguide" / "indexes" / "project_map.json").exists()