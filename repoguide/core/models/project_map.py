"""
ProjectMap 数据模型。

ProjectMap 是仓库快照经过映射、聚合后得到的高层结构化视图。
v1 阶段需要兼容 v0 formatter，因此字段命名暂时保留 v0 输出结构。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ProjectMap:
    """仓库结构化映射结果。"""

    root_path: str
    project_type: str
    file_count: int

    important_files: List[str]
    entrypoint_candidates: List[str]
    config_candidates: List[str]
    build_files: List[str]
    test_files: List[str]
    possible_run_commands: List[str]
    top_level_tree: str

    repo_id: str = ""
    project_name: str = ""
    generated_at: str = ""

    language_breakdown: Dict[str, int] = field(default_factory=dict)
    role_summary: Dict[str, int] = field(default_factory=dict)
    top_languages: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为 dict，兼容 v0 formatter。"""
        return {
            "repo_id": self.repo_id,
            "root_path": self.root_path,
            "project_name": self.project_name,
            "project_type": self.project_type,
            "generated_at": self.generated_at,
            "file_count": self.file_count,

            "important_files": self.important_files,
            "entrypoint_candidates": self.entrypoint_candidates,
            "config_candidates": self.config_candidates,
            "build_files": self.build_files,
            "test_files": self.test_files,
            "possible_run_commands": self.possible_run_commands,
            "top_level_tree": self.top_level_tree,

            "language_breakdown": self.language_breakdown,
            "role_summary": self.role_summary,
            "top_languages": self.top_languages,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectMap":
        """从字典反序列化 ProjectMap（用于读取本地索引）。"""
        return cls(
            repo_id=data.get("repo_id", ""),
            root_path=data["root_path"],
            project_name=data.get("project_name", ""),
            project_type=data["project_type"],
            generated_at=data.get("generated_at", ""),
            file_count=data["file_count"],
            important_files=data.get("important_files", []),
            entrypoint_candidates=data.get("entrypoint_candidates", []),
            config_candidates=data.get("config_candidates", []),
            build_files=data.get("build_files", []),
            test_files=data.get("test_files", []),
            possible_run_commands=data.get("possible_run_commands", []),
            top_level_tree=data.get("top_level_tree", ""),
            language_breakdown=data.get("language_breakdown", {}),
            role_summary=data.get("role_summary", {}),
            top_languages=data.get("top_languages", []),
            metadata=data.get("metadata", {}),
        )