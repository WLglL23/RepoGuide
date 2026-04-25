"""
文件分类与项目类型识别模块。

本模块提供两个核心工具类：
- FileClassifier：根据文件名、路径片段等规则对单个或多个文件进行分类，赋予角色标签（role）。
- ProjectTypeIdentifier：基于文件列表和项目根目录内容，推断项目类型（如 Java Spring Boot、Python FastAPI 等）。
模块还提供了便捷的函数接口。
"""

import fnmatch
from pathlib import Path
from typing import List, Dict


class FileClassifier:
    """v0 文件分类器：只做规则分类，不做 AST。

    通过多个维度的静态规则匹配，为文件添加角色标签（role）。
    规则包括：
    - 精确文件名匹配（EXACT_NAME_RULES）
    - 通配符匹配（WILDCARD_RULES）
    - 路径目录名匹配（PATH_PART_RULES）
    - 特定扩展名匹配（如 SQL 文件）
    未匹配返回 "unknown"。
    """

    # 精确文件名规则：文件名（小写）必须完全等于集合中的某个值
    EXACT_NAME_RULES = {
        "readme": {
            "readme.md",
            "readme.txt",
            "readme.rst",
        },
        "build_manifest": {
            "pom.xml",
            "build.gradle",
            "build.gradle.kts",
            "requirements.txt",
            "pyproject.toml",
            "package.json",
            "cargo.toml",
            "go.mod",
        },
        "config": {
            "application.yml",
            "application.yaml",
            "application.properties",
            ".env.example",
            ".env.sample",
            ".env.template",
            "config.yml",
            "config.yaml",
            "config.json",
            "settings.py",
        },
        "infra": {
            "dockerfile",
            "docker-compose.yml",
            "docker-compose.yaml",
            "jenkinsfile",
        },
    }

    # 通配符规则：使用 fnmatch 进行模式匹配（对文件名不区分大小写？注意文件名已转为小写）
    WILDCARD_RULES = {
        "entrypoint_candidate": {
            "*application.java",
            "main.py",
            "app.py",
            "server.py",
            "index.js",
            "server.js",
        },
    }

    # 路径片段规则：文件的任意目录层级名称（小写）若与关键字集合有交集，则匹配
    PATH_PART_RULES = {
        "controller_candidate": {
            "controller",
            "controllers",
            "route",
            "routes",
            "router",
            "routers",
        },
        "service_candidate": {
            "service",
            "services",
            "business",
            "biz",
        },
        "repository_candidate": {
            "mapper",
            "mappers",
            "repository",
            "repositories",
            "repo",
            "repos",
            "dao",
            "daos",
        },
        "test": {
            "test",
            "tests",
            "testing",
            "spec",
            "specs",
            "__tests__",
        },
    }

    @classmethod
    def classify_file(cls, file_path: str) -> str:
        """对单个文件进行分类，返回角色标签。

        Args:
            file_path: 文件的相对路径（如 "src/main.py"）。

        Returns:
            角色字符串，例如 "entrypoint_candidate"、"readme"、"sql"、"unknown" 等。
        """
        path = Path(file_path)
        # 文件名统一小写以避免大小写差异
        filename = path.name.lower()
        # 路径所有部分转为小写集合，用于目录层级匹配
        path_parts = {part.lower() for part in path.parts}
        # 扩展名小写，用于 SQL 等特定识别
        suffix = path.suffix.lower()

        # 优先级 1：精确文件名匹配
        for role, names in cls.EXACT_NAME_RULES.items():
            if filename in names:
                return role

        # 优先级 2：通配符匹配
        for role, patterns in cls.WILDCARD_RULES.items():
            for pattern in patterns:
                if fnmatch.fnmatch(filename, pattern):
                    return role

        # 优先级 3：扩展名匹配（目前仅 SQL）
        if suffix == ".sql":
            return "sql"

        # 优先级 4：路径片段包含匹配
        for role, keywords in cls.PATH_PART_RULES.items():
            if path_parts & keywords:  # 集合交集检查
                return role

        # 无法识别
        return "unknown"

    @classmethod
    def classify_files(cls, files: List[Dict]) -> List[Dict]:
        """批量分类文件，在原有文件信息上增加 role 字段。

        接收 scanner 返回的文件信息，并追加 role 字段。

        Args:
            files: 文件信息列表，每个元素为字典，至少包含 "path" 键。

        Returns:
            带 role 字段的文件信息列表，其他字段原样保留。

        Example:
            输入：
            [
                {"path": "src/main.py", "size": 100, ...}
            ]
            输出：
            [
                {"path": "src/main.py", "size": 100, ..., "role": "entrypoint_candidate"}
            ]
        """
        classified = []

        for file_info in files:
            item = dict(file_info)  # 浅拷贝，避免修改原数据
            item["role"] = cls.classify_file(item["path"])
            classified.append(item)

        return classified


class ProjectTypeIdentifier:
    """v0 项目类型识别器。

    基于文件列表（至少包含路径）以及可选的仓库根目录，
    通过关键字匹配和特定文件内容扫描，推断项目框架类型。
    """

    @classmethod
    def identify_project_type(cls, files: List[Dict], repo_root: str | None = None) -> str:
        """识别项目类型。

        Args:
            files: 文件信息列表，每个元素至少包含 "path" 键（相对路径）。
            repo_root: 仓库根目录的绝对路径，用于读取文件内容进行进一步判断（可选）。

        Returns:
            项目类型字符串，可能的值包括：
            - "java-springboot"
            - "python-fastapi"
            - "node-project"
            - "python-project"
            - "java-project"
            - "unknown"
        """
        # 将所有路径转为小写，方便后续比较
        paths = [file["path"].lower() for file in files]
        # 提取所有文件名（小写）
        names = {Path(path).name for path in paths}

        # 检查 Java 构建文件和 Application.java 入口文件
        has_pom = "pom.xml" in names
        has_gradle = "build.gradle" in names or "build.gradle.kts" in names
        has_application_java = any(
            path.endswith(".java") and "application" in Path(path).name.lower()
            for path in paths
        )

        # Spring Boot 特征：Maven 或 Gradle + Application.java
        if (has_pom or has_gradle) and has_application_java:
            return "java-springboot"

        # Python FastAPI：依赖清单中包含 fastapi
        if "requirements.txt" in names and repo_root:
            # 检查 requirements.txt 前 80 行是否包含 fastapi
            if cls._root_file_contains(repo_root, "requirements.txt", "fastapi"):
                return "python-fastapi"

        if "pyproject.toml" in names and repo_root:
            # 检查 pyproject.toml 前 80 行是否包含 fastapi
            if cls._root_file_contains(repo_root, "pyproject.toml", "fastapi"):
                return "python-fastapi"

        # Node.js 项目：存在 package.json
        if "package.json" in names:
            return "node-project"

        # 统计 Python 和 Java 文件数量，按多数决定
        py_count = sum(1 for path in paths if path.endswith(".py"))
        java_count = sum(1 for path in paths if path.endswith(".java"))

        if py_count > java_count and py_count > 0:
            return "python-project"

        if java_count > py_count and java_count > 0:
            return "java-project"

        # 无法确定
        return "unknown"

    @classmethod
    def _root_file_contains(cls, repo_root: str, filename: str, search_text: str) -> bool:
        """检查仓库根目录下指定文件的前 80 行是否包含给定文本（不区分大小写）。

        Args:
            repo_root: 仓库根目录。
            filename: 相对于仓库根目录的文件名。
            search_text: 要搜索的文本（小写比较）。

        Returns:
            如果文件存在且在前 80 行内找到搜索文本则返回 True，否则 False。
        """
        file_path = Path(repo_root) / filename

        if not file_path.exists():
            return False

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f):
                    if i >= 80:  # 只检查前 80 行，避免大文件扫描
                        break

                    if search_text.lower() in line.lower():
                        return True

            return False
        except OSError:
            return False


# 模块级便捷函数，直接委托给对应类方法

def classify_file(path: str) -> str:
    """便捷函数：分类单个文件，等同于 FileClassifier.classify_file。"""
    return FileClassifier.classify_file(path)


def classify_files(files: List[Dict]) -> List[Dict]:
    """便捷函数：批量分类文件，等同于 FileClassifier.classify_files。"""
    return FileClassifier.classify_files(files)


def identify_project_type(files: List[Dict], repo_root: str | None = None) -> str:
    """便捷函数：识别项目类型，等同于 ProjectTypeIdentifier.identify_project_type。"""
    return ProjectTypeIdentifier.identify_project_type(files, repo_root)