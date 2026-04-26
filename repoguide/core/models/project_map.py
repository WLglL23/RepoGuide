"""
ProjectMap 数据模型。

ProjectMap 是仓库快照经过映射、聚合后得到的高层结构化视图。
v1 阶段需要兼容 v0 formatter，因此字段命名暂时保留 v0 输出结构。
同时增加了 v1 新增的统计字段（language_breakdown 等），为后续升级做准备。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ProjectMap:
    """
    仓库结构化映射结果。

    字段说明：
    - root_path, project_type, file_count：基础信息。
    - important_files：高价值文件（readme、配置、入口等）。
    - entrypoint_candidates：入口候选列表，v0 格式字段名。
    - config_candidates：配置文件候选列表，v0 格式字段名。
    - build_files：构建文件列表。
    - test_files：测试文件列表。
    - possible_run_commands：可能的运行/测试命令。
    - top_level_tree：一级目录树的文本表示。
    - repo_id, project_name, generated_at：v1 新增的标识与时间信息。
    - language_breakdown：语言分布统计（v1 新增）。
    - role_summary：角色分布统计（v1 新增）。
    - top_languages：按文件数降序的前几大语言（v1 新增）。
    - metadata：扩展元数据。
    """

    # 核心必需字段（v0 和 v1 共享）
    root_path: str
    project_type: str
    file_count: int

    # v0 输出字段（命名保持与现有 formatter 一致）
    important_files: List[str]
    entrypoint_candidates: List[str]
    config_candidates: List[str]
    build_files: List[str]
    test_files: List[str]
    possible_run_commands: List[str]
    top_level_tree: str

    # v1 新增字段（带默认值，兼容未提供时）
    repo_id: str = ""
    project_name: str = ""
    generated_at: str = ""

    # v1 统计字段
    language_breakdown: Dict[str, int] = field(default_factory=dict)
    role_summary: Dict[str, int] = field(default_factory=dict)
    top_languages: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典，完全兼容 v0 formatter 所需的字段名。

        Returns:
            包含所有字段的字典，键名与 v0 项目地图一致。
        """
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