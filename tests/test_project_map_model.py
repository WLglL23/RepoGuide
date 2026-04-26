from repoguide.core.models.project_map import ProjectMap


def test_project_map_to_dict_compatible_with_v0_formatter():
    project_map = ProjectMap(
        root_path=".",
        project_type="python-project",
        file_count=1,
        important_files=["main.py"],
        entrypoint_candidates=["main.py"],
        config_candidates=[],
        build_files=[],
        test_files=[],
        possible_run_commands=["python main.py"],
        top_level_tree="RepoGuide/\n  main.py",
    )

    data = project_map.to_dict()

    assert data["entrypoint_candidates"] == ["main.py"]
    assert data["config_candidates"] == []
    assert data["possible_run_commands"] == ["python main.py"]
    assert data["top_level_tree"].startswith("RepoGuide/")