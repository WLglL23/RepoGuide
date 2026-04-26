"""
RepoSnapshot 数据模型。

RepoSnapshot 表示一次仓库扫描得到的结构化快照。
它是 v1 Core SDK 的核心聚合对象，用于逐步替代 v0 的散装 dict 数据流。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from repoguide.core.models.repo_file import RepoFile


@dataclass
class RepoSnapshot:
    """
    仓库的一次完整快照。

    当前 v1 阶段只保存静态扫描结果，不做 AST 解析、不做索引持久化、不做 LLM 问答。
    """

    repo_id: str
    root_path: str
    project_name: str
    project_type: str
    files: List[RepoFile]
    file_count: int
    created_at: str

    entrypoints: List[str] = field(default_factory=list)
    config_files: List[str] = field(default_factory=list)
    build_files: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    important_files: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """补全派生字段，并保证输出稳定。"""
        if self.file_count != len(self.files):
            self.file_count = len(self.files)

        if not self.entrypoints:
            self.entrypoints = [
                f.path for f in self.files
                if f.role == "entrypoint_candidate"
            ]

        if not self.config_files:
            self.config_files = [
                f.path for f in self.files
                if f.role == "config"
            ]

        if not self.build_files:
            self.build_files = [
                f.path for f in self.files
                if f.role == "build_manifest"
            ]

        if not self.test_files:
            self.test_files = [
                f.path for f in self.files
                if f.role == "test"
            ]

        if not self.important_files:
            important_roles = {
                "readme",
                "config",
                "infra",
                "build_manifest",
                "entrypoint_candidate",
            }
            self.important_files = [
                f.path for f in self.files
                if f.role in important_roles
            ]

        self.entrypoints = sorted(set(self.entrypoints))
        self.config_files = sorted(set(self.config_files))
        self.build_files = sorted(set(self.build_files))
        self.test_files = sorted(set(self.test_files))
        self.important_files = sorted(set(self.important_files))

    def to_dict(self) -> Dict[str, Any]:
        """转换为 dict，方便兼容旧 mapper / formatter。"""
        return {
            "repo_id": self.repo_id,
            "root_path": self.root_path,
            "project_name": self.project_name,
            "project_type": self.project_type,
            "files": [f.to_dict() for f in self.files],
            "file_count": self.file_count,
            "created_at": self.created_at,
            "entrypoints": self.entrypoints,
            "config_files": self.config_files,
            "build_files": self.build_files,
            "test_files": self.test_files,
            "important_files": self.important_files,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepoSnapshot":
        """
        从字典反序列化 RepoSnapshot。

        用于从本地索引文件（如 repo_snapshot.json）读取快照。
        """
        files = [RepoFile.from_dict(f) for f in data["files"]]
        return cls(
            repo_id=data["repo_id"],
            root_path=data["root_path"],
            project_name=data["project_name"],
            project_type=data["project_type"],
            files=files,
            file_count=data.get("file_count", len(files)),
            created_at=data["created_at"],
            entrypoints=data.get("entrypoints", []),
            config_files=data.get("config_files", []),
            build_files=data.get("build_files", []),
            test_files=data.get("test_files", []),
            important_files=data.get("important_files", []),
        )

    def files_as_dicts(self) -> List[Dict[str, Any]]:
        """返回文件 dict 列表，方便旧 mapper 使用。"""
        return [f.to_dict() for f in self.files]