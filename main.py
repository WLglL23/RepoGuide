"""
RepoGuide v1 命令行脚本入口。

当前仍然不是正式 CLI 工具，只是一个轻量命令行入口：

    python main.py .

它调用 Core Facade：

    RepoGuide.map(path)

然后使用旧 formatter 输出文本项目地图。

后续 v2 CLI 阶段再替换为 Typer / Click，并支持：

    repoguide init
    repoguide index .
    repoguide map
"""

import argparse
import sys

from repoguide import RepoGuide
from repoguide.core.mapper.project_map_formatter import format_project_map


def main() -> int:
    """
    命令行入口。

    当前只支持一个位置参数 path：

        python main.py .
        python main.py 绝对路径

    Returns:
        0 表示成功。
        1 表示失败。
    """
    parser = argparse.ArgumentParser(
        prog="repoguide-v1",
        description="RepoGuide v1: generate a basic project map for a local repository.",
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the local project directory. Defaults to current directory.",
    )

    args = parser.parse_args()

    try:
        # 通过 Core Facade 获取结构化 ProjectMap。
        #
        # main.py 不再直接关心：
        # - scan_repo
        # - classify_files
        # - identify_project_type
        # - SnapshotBuilder
        # - ProjectMapper
        #
        # 这些细节都应该封装在 Core SDK 内部。
        project_map = RepoGuide.map(args.path)

        # 当前 formatter 仍然接收 dict。
        # 所以这里通过 to_dict() 做兼容。
        output = format_project_map(project_map.to_dict())

        print(output)
        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except PermissionError as e:
        print(f"Permission error: {e}", file=sys.stderr)
        return 1

    except ValueError as e:
        print(f"Invalid input: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())