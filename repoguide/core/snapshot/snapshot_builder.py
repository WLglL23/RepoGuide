"""
SnapshotBuilder - 快照构建器（配置传递版）

将扫描、分类、语言检测串联成 RepoSnapshot，
并允许通过 RepoGuideConfig 自定义扫描行为与项目名称。
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from repoguide.core.classifier.file_classifier import classify_files, identify_project_type
from repoguide.core.models.repo_file import RepoFile
from repoguide.core.models.repo_snapshot import RepoSnapshot
from repoguide.core.scanner.repo_scanner import scan_repo
from repoguide.config.config_model import RepoGuideConfig


class SnapshotBuilder:
    """快照构建器，封装扫描 -> 分类 -> 建模流程。"""

    @staticmethod
    def build(
        root_path: str,
        config: Optional[RepoGuideConfig] = None,
    ) -> RepoSnapshot:
        """
        从本地路径构建 RepoSnapshot。

        Args:
            root_path: 项目根目录路径。
            config: RepoGuide 配置对象，为 None 时使用内置默认值。
        """
        resolved_root = Path(root_path).expanduser().resolve()
        if not resolved_root.exists():
            raise FileNotFoundError(f"路径不存在：{root_path}")

        # 提取配置中的扫描参数
        ignore_dirs = config.scan.ignore_dirs if config else None
        include_hidden = config.scan.include_hidden_templates if config else None

        # 扫描文件系统
        raw_files = scan_repo(
            str(resolved_root),
            ignore_dirs=ignore_dirs,
            include_hidden_templates=include_hidden,
        )

        # 分类
        classified_files = classify_files(raw_files)

        # 转 RepoFile
        repo_files: List[RepoFile] = [
            RepoFile.from_dict(item) for item in classified_files
        ]

        # 项目类型识别
        project_type = identify_project_type(classified_files, str(resolved_root))

        # 项目名称：配置优先，否则用目录名
        project_name = resolved_root.name
        if config and config.project.name:
            project_name = config.project.name

        return RepoSnapshot(
            repo_id=f"local:{resolved_root}",
            root_path=str(resolved_root),
            project_name=project_name,
            project_type=project_type,
            files=repo_files,
            file_count=len(repo_files),
            created_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )