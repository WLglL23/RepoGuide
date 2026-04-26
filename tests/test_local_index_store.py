"""
LocalIndexStore 测试。

当前测试 v2.2 的本地索引持久化能力：
1. 能保存并读取 RepoSnapshot
2. 能保存并读取 ProjectMap
3. 能判断索引是否存在
4. 索引文件不存在时返回 None
"""

from pathlib import Path

from repoguide.core.mapper.project_mapper import ProjectMapper
from repoguide.core.snapshot.snapshot_builder import SnapshotBuilder
from repoguide.storage.local_index_store import LocalIndexStore


def test_store_returns_none_when_index_missing(tmp_path: Path):
    """没有索引文件时，load_* 应该返回 None。"""
    store = LocalIndexStore(tmp_path)

    assert store.load_snapshot() is None
    assert store.load_project_map() is None
    assert store.has_snapshot() is False
    assert store.has_project_map() is False
    assert store.has_index() is False


def test_store_save_and_load_snapshot():
    """保存 RepoSnapshot 后应该可以正常读回。"""
    snapshot = SnapshotBuilder.build(".")
    store = LocalIndexStore(snapshot.root_path)

    store.save_snapshot(snapshot)

    loaded = store.load_snapshot()

    assert loaded is not None
    assert loaded.root_path == snapshot.root_path
    assert loaded.project_type == snapshot.project_type
    assert loaded.file_count == snapshot.file_count
    assert len(loaded.files) == len(snapshot.files)


def test_store_save_and_load_project_map():
    """保存 ProjectMap 后应该可以正常读回。"""
    snapshot = SnapshotBuilder.build(".")
    project_map = ProjectMapper.generate_project_map_from_snapshot(snapshot)

    store = LocalIndexStore(snapshot.root_path)
    store.save_project_map(project_map)

    loaded = store.load_project_map()

    assert loaded is not None
    assert loaded.root_path == project_map.root_path
    assert loaded.project_type == project_map.project_type
    assert loaded.file_count == project_map.file_count
    assert loaded.important_files == project_map.important_files


def test_store_has_index_after_saving_both_files():
    """同时保存 Snapshot 和 ProjectMap 后，has_index() 应该为 True。"""
    snapshot = SnapshotBuilder.build(".")
    project_map = ProjectMapper.generate_project_map_from_snapshot(snapshot)

    store = LocalIndexStore(snapshot.root_path)
    store.save_snapshot(snapshot)
    store.save_project_map(project_map)

    assert store.has_snapshot() is True
    assert store.has_project_map() is True
    assert store.has_index() is True


def test_store_creates_index_dir(tmp_path: Path):
    """保存文件时应该自动创建 .repoguide/indexes 目录。"""
    snapshot = SnapshotBuilder.build(".")
    project_map = ProjectMapper.generate_project_map_from_snapshot(snapshot)

    store = LocalIndexStore(tmp_path)
    store.save_snapshot(snapshot)
    store.save_project_map(project_map)

    assert (tmp_path / ".repoguide" / "indexes").exists()
    assert (tmp_path / ".repoguide" / "indexes" / "repo_snapshot.json").exists()
    assert (tmp_path / ".repoguide" / "indexes" / "project_map.json").exists()