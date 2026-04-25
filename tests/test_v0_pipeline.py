from repoguide.core.scanner.repo_scanner import scan_repo
from repoguide.core.classifier.file_classifier import classify_files, identify_project_type
from repoguide.core.mapper.project_mapper import generate_project_map
from repoguide.core.mapper.project_map_formatter import format_project_map


def test_v0_pipeline_on_current_repo():
    root = "."

    files = scan_repo(root)
    classified_files = classify_files(files)
    project_type = identify_project_type(classified_files, root)

    project_map = generate_project_map(
        files=classified_files,
        root_path=root,
        project_type=project_type,
    )

    output = format_project_map(project_map)

    assert "RepoGuide v0 Project Map" in output
    assert "Project Root:" in output
    assert "Detected Project Type:" in output
    assert "File Count:" in output
    assert project_map["file_count"] > 0