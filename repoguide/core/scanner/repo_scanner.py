"""
仓库扫描器（v2.3 参数化版）

扫描本地项目目录，收集文件的基础信息，
支持自定义忽略目录和隐藏模板白名单，并保留 .gitignore 规则。

注意：
    - 内置默认忽略目录和隐藏模板白名单仍然保留，作为最低安全基线。
    - 外部通过参数传入的列表会与默认值合并，不会直接替换。
    - .gitignore 规则会叠加在目录名忽略规则之上。
"""

import os
import fnmatch
from pathlib import Path
from typing import Dict, List, Optional, Set


# ---------------------------------------------------------------------------
# 内置默认值
# ---------------------------------------------------------------------------

DEFAULT_IGNORE_DIRS: Set[str] = {
    ".git",
    "node_modules",
    "target",
    "dist",
    "build",
    "out",
    "venv",
    ".venv",
    "__pycache__",
    ".idea",
    ".vscode",
    ".mypy_cache",
    ".pytest_cache",
}

HIDDEN_FILE_ALLOWLIST: Set[str] = {
    ".env.example",
    ".env.sample",
    ".env.template",
}


# ---------------------------------------------------------------------------
# .gitignore 工具函数（已保留）
# ---------------------------------------------------------------------------

def load_gitignore(root: str) -> List[str]:
    """
    读取项目根目录下的 .gitignore，返回非空且非注释 pattern 列表。
    """
    gitignore_path = os.path.join(root, ".gitignore")
    patterns: List[str] = []
    if os.path.isfile(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except OSError:
            pass
    return patterns


def should_ignore_by_gitignore(rel_path: str, patterns: List[str]) -> bool:
    """
    判断给定相对路径是否匹配任一 .gitignore pattern。
    使用简化逻辑：仅对路径字符串做 fnmatch（不处理目录前缀斜杠等复杂情况）。
    """
    for pattern in patterns:
        if fnmatch.fnmatch(rel_path, pattern):
            return True
    return False


# ---------------------------------------------------------------------------
# 内部扫描函数（已有，保持原样）
# ---------------------------------------------------------------------------

def scan_local_directory(
    root: Path,
    extra_ignore_dirs: Optional[List[str]] = None,
    extra_hidden_allowlist: Optional[List[str]] = None,
) -> List[Dict]:
    """
    实际的目录遍历逻辑，收集文件信息。

    Args:
        root: 项目根路径（已解析的绝对路径）。
        extra_ignore_dirs: 外部传入的额外忽略目录名列表。
        extra_hidden_allowlist: 外部传入的额外允许隐藏文件列表。

    Returns:
        文件信息字典列表（同 scan_repo 返回格式）。
    """
    # 合并最终忽略目录集合
    final_ignore_dirs = DEFAULT_IGNORE_DIRS.copy()
    if extra_ignore_dirs:
        final_ignore_dirs.update(extra_ignore_dirs)

    # 合并最终隐藏文件白名单
    final_allowlist = HIDDEN_FILE_ALLOWLIST.copy()
    if extra_hidden_allowlist:
        final_allowlist.update(extra_hidden_allowlist)

    # 加载 .gitignore 规则
    gitignore_patterns = load_gitignore(str(root))

    files: List[Dict] = []

    for dirpath, dirnames, filenames in os.walk(str(root)):
        # 过滤需要忽略的目录（直接修改 dirnames 避免进入）
        dirnames[:] = [
            d
            for d in dirnames
            if d not in final_ignore_dirs
        ]

        for filename in filenames:
            # 隐藏文件过滤（以点开头且不在白名单）
            if filename.startswith(".") and filename not in final_allowlist:
                continue

            full_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(full_path, str(root)).replace("\\", "/")

            # .gitignore 二次过滤
            if should_ignore_by_gitignore(rel_path, gitignore_patterns):
                continue

            try:
                stat = os.stat(full_path)
            except OSError:
                continue  # 无权限或链接失效

            files.append({
                "path": rel_path,
                "name": filename,
                "size": stat.st_size,
                "extension": os.path.splitext(filename)[1].lower(),
                "modified_time": stat.st_mtime,
            })

    return files


# ---------------------------------------------------------------------------
# 公共入口：scan_repo
# ---------------------------------------------------------------------------

def scan_repo(
    root_path: str,
    ignore_dirs: Optional[List[str]] = None,
    include_hidden_templates: Optional[List[str]] = None,
) -> List[Dict]:
    """
    扫描项目目录，返回文件信息列表。

    Args:
        root_path: 项目根目录路径（绝对或相对）。
        ignore_dirs: 额外需要忽略的目录名列表，与内置默认值合并。
        include_hidden_templates: 额外允许的隐藏模板文件名列表，与内置默认值合并。

    Returns:
        文件信息字典列表，每个字典包含：
            path, name, size, extension, modified_time
    """
    root = Path(root_path).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"路径不存在：{root_path}")
    if not root.is_dir():
        raise NotADirectoryError(f"路径不是目录：{root_path}")

    return scan_local_directory(
        root=root,
        extra_ignore_dirs=ignore_dirs,
        extra_hidden_allowlist=include_hidden_templates,
    )