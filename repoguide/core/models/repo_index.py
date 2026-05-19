from dataclasses import dataclass, field
from typing import Any, Dict, List

from repoguide.core.models.api_endpoint import ApiEndpoint
from repoguide.core.models.code_symbol import CodeSymbol


@dataclass
class RepoIndex:
    """Aggregated repository index for the v3 parsing layer."""

    repo_id: str
    root_path: str
    project_name: str
    project_type: str
    created_at: str
    snapshot: Dict[str, Any]
    project_map: Dict[str, Any]
    symbols: List[CodeSymbol] = field(default_factory=list)
    api_endpoints: List[ApiEndpoint] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repo_id": self.repo_id,
            "root_path": self.root_path,
            "project_name": self.project_name,
            "project_type": self.project_type,
            "created_at": self.created_at,
            "snapshot": self.snapshot,
            "project_map": self.project_map,
            "symbols": [symbol.to_dict() for symbol in self.symbols],
            "api_endpoints": [
                endpoint.to_dict() for endpoint in self.api_endpoints
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepoIndex":
        return cls(
            repo_id=data["repo_id"],
            root_path=data["root_path"],
            project_name=data["project_name"],
            project_type=data["project_type"],
            created_at=data["created_at"],
            snapshot=data.get("snapshot", {}),
            project_map=data.get("project_map", {}),
            symbols=[
                CodeSymbol.from_dict(item)
                for item in data.get("symbols", [])
            ],
            api_endpoints=[
                ApiEndpoint.from_dict(item)
                for item in data.get("api_endpoints", [])
            ],
        )
