import fnmatch
import os
from pathlib import Path
from typing import List, Dict


"""
v0 扫描器职责：
1. 接收本地仓库路径
2. 递归扫描文件
3. 忽略无意义目录
4. 返回文件元信息列表

注意：
v0 只支持本地目录，不支持 GitHub 远程仓库。
"""


DEFAULT_IGNORE_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    "venv",
    ".venv",
    ".idea",
    ".vscode",
    ".mypy_cache",
    ".pytest_cache",
    "target",
    "dist",
    "build",
    "out",
}

DEFAULT_IGNORE_FILES = {
    ".DS_Store",
}

HIDDEN_FILE_ALLOWLIST = {
    ".env.example",
    ".env.sample",
    ".env.template",
}


def normalize_path(path: str) -> Path:
    """标准化路径"""
    return Path(path).expanduser().resolve()


def load_gitignore(root_path: Path) -> List[str]:
    """加载 .gitignore 中的基础忽略模式。v0 只做简化支持。"""
    gitignore_path = root_path / ".gitignore"
    ignore_list = []

    if not gitignore_path.exists():
        return ignore_list

    try:
        with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                ignore_list.append(line)
    except OSError:
        pass

    return ignore_list


def should_ignore_by_gitignore(rel_path: Path, ignore_list: List[str]) -> bool:
    """
    简化版 .gitignore 匹配。

    支持：
    1. *.log
    2. target/
    3. src/*.tmp
    4. 文件名匹配
    """
    path_str = rel_path.as_posix()

    for pattern in ignore_list:
        normalized = pattern.strip()

        if not normalized:
            continue

        # 暂不支持反向规则，例如 !important.log
        if normalized.startswith("!"):
            continue

        # 目录规则，例如 target/
        if normalized.endswith("/"):
            dir_name = normalized.rstrip("/")
            if dir_name in rel_path.parts:
                return True

        # 路径整体匹配
        if fnmatch.fnmatch(path_str, normalized):
            return True

        # 文件名匹配
        if fnmatch.fnmatch(rel_path.name, normalized):
            return True

    return False


def should_skip_file(filename: str) -> bool:
    """判断文件是否应该跳过"""
    if filename in DEFAULT_IGNORE_FILES:
        return True

    # .env.example 这类文件需要保留，因为它是配置候选
    if filename in HIDDEN_FILE_ALLOWLIST:
        return False

    # v0 不扫描其他隐藏文件，避免把 .env、密钥文件纳入输出
    if filename.startswith("."):
        return True

    return False


def scan_local_directory(root: Path) -> List[Dict]:
    """递归扫描本地目录"""
    files_info = []
    ignore_list = load_gitignore(root)

    for dirpath, dirnames, filenames in os.walk(root):
        # 原地修改 dirnames，可以阻止 os.walk 继续进入这些目录
        dirnames[:] = [
            d for d in dirnames
            if d not in DEFAULT_IGNORE_DIRS
        ]

        current_dir = Path(dirpath)

        for filename in filenames:
            if should_skip_file(filename):
                continue

            file_path = current_dir / filename
            rel_path = file_path.relative_to(root)

            if should_ignore_by_gitignore(rel_path, ignore_list):
                continue

            try:
                stat = file_path.stat()
            except (PermissionError, OSError):
                continue

            files_info.append({
                "path": rel_path.as_posix(),
                "name": filename,
                "size": stat.st_size,
                "extension": file_path.suffix.lower(),
                "modified_time": stat.st_mtime,
            })

    return files_info


def scan_repo(root_path: str) -> List[Dict]:
    """扫描本地仓库或本地目录"""
    root = normalize_path(root_path)

    if not root.exists():
        raise FileNotFoundError(f"路径不存在：{root_path}")

    if root.is_file():
        stat = root.stat()
        return [{
            "path": root.name,
            "name": root.name,
            "size": stat.st_size,
            "extension": root.suffix.lower(),
            "modified_time": stat.st_mtime,
        }]

    return scan_local_directory(root)