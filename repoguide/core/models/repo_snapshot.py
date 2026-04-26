"""
RepoSnapshot 数据模型。

RepoSnapshot 表示一次仓库扫描得到的结构化快照。
它是 v1 Core SDK 的核心聚合对象，用于逐步替代 v0 的散装 dict 数据流。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from repoguide.core.models.repo_file import RepoFile


@dataclass
class RepoSnapshot:
    """
    仓库的一次完整快照。

    当前 v1 阶段只保存静态扫描结果，不做 AST 解析、不做索引持久化、不做 LLM 问答。

    设计原则：
    - 兼容 v0：保留 to_dict() 和 files_as_dicts()，使旧的 ProjectMapper 可以继续工作。
    - 单一数据源：便捷文件列表（entrypoints 等）由 role 字段自动填充，无需手动维护。
    - 只做聚合：不包含构建逻辑，构建逻辑交给 SnapshotBuilder。
    """

    # ---- 仓库标识与基础信息 ----
    repo_id: str
    """仓库唯一标识，例如 ``"github.com/owner/repo"`` 或 ``"local:/abs/path"``。"""

    root_path: str
    """仓库在本地文件系统中的根路径（绝对路径）。"""

    project_name: str
    """项目名称，一般取自根目录名或配置文件。"""

    project_type: str
    """项目类型标识，例如 ``"python"``、``"java-maven"``、``"generic"``。
       由 classifier 模块的 identify_project_type() 提供，保证与 v0 一致。"""

    # ---- 文件清单 ----
    files: List[RepoFile]
    """仓库内所有文件的 RepoFile 列表，由扫描器生成并经过分类器、语言检测处理。"""

    file_count: int
    """文件总数。在 __post_init__ 中会自动修正为 len(files)，确保数据一致。"""

    created_at: str
    """快照创建时间，ISO 8601 格式（UTC），例如 ``"2025-03-15T10:30:00Z"``。"""

    # ---- 便捷文件列表 ----
    # 这些列表在构造时可以不提供，__post_init__ 会根据角色自动填充。
    # 如果外部显式提供了值，则尊重外部数据，不再自动填充（此处逻辑已简化，
    # 当前版本只在未提供时自动计算，提供后不再计算，但会去掉重复并排序）。
    entrypoints: List[str] = field(default_factory=list)
    """入口点文件路径列表，如 ``["src/main.py", "app.js"]``。"""

    config_files: List[str] = field(default_factory=list)
    """配置文件路径列表，如 ``["pyproject.toml", ".env"]``。"""

    build_files: List[str] = field(default_factory=list)
    """构建相关文件路径列表，如 ``["Makefile", "build.gradle"]``。"""

    test_files: List[str] = field(default_factory=list)
    """测试文件路径列表，如 ``["tests/test_main.py"]``。"""

    important_files: List[str] = field(default_factory=list)
    """重要文件路径列表，包含入口点、配置、构建清单、readme 等高价值文件。"""

    def __post_init__(self) -> None:
        """
        构造后的自动处理。

        保证：
        1. file_count 与 files 列表长度一致。
        2. 如果便捷列表为空，则根据文件的 role 字段自动填充。
        3. 所有列表去重、排序，保证输出稳定。
        """
        # 保证文件计数准确
        if self.file_count != len(self.files):
            self.file_count = len(self.files)

        # 自动填充 entrypoints（若为空）
        if not self.entrypoints:
            self.entrypoints = [
                f.path for f in self.files
                if f.role == "entrypoint_candidate"
            ]

        # 自动填充 config_files（若为空）
        if not self.config_files:
            self.config_files = [
                f.path for f in self.files
                if f.role == "config"
            ]

        # 自动填充 build_files（若为空）
        if not self.build_files:
            self.build_files = [
                f.path for f in self.files
                if f.role == "build_manifest"
            ]

        # 自动填充 test_files（若为空）
        if not self.test_files:
            self.test_files = [
                f.path for f in self.files
                if f.role == "test"
            ]

        # 自动填充 important_files（若为空）
        # important_files 定义为：入口点、配置、基础设施、构建清单、readme 等角色。
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

        # 去重并排序，保证输出稳定
        self.entrypoints = sorted(set(self.entrypoints))
        self.config_files = sorted(set(self.config_files))
        self.build_files = sorted(set(self.build_files))
        self.test_files = sorted(set(self.test_files))
        self.important_files = sorted(set(self.important_files))

    def to_dict(self) -> Dict[str, Any]:
        """
        将整个快照转换为字典，便于序列化或兼容旧接口。

        Returns:
            包含所有字段的大字典，其中 files 字段是 RepoFile.to_dict() 的结果列表。
        """
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

    def files_as_dicts(self) -> List[Dict[str, Any]]:
        """
        返回文件 dict 列表。

        作用：
        让当前 v0 的 ProjectMapper 可以继续复用，不需要一次性重构。
        v0 原本接收 list[dict]，通过此方法可无缝桥接。
        """
        return [f.to_dict() for f in self.files]