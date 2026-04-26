"""
RepoGuide 核心门面（Core Facade）

这是 v1 Core SDK 的统一入口。

在 v0 阶段，调用方需要自己手动串联：

    scan_repo()
      -> classify_files()
      -> identify_project_type()
      -> generate_project_map()
      -> format_project_map()

这会导致 main.py 或未来 CLI 层知道太多 Core 内部细节。

进入 v1 后，RepoGuide 需要提供一个更稳定的门面类：

    RepoGuide.map(root_path) -> ProjectMap

这样调用方不需要关心 Scanner、Classifier、SnapshotBuilder、ProjectMapper
之间如何协作，只需要拿到最终的结构化 ProjectMap 即可。

当前 v1 只暴露 map() 方法。
后续版本可以逐步扩展：

    RepoGuide.index(...)
    RepoGuide.ask(...)
    RepoGuide.explain_api(...)
    RepoGuide.explain_flow(...)
    RepoGuide.diff(...)
    RepoGuide.diagnose(...)

但现在不要提前实现这些能力。
"""

from repoguide.core.mapper.project_mapper import generate_project_map_from_snapshot
from repoguide.core.models.project_map import ProjectMap
from repoguide.core.snapshot.snapshot_builder import SnapshotBuilder


class RepoGuide:
    """
    RepoGuide 核心门面。

    设计目标：
    1. 对外提供简单稳定的 Core SDK 入口。
    2. 隐藏扫描、分类、快照构建、项目地图生成等内部步骤。
    3. 返回结构化数据模型，而不是散装 dict。
    4. 保持后续 CLI / API / Web 都可以复用同一套 Core 能力。

    当前 v1 暂时只提供：

        map(root_path) -> ProjectMap

    注意：
        这里的 map 不是 Python 内置 map 函数，而是“生成项目地图”的业务方法。
    """

    @staticmethod
    def map(root_path: str) -> ProjectMap:
        """
        分析一个本地项目，返回结构化项目地图。

        内部流程：

            1. SnapshotBuilder.build(root_path)
               扫描本地目录，识别文件角色，生成 RepoSnapshot。

            2. generate_project_map_from_snapshot(snapshot)
               将 RepoSnapshot 聚合为 ProjectMap。

        Args:
            root_path:
                项目根目录路径，可以是相对路径，也可以是绝对路径。
                例如：
                    "."
                    "E:/STUDY/My/RepoGuide"
                    "/Users/me/projects/demo"

        Returns:
            ProjectMap:
                结构化项目地图对象，包含：
                    - root_path
                    - project_type
                    - file_count
                    - important_files
                    - entrypoint_candidates
                    - config_candidates
                    - build_files
                    - test_files
                    - possible_run_commands
                    - top_level_tree
                    - language_breakdown
                    - role_summary
                    - top_languages

        Raises:
            ValueError:
                当 root_path 为空字符串时抛出。

            FileNotFoundError:
                当 root_path 不存在时，由 SnapshotBuilder 继续向上抛出。

        Example:
            >>> guide = RepoGuide()
            >>> project_map = guide.map(".")
            >>> print(project_map.project_type)
            python-project

            如果要兼容旧 formatter：

            >>> from repoguide.core.mapper.project_map_formatter import format_project_map
            >>> print(format_project_map(project_map.to_dict()))
        """
        if not root_path or not str(root_path).strip():
            raise ValueError("root_path 不能为空")

        # 1. 构建仓库快照。
        #
        # RepoSnapshot 是 v1 的核心中间模型。
        # 它包含：
        # - 仓库路径
        # - 项目名称
        # - 项目类型
        # - RepoFile 列表
        # - 入口文件、配置文件、构建文件、测试文件等派生列表
        snapshot = SnapshotBuilder.build(root_path)

        # 2. 从 RepoSnapshot 生成 ProjectMap。
        #
        # ProjectMap 是更高层的人类可读结构视图。
        # 它面向 formatter、CLI、未来 API 和 Web。
        return generate_project_map_from_snapshot(snapshot)