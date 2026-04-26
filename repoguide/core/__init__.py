"""
RepoGuide v1 Core SDK

该模块导出 Core SDK 的主要公共对象。

当前 v1 阶段的核心目标是：

1. 将 v0 中散落的 dict 数据流逐步收敛为稳定数据模型。
2. 提供统一的 RepoGuide Core Facade。
3. 为后续正式 CLI、索引、接口解析、诊断和 API 服务化打基础。

主要公共对象：

- RepoGuide:
    Core SDK 统一入口，目前提供 map() 方法。

- RepoFile:
    单个仓库文件的数据模型。

- RepoSnapshot:
    一次仓库扫描得到的结构化快照。

- ProjectMap:
    从 RepoSnapshot 聚合得到的项目地图。

- SnapshotBuilder:
    负责扫描、分类并构造 RepoSnapshot。

- ProjectMapper:
    负责从 RepoSnapshot 生成 ProjectMap。

- LanguageDetector:
    基于扩展名的语言检测器。
"""

from repoguide.core.language.language_detector import LanguageDetector
from repoguide.core.mapper.project_mapper import (
    ProjectMapper,
    generate_project_map_from_snapshot,
)
from repoguide.core.models.project_map import ProjectMap
from repoguide.core.models.repo_file import RepoFile
from repoguide.core.models.repo_snapshot import RepoSnapshot
from repoguide.core.repoguide import RepoGuide
from repoguide.core.snapshot.snapshot_builder import SnapshotBuilder

__all__ = [
    "RepoGuide",
    "RepoFile",
    "RepoSnapshot",
    "ProjectMap",
    "SnapshotBuilder",
    "ProjectMapper",
    "LanguageDetector",
    "generate_project_map_from_snapshot",
]