from repoguide.core.mapper.project_mapper import ProjectMapper
from repoguide.core.models.project_map import ProjectMap
from repoguide.core.snapshot.snapshot_builder import SnapshotBuilder


def test_generate_project_map_from_snapshot():
    snapshot = SnapshotBuilder.build(".")

    project_map = ProjectMapper.generate_project_map_from_snapshot(snapshot)

    assert isinstance(project_map, ProjectMap)
    assert project_map.file_count == snapshot.file_count
    assert project_map.root_path == snapshot.root_path
    assert project_map.project_type == snapshot.project_type
    assert isinstance(project_map.language_breakdown, dict)
    assert isinstance(project_map.role_summary, dict)


def test_project_map_from_snapshot_can_format():
    from repoguide.core.mapper.project_map_formatter import format_project_map

    snapshot = SnapshotBuilder.build(".")
    project_map = ProjectMapper.generate_project_map_from_snapshot(snapshot)

    output = format_project_map(project_map.to_dict())

    assert "RepoGuide v0 Project Map" in output
    assert "Project Root:" in output
    assert "Detected Project Type:" in output