"""
RepoGuide 核心门面（Core Facade）- v2.3 配置集成版

自动加载项目配置并传递给 SnapshotBuilder，
保持 map/index 接口简洁。

当前核心能力：
- map(root_path)         : 优先读取缓存的项目地图，否则临时扫描。
- index(root_path)       : 强制扫描、生成快照和地图，并保存索引。
- build_snapshot         : 仅构建快照。
- build_project_map      : 从快照生成项目地图。

设计原则：
1. 对调用方隐藏扫描、分类、索引读写的细节。
2. 自动加载项目配置（.repoguide/config.yml），不存在时使用内置默认值。
3. 只读操作（map）不自动保存索引，写操作（index）才会持久化。
"""

from pathlib import Path

from repoguide.core.mapper.project_mapper import generate_project_map_from_snapshot
from repoguide.core.models.project_map import ProjectMap
from repoguide.core.models.repo_snapshot import RepoSnapshot
from repoguide.core.snapshot.snapshot_builder import SnapshotBuilder
from repoguide.config.config_loader import ConfigLoader
from repoguide.storage.local_index_store import LocalIndexStore


class RepoGuide:
    """
    RepoGuide 核心门面。

    提供两套主要工作流：
    1. 临时查看：map() 优先读缓存，若无则临时扫描（不保存）。
    2. 索引固化：index() 强制扫描并保存到 .repoguide/indexes/。

    内部自动加载项目配置文件，支持自定义忽略目录、项目名称等。
    """

    @staticmethod
    def map(root_path: str, refresh: bool = False) -> ProjectMap:
        """
        获取项目的 ProjectMap。

        行为：
        - refresh=False（默认）：
            1. 尝试读取 .repoguide/indexes/project_map.json
            2. 存在且合法 → 直接返回
            3. 不存在 → 临时扫描项目（不保存索引）
        - refresh=True：
            强制重新扫描并更新索引。

        Args:
            root_path: 项目根目录路径。
            refresh: 是否强制重建索引。

        Returns:
            ProjectMap 对象。
        """
        # 路径标准化与校验
        resolved_root = RepoGuide._resolve_root_path(root_path)

        # 刷新模式委托给 index 方法，保证唯一的“保存索引”逻辑
        if refresh:
            return RepoGuide.index(str(resolved_root))

        # 尝试读取已有缓存
        store = LocalIndexStore(resolved_root)
        cached = store.load_project_map()
        if cached is not None:
            return cached

        # 没有缓存：加载配置并执行临时扫描（不保存）
        config = ConfigLoader.load(str(resolved_root))
        snapshot = SnapshotBuilder.build(str(resolved_root), config=config)
        return generate_project_map_from_snapshot(snapshot)

    @staticmethod
    def index(root_path: str) -> ProjectMap:
        """
        扫描项目，生成快照和项目地图，并保存为本地索引。

        具体流程：
        1. 加载项目配置（ConfigLoader）
        2. 构建 RepoSnapshot（SnapshotBuilder）
        3. 生成 ProjectMap
        4. 持久化 snapshot 和 project_map 到 .repoguide/indexes/

        Args:
            root_path: 项目根目录路径。

        Returns:
            新生成并已保存的 ProjectMap。
        """
        resolved_root = RepoGuide._resolve_root_path(root_path)

        # 加载配置（不存在则用默认配置）
        config = ConfigLoader.load(str(resolved_root))

        # 构建快照（传入配置以影响扫描行为）
        snapshot = SnapshotBuilder.build(str(resolved_root), config=config)

        # 从快照生成项目地图
        project_map = generate_project_map_from_snapshot(snapshot)

        # 保存索引文件
        store = LocalIndexStore(resolved_root)
        store.save_snapshot(snapshot)
        store.save_project_map(project_map)

        return project_map

    @staticmethod
    def build_snapshot(root_path: str) -> RepoSnapshot:
        """
        仅构建 RepoSnapshot，不生成 ProjectMap，也不保存索引。

        适用场景：
        - 测试快照生成逻辑。
        - 其它模块需要直接消费 RepoSnapshot 时。

        Args:
            root_path: 项目根目录路径。

        Returns:
            RepoSnapshot 对象。
        """
        resolved_root = RepoGuide._resolve_root_path(root_path)
        config = ConfigLoader.load(str(resolved_root))
        return SnapshotBuilder.build(str(resolved_root), config=config)

    @staticmethod
    def build_project_map(snapshot: RepoSnapshot) -> ProjectMap:
        """
        从已有的 RepoSnapshot 生成 ProjectMap。

        该方法不执行任何扫描或 I/O 操作，纯粹做数据转换。

        Args:
            snapshot: 已构建好的 RepoSnapshot 实例。

        Returns:
            聚合后的 ProjectMap。

        Raises:
            TypeError: 传入对象不是 RepoSnapshot 实例时抛出。
        """
        if not isinstance(snapshot, RepoSnapshot):
            raise TypeError("snapshot 必须是 RepoSnapshot 实例")
        return generate_project_map_from_snapshot(snapshot)

    @staticmethod
    def _resolve_root_path(root_path: str) -> Path:
        """
        校验并标准化项目根路径。

        所有对外方法统一调用此函数以保证路径行为一致。

        Args:
            root_path: 用户输入的路径（相对或绝对）。

        Returns:
            解析后的绝对路径 Path 对象。

        Raises:
            ValueError: root_path 为空字符串。
            FileNotFoundError: 路径不存在。
            NotADirectoryError: 路径存在但并非目录。
        """
        if not root_path or not str(root_path).strip():
            raise ValueError("root_path 不能为空")

        resolved_root = Path(root_path).expanduser().resolve()

        if not resolved_root.exists():
            raise FileNotFoundError(f"路径不存在：{root_path}")

        if not resolved_root.is_dir():
            raise NotADirectoryError(f"目标不是目录：{root_path}")

        return resolved_root