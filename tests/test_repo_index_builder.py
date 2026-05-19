from pathlib import Path

from repoguide.core.indexer import RepoIndexBuilder
from repoguide.core.mapper.project_mapper import generate_project_map_from_snapshot
from repoguide.core.snapshot.snapshot_builder import SnapshotBuilder


def test_repo_index_builder_collects_python_symbols_and_api_endpoints(
    tmp_path: Path,
):
    source_file = tmp_path / "api.py"
    source_file.write_text(
        "\n".join(
            [
                "from fastapi import FastAPI",
                "",
                "app = FastAPI()",
                "",
                '@app.get("/users")',
                "def list_users():",
                "    return []",
            ]
        ),
        encoding="utf-8",
    )

    snapshot = SnapshotBuilder.build(str(tmp_path))
    project_map = generate_project_map_from_snapshot(snapshot)

    repo_index = RepoIndexBuilder.build(snapshot, project_map)

    assert repo_index.symbols
    assert repo_index.api_endpoints

    endpoint = repo_index.api_endpoints[0]
    assert endpoint.method == "GET"
    assert endpoint.path == "/users"
    assert endpoint.handler == "list_users"
    assert endpoint.file_path == "api.py"
