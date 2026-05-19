from datetime import datetime, timezone
from pathlib import Path

from repoguide.core.mapper.project_mapper import generate_project_map_from_snapshot
from repoguide.core.models.project_map import ProjectMap
from repoguide.core.models.repo_index import RepoIndex
from repoguide.core.models.repo_snapshot import RepoSnapshot
from repoguide.core.parser import PythonParser


class RepoIndexBuilder:
    @staticmethod
    def build(
        snapshot: RepoSnapshot,
        project_map: ProjectMap | None = None,
    ) -> RepoIndex:
        if project_map is None:
            project_map = generate_project_map_from_snapshot(snapshot)

        symbols = []
        api_endpoints = []

        for repo_file in snapshot.files:
            if repo_file.language != "python":
                continue
            file_path = Path(snapshot.root_path) / repo_file.path
            result = PythonParser.parse_file(
                str(file_path),
                relative_path=repo_file.path,
            )
            symbols.extend(result.symbols)
            api_endpoints.extend(result.api_endpoints)

        return RepoIndex(
            repo_id=snapshot.repo_id,
            root_path=snapshot.root_path,
            project_name=snapshot.project_name,
            project_type=snapshot.project_type,
            created_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            snapshot=snapshot.to_dict(),
            project_map=project_map.to_dict(),
            symbols=symbols,
            api_endpoints=api_endpoints,
        )
