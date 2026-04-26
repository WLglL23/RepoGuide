"""
LocalIndexStore - 本地索引文件读写器。

v2.2 第一版使用 JSON 文件保存 RepoSnapshot 和 ProjectMap。

为什么先用 JSON：
1. 当前还没有复杂符号索引、API 索引、调用图索引。
2. 当前只需要保存一次扫描结果和项目地图。
3. JSON 可读、可调试，适合 v2.2 阶段验证本地索引工作流。
4. 后续进入 RepoIndex 阶段后，再升级为 SQLite / DuckDB 更合适。

索引目录结构：

    <repo_root>/
      .repoguide/
        indexes/
          repo_snapshot.json
          project_map.json

注意：
    LocalIndexStore 只负责 indexes/ 下的索引文件读写。
    它不负责创建完整的 .repoguide/ 目录结构。
    完整目录初始化由 CLI 的 `repoguide init` 命令负责。
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from repoguide.core.models.project_map import ProjectMap
from repoguide.core.models.repo_snapshot import RepoSnapshot


class LocalIndexStore:
    """
    本地 JSON 索引仓库读写器。

    当前负责读写：

    - repo_snapshot.json
    - project_map.json

    设计原则：
    1. 尽量薄，不做扫描、不做分类、不做业务推理。
    2. 只处理路径、目录、JSON 序列化和反序列化。
    3. 如果文件不存在或内容损坏，load_* 返回 None。
    4. 上层决定是否重新 index。
    """

    SNAPSHOT_FILENAME = "repo_snapshot.json"
    PROJECT_MAP_FILENAME = "project_map.json"

    def __init__(self, repo_root: str | Path):
        """
        Args:
            repo_root:
                项目根路径，也就是包含 .repoguide/ 的目录。

                示例：
                    "."
                    "E:/STUDY/My/RepoGuide"
                    "/Users/me/projects/demo"
        """
        self.repo_root = Path(repo_root).expanduser().resolve()
        self.base_dir = self.repo_root / ".repoguide"
        self.index_dir = self.base_dir / "indexes"

    # ------------------------------------------------------------------
    # 路径属性
    # ------------------------------------------------------------------

    @property
    def snapshot_path(self) -> Path:
        """repo_snapshot.json 的完整路径。"""
        return self.index_dir / self.SNAPSHOT_FILENAME

    @property
    def project_map_path(self) -> Path:
        """project_map.json 的完整路径。"""
        return self.index_dir / self.PROJECT_MAP_FILENAME

    # ------------------------------------------------------------------
    # 目录管理
    # ------------------------------------------------------------------

    def ensure_dirs(self) -> None:
        """
        确保索引目录存在。

        这里只创建 .repoguide/indexes/，不创建 cache、traces、logs 等目录。
        完整目录结构仍然由 `repoguide init` 负责。

        这样设计的原因：
        - index 命令可以在用户未手动 init 时自动运行。
        - init 命令仍然是完整初始化入口。
        """
        self.index_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 存在性判断
    # ------------------------------------------------------------------

    def has_snapshot(self) -> bool:
        """判断 repo_snapshot.json 是否存在。"""
        return self.snapshot_path.exists()

    def has_project_map(self) -> bool:
        """判断 project_map.json 是否存在。"""
        return self.project_map_path.exists()

    def has_index(self) -> bool:
        """
        判断本地索引是否基本存在。

        当前标准：
            repo_snapshot.json 和 project_map.json 都存在。
        """
        return self.has_snapshot() and self.has_project_map()

    # ------------------------------------------------------------------
    # Snapshot 读写
    # ------------------------------------------------------------------

    def save_snapshot(self, snapshot: RepoSnapshot) -> None:
        """
        将 RepoSnapshot 序列化为 JSON 并保存。

        Args:
            snapshot:
                SnapshotBuilder.build() 生成的仓库快照。
        """
        self.ensure_dirs()
        self._write_json(self.snapshot_path, snapshot.to_dict())

    def load_snapshot(self) -> Optional[RepoSnapshot]:
        """
        从 repo_snapshot.json 加载 RepoSnapshot。

        Returns:
            RepoSnapshot:
                文件存在且内容合法时返回。

            None:
                文件不存在、JSON 损坏、字段缺失或读文件失败时返回。
        """
        data = self._read_json(self.snapshot_path)

        if data is None:
            return None

        try:
            return RepoSnapshot.from_dict(data)
        except (KeyError, TypeError, ValueError):
            return None

    # ------------------------------------------------------------------
    # ProjectMap 读写
    # ------------------------------------------------------------------

    def save_project_map(self, project_map: ProjectMap) -> None:
        """
        将 ProjectMap 序列化为 JSON 并保存。

        Args:
            project_map:
                ProjectMapper.generate_project_map_from_snapshot() 生成的项目地图。
        """
        self.ensure_dirs()
        self._write_json(self.project_map_path, project_map.to_dict())

    def load_project_map(self) -> Optional[ProjectMap]:
        """
        从 project_map.json 加载 ProjectMap。

        Returns:
            ProjectMap:
                文件存在且内容合法时返回。

            None:
                文件不存在、JSON 损坏、字段缺失或读文件失败时返回。
        """
        data = self._read_json(self.project_map_path)

        if data is None:
            return None

        try:
            return ProjectMap.from_dict(data)
        except (KeyError, TypeError, ValueError):
            return None

    # ------------------------------------------------------------------
    # JSON 工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def _write_json(path: Path, data: Dict[str, Any]) -> None:
        """
        写入 JSON 文件。

        当前第一版直接写目标文件。
        后续如需更强一致性，可以改为：
            1. 写入临时文件
            2. fsync
            3. rename 覆盖目标文件

        Args:
            path:
                目标 JSON 文件路径。

            data:
                可 JSON 序列化的字典。
        """
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @staticmethod
    def _read_json(path: Path) -> Optional[Dict[str, Any]]:
        """
        读取 JSON 文件。

        Returns:
            dict:
                JSON 文件存在且解析成功时返回。

            None:
                文件不存在、JSON 损坏、权限不足或读取失败时返回。
        """
        if not path.exists():
            return None

        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)

            if not isinstance(data, dict):
                return None

            return data

        except (OSError, json.JSONDecodeError):
            return None