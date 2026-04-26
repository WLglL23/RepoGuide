"""
RepoGuide 核心门面（Core Facade）

这是 RepoGuide Core SDK 的统一入口。

v1 阶段：
    - 提供 RepoGuide.map(root_path)
    - 内部封装 SnapshotBuilder 和 ProjectMapper
    - 返回结构化 ProjectMap

v2.2 阶段：
    - 增加本地索引持久化能力
    - 支持 RepoGuide.index(root_path)
    - 支持 RepoGuide.map(root_path, refresh=False)
    - 优先读取 .repoguide/indexes/project_map.json
    - 支持 refresh=True 强制重建索引

当前 Core Facade 提供：
    - map(root_path, refresh=False) -> ProjectMap
    - index(root_path) -> ProjectMap
    - build_snapshot(root_path) -> RepoSnapshot
    - build_project_map(snapshot) -> ProjectMap

注意：
    当前仍然不包含 LLM、接口解析、调用链分析、git diff 诊断或 Patch 能力。
    这些能力会在后续阶段继续挂到 RepoGuide 这个统一门面上。
"""

from pathlib import Path

from repoguide.core.mapper.project_mapper import generate_project_map_from_snapshot
from repoguide.core.models.project_map import ProjectMap
from repoguide.core.models.repo_snapshot import RepoSnapshot
from repoguide.core.snapshot.snapshot_builder import SnapshotBuilder
from repoguide.storage.local_index_store import LocalIndexStore


class RepoGuide:
    """
    RepoGuide 核心门面。

    设计目标：
    1. 对外提供简单稳定的 Core SDK 入口。
    2. 隐藏扫描、分类、快照构建、项目地图生成、索引读写等内部步骤。
    3. 返回结构化数据模型，而不是散装 dict。
    4. 让 CLI、未来 API Server、未来 Web 都复用同一套 Core 能力。

    当前核心流程：

        map(root_path)
          -> 优先读取本地 project_map.json
          -> 如果没有索引，则临时扫描并生成 ProjectMap

        index(root_path)
          -> 扫描项目
          -> 生成 RepoSnapshot
          -> 生成 ProjectMap
          -> 保存 repo_snapshot.json 和 project_map.json

        map(root_path, refresh=True)
          -> 等价于 index(root_path)
    """

    # ------------------------------------------------------------------
    # 公共入口：map
    # ------------------------------------------------------------------

    @staticmethod
    def map(root_path: str, refresh: bool = False) -> ProjectMap:
        """
        获取项目的 ProjectMap。

        行为说明：

        1. refresh=False，默认行为：
            - 优先尝试读取：
                .repoguide/indexes/project_map.json
            - 如果本地索引存在且合法，则直接返回。
            - 如果索引不存在或损坏，则执行一次临时扫描。
            - 临时扫描结果不会自动写入索引。

        2. refresh=True：
            - 强制重新扫描项目。
            - 重新生成 RepoSnapshot 和 ProjectMap。
            - 保存到 .repoguide/indexes/。
            - 返回新的 ProjectMap。

        Args:
            root_path:
                项目根目录路径，可以是相对路径或绝对路径。

            refresh:
                是否强制重建索引。

        Returns:
            ProjectMap:
                项目地图对象。

        Raises:
            ValueError:
                当 root_path 为空时抛出。

            FileNotFoundError:
                当 root_path 不存在时抛出。
        """
        resolved_root = RepoGuide._resolve_root_path(root_path)

        # refresh=True 时，map 直接委托给 index。
        #
        # 这样可以保证“强制刷新”的行为只有一份实现：
        # - 扫描
        # - 生成 snapshot
        # - 生成 project_map
        # - 保存索引
        if refresh:
            return RepoGuide.index(str(resolved_root))

        # refresh=False 时，优先读取本地索引。
        #
        # 如果用户之前运行过：
        #     repoguide index .
        #
        # 那么这里会直接读取：
        #     .repoguide/indexes/project_map.json
        #
        # 这样可以避免每次 map 都重新扫描项目。
        store = LocalIndexStore(resolved_root)
        cached_project_map = store.load_project_map()

        if cached_project_map is not None:
            return cached_project_map

        # 如果没有本地索引，则退化为临时扫描。
        #
        # 注意：
        #     这里不保存索引。
        #     保存索引的动作只由 index() 或 refresh=True 触发。
        #
        # 这样可以区分：
        #     map   = 查看项目地图
        #     index = 构建或更新本地索引
        snapshot = SnapshotBuilder.build(str(resolved_root))
        return generate_project_map_from_snapshot(snapshot)

    # ------------------------------------------------------------------
    # 公共入口：index
    # ------------------------------------------------------------------

    @staticmethod
    def index(root_path: str) -> ProjectMap:
        """
        扫描项目，生成快照和项目地图，并保存为本地索引。

        内部流程：

            1. 校验并标准化 root_path
            2. SnapshotBuilder.build(root_path)
               生成 RepoSnapshot
            3. generate_project_map_from_snapshot(snapshot)
               生成 ProjectMap
            4. LocalIndexStore.save_snapshot(snapshot)
               写入 .repoguide/indexes/repo_snapshot.json
            5. LocalIndexStore.save_project_map(project_map)
               写入 .repoguide/indexes/project_map.json
            6. 返回 ProjectMap

        Args:
            root_path:
                项目根目录路径。

        Returns:
            ProjectMap:
                新生成并已保存的项目地图。

        Raises:
            ValueError:
                当 root_path 为空时抛出。

            FileNotFoundError:
                当 root_path 不存在时抛出。
        """
        resolved_root = RepoGuide._resolve_root_path(root_path)

        # 1. 构建仓库快照。
        #
        # SnapshotBuilder 内部会完成：
        # - scan_repo
        # - classify_files
        # - identify_project_type
        # - RepoFile.from_dict
        # - RepoSnapshot 构造
        snapshot = SnapshotBuilder.build(str(resolved_root))

        # 2. 从快照生成项目地图。
        #
        # ProjectMap 是更高层的视图，适合 CLI/API/Web 消费。
        project_map = generate_project_map_from_snapshot(snapshot)

        # 3. 保存本地索引。
        #
        # LocalIndexStore 当前使用 JSON 文件：
        # - repo_snapshot.json
        # - project_map.json
        #
        # 后续进入真正 RepoIndex 阶段时，这里可以替换或扩展为 SQLite。
        store = LocalIndexStore(resolved_root)
        store.save_snapshot(snapshot)
        store.save_project_map(project_map)

        return project_map

    # ------------------------------------------------------------------
    # 辅助入口：build_snapshot
    # ------------------------------------------------------------------

    @staticmethod
    def build_snapshot(root_path: str) -> RepoSnapshot:
        """
        仅构建 RepoSnapshot，不生成 ProjectMap，也不保存索引。

        适用场景：
            - 单元测试
            - 后续 indexer 需要直接消费 RepoSnapshot
            - 后续 CLI 想单独展示 snapshot 摘要

        Args:
            root_path:
                项目根目录路径。

        Returns:
            RepoSnapshot:
                仓库扫描快照。
        """
        resolved_root = RepoGuide._resolve_root_path(root_path)
        return SnapshotBuilder.build(str(resolved_root))

    # ------------------------------------------------------------------
    # 辅助入口：build_project_map
    # ------------------------------------------------------------------

    @staticmethod
    def build_project_map(snapshot: RepoSnapshot) -> ProjectMap:
        """
        从已有 RepoSnapshot 生成 ProjectMap。

        这个方法不会读写本地索引。

        适用场景：
            - 测试 ProjectMapper
            - 后续其他模块已经持有 RepoSnapshot，不希望重新扫描
            - 后续 Indexer / API 层需要手动组合流程

        Args:
            snapshot:
                已构建好的 RepoSnapshot。

        Returns:
            ProjectMap:
                从 snapshot 聚合得到的项目地图。

        Raises:
            TypeError:
                当 snapshot 不是 RepoSnapshot 实例时抛出。
        """
        if not isinstance(snapshot, RepoSnapshot):
            raise TypeError("snapshot 必须是 RepoSnapshot 实例")

        return generate_project_map_from_snapshot(snapshot)

    # ------------------------------------------------------------------
    # 内部工具：路径校验
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_root_path(root_path: str) -> Path:
        """
        校验并标准化项目根路径。

        为什么单独抽出来：
            map()、index()、build_snapshot() 都需要做相同的路径校验。
            如果每个方法各写一遍，后续容易出现行为不一致。

        Args:
            root_path:
                用户传入的项目路径。

        Returns:
            Path:
                解析后的绝对路径。

        Raises:
            ValueError:
                root_path 为空时抛出。

            FileNotFoundError:
                路径不存在时抛出。

            NotADirectoryError:
                路径存在但不是目录时抛出。
        """
        if not root_path or not str(root_path).strip():
            raise ValueError("root_path 不能为空")

        resolved_root = Path(root_path).expanduser().resolve()

        if not resolved_root.exists():
            raise FileNotFoundError(f"路径不存在：{root_path}")

        if not resolved_root.is_dir():
            raise NotADirectoryError(f"目标不是目录：{root_path}")

        return resolved_root