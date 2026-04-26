"""
项目地图生成器（ProjectMapper）。

v0 接口：
- generate_project_map(files, root_path, project_type="unknown") -> dict

v1 接口：
- generate_project_map_from_snapshot(snapshot: RepoSnapshot) -> ProjectMap

迁移原则：
- 旧接口签名与行为完全不变，保证 main.py 和现有测试可以继续工作。
- 新接口内部复用旧逻辑，避免重复实现，然后补充统计信息。
"""

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from repoguide.core.models.project_map import ProjectMap
from repoguide.core.models.repo_snapshot import RepoSnapshot


class ProjectMapper:
    """负责生成项目地图的静态工具类。"""

    # ------------------------------------------------------------------
    # 运行命令映射（v0 已存在，保持不变）
    # ------------------------------------------------------------------
    RUN_COMMAND_MAP = {
        "java-springboot": [
            "mvn spring-boot:run",
            "mvn test",
        ],
        "python-fastapi": [
            "uvicorn main:app --reload",
            "pytest",
        ],
        "node-project": [
            "npm install",
            "npm run dev",
            "npm test",
        ],
        "python-project": [
            "python main.py",
            "pytest",
        ],
        "java-project": [
            "mvn compile",
            "mvn test",
        ],
    }

    DEFAULT_COMMANDS = []

    # ------------------------------------------------------------------
    # 重要角色集合（用于提取 important_files）
    # ------------------------------------------------------------------
    IMPORTANT_ROLES = {
        "readme",
        "config",
        "infra",
        "build_manifest",
    }

    MAX_IMPORTANT_FILES = 30

    # ------------------------------------------------------------------
    # v0 旧接口：从 dict 列表生成 project_map dict
    # ------------------------------------------------------------------
    @classmethod
    def generate_project_map(
        cls,
        files: List[Dict],
        root_path: str,
        project_type: str = "unknown",
    ) -> Dict:
        """
        从 dict 文件列表生成项目地图字典（v0 兼容接口）。

        此方法不应删除，因为 main.py 及现有测试直接依赖它。

        Args:
            files: 已分类的文件信息列表，每个元素为 dict。
            root_path: 项目根路径。
            project_type: 项目类型标识，如 "python-project"。

        Returns:
            包含 entrypoint_candidates, config_candidates 等字段的字典。
        """
        entrypoints = []
        configs = []
        builds = []
        tests = []
        important = []

        # 按角色分类路径
        for file in files:
            path = file.get("path")
            role = file.get("role", "unknown")

            if not path:
                continue

            if role == "entrypoint_candidate":
                entrypoints.append(path)

            if role == "config":
                configs.append(path)

            if role == "build_manifest":
                builds.append(path)

            if role == "test":
                tests.append(path)

            if role in cls.IMPORTANT_ROLES:
                important.append(path)

        # 入口点也视为重要文件
        for path in entrypoints:
            if path not in important:
                important.append(path)

        # 去重、排序、裁剪
        important = sorted(set(important))[:cls.MAX_IMPORTANT_FILES]
        entrypoints = sorted(set(entrypoints))
        configs = sorted(set(configs))
        builds = sorted(set(builds))
        tests = sorted(set(tests))

        # 运行命令
        commands = list(cls.RUN_COMMAND_MAP.get(project_type, cls.DEFAULT_COMMANDS))

        # 一级目录树
        top_level_tree = cls._generate_top_level_tree_from_files(
            root_path=root_path,
            files=files,
        )

        return {
            "root_path": str(Path(root_path).resolve()),
            "project_type": project_type,
            "file_count": len(files),
            "important_files": important,
            "entrypoint_candidates": entrypoints,
            "config_candidates": configs,
            "build_files": builds,
            "test_files": tests,
            "possible_run_commands": commands,
            "top_level_tree": top_level_tree,
        }

    # ------------------------------------------------------------------
    # v1 新接口：从 RepoSnapshot 生成 ProjectMap
    # ------------------------------------------------------------------
    @classmethod
    def generate_project_map_from_snapshot(cls, snapshot: RepoSnapshot) -> ProjectMap:
        """
        从 RepoSnapshot 构建 ProjectMap（v1 推荐接口）。

        此方法内部调用旧接口以获得兼容字段，然后补充 v1 特有的统计信息。

        Args:
            snapshot: 已完成的仓库快照。

        Returns:
            填充完整的 ProjectMap 对象，其 to_dict() 与 v0 formatter 完全兼容。
        """
        # 将快照中的文件转换为 dict 列表，复用旧逻辑
        files_as_dicts = snapshot.files_as_dicts()

        base_map = cls.generate_project_map(
            files=files_as_dicts,
            root_path=snapshot.root_path,
            project_type=snapshot.project_type,
        )

        # 统计语言和角色分布
        language_counter = Counter()
        role_counter = Counter()

        for file in snapshot.files:
            language_counter[file.language] += 1
            role_counter[file.role] += 1

        # 前 5 大语言（排除 unknown）
        top_languages = [
            language
            for language, _ in language_counter.most_common(5)
            if language != "unknown"
        ]

        # 组装 ProjectMap 数据类
        return ProjectMap(
            repo_id=snapshot.repo_id,
            root_path=base_map["root_path"],
            project_name=snapshot.project_name,
            project_type=base_map["project_type"],
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            file_count=base_map["file_count"],

            important_files=base_map["important_files"],
            entrypoint_candidates=base_map["entrypoint_candidates"],
            config_candidates=base_map["config_candidates"],
            build_files=base_map["build_files"],
            test_files=base_map["test_files"],
            possible_run_commands=base_map["possible_run_commands"],
            top_level_tree=base_map["top_level_tree"],

            language_breakdown=dict(language_counter),
            role_summary=dict(role_counter),
            top_languages=top_languages,
        )

    # ------------------------------------------------------------------
    # 内部辅助：从文件列表生成一级目录树
    # ------------------------------------------------------------------
    @classmethod
    def _generate_top_level_tree_from_files(
        cls,
        root_path: str,
        files: List[Dict],
    ) -> str:
        """根据已扫描文件生成一级目录树的文本表示，不重新读取磁盘。"""
        root = Path(root_path)
        root_name = root.name or str(root)

        top_dirs = set()
        top_files = set()

        for file in files:
            path_str = file.get("path")
            if not path_str:
                continue

            parts = Path(path_str).parts
            if not parts:
                continue

            if len(parts) == 1:
                top_files.add(parts[0])
            else:
                top_dirs.add(parts[0])

        lines = [f"{root_name}/"]

        for dirname in sorted(top_dirs, key=str.lower):
            lines.append(f"  {dirname}/")

        for filename in sorted(top_files, key=str.lower):
            lines.append(f"  {filename}")

        return "\n".join(lines)


# ------------------------------------------------------------------
# 模块级便捷函数（保持与原来一致）
# ------------------------------------------------------------------
def generate_project_map(
    files: List[Dict],
    root_path: str,
    project_type: str = "unknown",
) -> Dict:
    """v0 便捷函数。"""
    return ProjectMapper.generate_project_map(files, root_path, project_type)


def generate_project_map_from_snapshot(snapshot: RepoSnapshot) -> ProjectMap:
    """v1 便捷函数。"""
    return ProjectMapper.generate_project_map_from_snapshot(snapshot)