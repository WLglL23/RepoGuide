"""
SnapshotBuilder - 将扫描、分类、语言检测串联成 RepoSnapshot。

职责：
1. 调用 Scanner 获取原始文件信息
2. 调用 Classifier 为每个文件打 role
3. 将 dict 转为 RepoFile
4. 复用现有项目类型识别逻辑
5. 构造 RepoSnapshot
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from repoguide.core.classifier.file_classifier import classify_files, identify_project_type
from repoguide.core.models.repo_file import RepoFile
from repoguide.core.models.repo_snapshot import RepoSnapshot
from repoguide.core.scanner.repo_scanner import scan_repo


class SnapshotBuilder:
    """
    快照构建器，封装扫描 -> 分类 -> 建模流程。

    设计原则：
    - 不重复实现项目类型识别，直接复用 classifier 模块的 identify_project_type()，
      确保 v1 输出的 project_type 与 v0 一致。
    - 所有组件（Scanner, Classifier, LanguageDetector）均通过已有模块调用，
      构建器只负责编排。
    - 入口方法 build() 力求简单，外部只需提供根路径即可获得完整快照。
    """

    @staticmethod
    def build(
        root_path: str,
        repo_id: Optional[str] = None,
        project_name: Optional[str] = None,
    ) -> RepoSnapshot:
        """
        从本地路径构建 RepoSnapshot。

        Args:
            root_path: 本地项目的绝对或相对路径。
            repo_id: 仓库唯一标识，默认使用 "local:<绝对路径>"。
            project_name: 项目名称，默认使用根目录名。

        Returns:
            完全填充的 RepoSnapshot 对象。

        Raises:
            FileNotFoundError: 如果 root_path 不存在。
        """
        # 路径规范化
        resolved_root = Path(root_path).expanduser().resolve()

        if not resolved_root.exists():
            raise FileNotFoundError(f"路径不存在：{root_path}")

        # 设置默认标识
        if repo_id is None:
            repo_id = f"local:{resolved_root}"

        if project_name is None:
            project_name = resolved_root.name

        # 1. 扫描文件系统
        raw_files = scan_repo(str(resolved_root))

        # 2. 分类（添加 role 字段）
        classified_files = classify_files(raw_files)

        # 3. 将 dict 转为 RepoFile（自动触发语言推断）
        repo_files = [
            RepoFile.from_dict(item)
            for item in classified_files
        ]

        # 4. 识别项目类型（复用现有逻辑）
        project_type = identify_project_type(
            classified_files,
            str(resolved_root),
        )

        # 5. 构建快照（便捷列表由 RepoSnapshot.__post_init__ 自动处理）
        return RepoSnapshot(
            repo_id=repo_id,
            root_path=str(resolved_root),
            project_name=project_name,
            project_type=project_type,
            files=repo_files,
            file_count=len(repo_files),
            created_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )