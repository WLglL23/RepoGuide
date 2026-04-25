"""
项目地图生成器。

v0 职责：
1. 接收扫描/分类后的文件列表
2. 聚合关键文件、入口候选、配置候选、测试文件
3. 根据项目类型给出启动命令候选
4. 生成稳定的项目地图 dict
"""

from pathlib import Path
from typing import List, Dict


class ProjectMapper:
    """项目地图映射器。"""

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

    IMPORTANT_ROLES = {
        "readme",
        "config",
        "infra",
        "build_manifest",
    }

    MAX_IMPORTANT_FILES = 30

    @classmethod
    def generate_project_map(
        cls,
        files: List[Dict],
        root_path: str,
        project_type: str = "unknown",
    ) -> Dict:
        """
        生成结构化项目地图。

        Args:
            files: 已分类文件列表，每个元素至少包含 path 和 role
            root_path: 项目根路径
            project_type: 项目类型

        Returns:
            项目地图 dict
        """
        entrypoints = []
        configs = []
        builds = []
        tests = []
        important = []

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


        for path in entrypoints:
            if path not in important:
                important.append(path)

        important = sorted(set(important))[:cls.MAX_IMPORTANT_FILES]
        entrypoints = sorted(set(entrypoints))
        configs = sorted(set(configs))
        builds = sorted(set(builds))
        tests = sorted(set(tests))

        commands = list(cls.RUN_COMMAND_MAP.get(project_type, cls.DEFAULT_COMMANDS))

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

    @classmethod
    def _generate_top_level_tree_from_files(
        cls,
        root_path: str,
        files: List[Dict],
    ) -> str:
        """
        根据已扫描文件生成一级目录树。

        不重新读取磁盘，避免和 scanner 的忽略规则不一致。
        """
        root = Path(root_path)
        root_name = root.name or str(root)

        top_dirs = set()
        top_files = set()

        for file in files:
            path = file.get("path")
            if not path:
                continue

            parts = Path(path).parts

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


def generate_project_map(
    files: List[Dict],
    root_path: str,
    project_type: str = "unknown",
) -> Dict:
    """生成项目地图的便捷函数。"""
    return ProjectMapper.generate_project_map(files, root_path, project_type)