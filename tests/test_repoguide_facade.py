"""
RepoGuide Core Facade 测试。

目标：
1. 确认 RepoGuide.map() 可以返回 ProjectMap。
2. 确认 ProjectMap 可以兼容旧 formatter。
3. 确认 from repoguide import RepoGuide 可用。
"""

from repoguide import RepoGuide
from repoguide.core.mapper.project_map_formatter import format_project_map
from repoguide.core.models.project_map import ProjectMap


def test_repoguide_map_returns_project_map():
    """RepoGuide.map('.') 应该返回 ProjectMap 对象。"""
    project_map = RepoGuide.map(".")

    assert isinstance(project_map, ProjectMap)
    assert project_map.file_count > 0
    assert project_map.root_path
    assert project_map.project_type


def test_repoguide_map_can_format_output():
    """RepoGuide.map() 的结果应该可以交给旧 formatter 输出。"""
    project_map = RepoGuide.map(".")
    output = format_project_map(project_map.to_dict())

    assert "RepoGuide v0 Project Map" in output
    assert "Project Root:" in output
    assert "Detected Project Type:" in output
    assert "File Count:" in output


def test_top_level_import_repoguide():
    """确认 from repoguide import RepoGuide 可用。"""
    assert RepoGuide is not None