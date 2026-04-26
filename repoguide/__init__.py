"""
RepoGuide

面向项目交接和本地开发诊断的代码仓库理解工具。

当前 v1 阶段主要暴露 Core SDK 的统一入口：

    from repoguide import RepoGuide

    project_map = RepoGuide.map(".")
    print(project_map.project_type)

注意：
    当前版本仍处于 v1 Core SDK 雏形阶段。
    已实现：
        - 本地目录扫描
        - 文件角色分类
        - RepoSnapshot
        - ProjectMap
        - RepoGuide.map()

    尚未实现：
        - LLM 问答
        - 接口解析
        - 调用链分析
        - git diff 诊断
        - Patch 生成
        - API Server
        - Web UI
"""

from repoguide.core import (
    LanguageDetector,
    ProjectMap,
    ProjectMapper,
    RepoFile,
    RepoGuide,
    RepoSnapshot,
    SnapshotBuilder,
)

__all__ = [
    "RepoGuide",
    "RepoFile",
    "RepoSnapshot",
    "ProjectMap",
    "SnapshotBuilder",
    "ProjectMapper",
    "LanguageDetector",
]