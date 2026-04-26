"""
RepoGuide CLI 应用

当前 CLI 属于 v2.1 阶段的正式命令行入口雏形。

已支持命令：
- version : 显示当前版本号
- map     : 生成项目地图并输出格式化文本
- init    : 初始化本地 .repoguide 目录结构

当前 CLI 不包含：
- LLM 问答
- 向量检索
- 接口解析
- 调用链追踪
- git diff 诊断
- Patch 生成
- 测试执行

这些能力会在后续阶段基于 Core SDK 继续扩展。

设计原则：
1. CLI 只做参数解析和输出，不直接承担核心业务逻辑。
2. 真正的项目分析能力统一调用 Core SDK，即 RepoGuide.map()。
3. CLI 输出暂时复用已有 format_project_map()，保持 v0/v1 输出稳定。
"""

from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path

import typer

from repoguide.core.mapper.project_map_formatter import format_project_map
from repoguide.core.repoguide import RepoGuide


# -----------------------------------------------------------------------------
# 版本号读取
# -----------------------------------------------------------------------------
# 优先从包元数据中读取版本号。
#
# 当项目通过以下命令安装后：
#
#     pip install -e .
#
# importlib.metadata 可以从 pyproject.toml / 安装元数据中读取版本。
#
# 如果当前代码还没有以包形式安装，例如直接 python repoguide/cli/app.py，
# 则可能读取失败，此时回退到硬编码版本号。
# -----------------------------------------------------------------------------
try:
    VERSION = package_version("repoguide")
except PackageNotFoundError:
    VERSION = "0.2.0"


# -----------------------------------------------------------------------------
# Typer 应用对象
# -----------------------------------------------------------------------------
# 这里定义的是 CLI 根应用。
#
# 安装后，pyproject.toml 中的：
#
#     [project.scripts]
#     repoguide = "repoguide.cli.app:main"
#
# 会把 main() 注册成终端命令 repoguide。
# -----------------------------------------------------------------------------
app = typer.Typer(
    name="repoguide",
    help="A local-first repository understanding tool for project handoff.",
    no_args_is_help=True,
)


@app.command("version")
def version_command() -> None:
    """
    显示 RepoGuide 当前版本。

    示例：

        repoguide version
    """
    typer.echo(f"RepoGuide {VERSION}")


@app.command("map")
def map_command(
    path: str = typer.Argument(
        ".",
        help="项目根目录路径，默认为当前目录。",
    ),
) -> None:
    """
    分析指定路径的项目，生成并打印项目地图。

    示例：

        repoguide map .
        repoguide map E:/STUDY/My/SomeProject

    当前该命令内部调用：

        RepoGuide.map(path)

    然后将 ProjectMap 转换为 dict，交给已有 formatter 输出。
    """
    root = Path(path).expanduser().resolve()

    if not root.exists():
        typer.echo(f"Error: 路径不存在 - {path}", err=True)
        raise typer.Exit(code=1)

    if not root.is_dir():
        typer.echo(f"Error: 目标不是目录 - {path}", err=True)
        raise typer.Exit(code=1)

    try:
        typer.echo(f"Analyzing project at {root} ...\n")

        # 通过 Core Facade 获取结构化 ProjectMap。
        #
        # CLI 不直接调用：
        # - scan_repo
        # - classify_files
        # - SnapshotBuilder
        # - ProjectMapper
        #
        # 这些内部流程都由 Core SDK 封装。
        project_map = RepoGuide.map(str(root))

        # 当前 formatter 仍然接收 dict。
        # ProjectMap.to_dict() 用于兼容 v0/v1 的文本输出格式。
        output = format_project_map(project_map.to_dict())
        typer.echo(output)

    except PermissionError as exc:
        typer.echo(f"Permission error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    except ValueError as exc:
        typer.echo(f"Invalid input: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    except Exception as exc:
        # 第一版 CLI 先统一兜底，避免用户看到长堆栈。
        # 后续可以增加 --debug 参数，在 debug 模式下打印完整 traceback。
        typer.echo(f"Unexpected error: {exc}", err=True)
        raise typer.Exit(code=1) from exc


@app.command("init")
def init_command(
    path: str = typer.Argument(
        ".",
        help="需要初始化 .repoguide 的项目目录，默认为当前目录。",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="如果 config.yml 已存在，是否覆盖它。",
    ),
) -> None:
    """
    初始化 RepoGuide 本地工作目录。

    示例：

        repoguide init
        repoguide init .
        repoguide init E:/STUDY/My/SomeProject
        repoguide init . --force

    初始化后会创建：

        .repoguide/
          config.yml
          indexes/
          cache/
          overlays/
          traces/
          patches/
          logs/

    注意：
        当前 v2.1 只负责创建目录和默认配置。
        暂时不会读取 config.yml 参与扫描逻辑。
        配置读取会放到后续 v2.2 / v3 阶段。
    """
    root = Path(path).expanduser().resolve()

    if not root.exists():
        typer.echo(f"Error: 路径不存在 - {path}", err=True)
        raise typer.Exit(code=1)

    if not root.is_dir():
        typer.echo(f"Error: 目标不是目录 - {path}", err=True)
        raise typer.Exit(code=1)

    base_dir = root / ".repoguide"

    # 创建 .repoguide 根目录。
    #
    # exist_ok=True 的意义：
    # - 如果目录不存在，则创建。
    # - 如果目录已存在，不报错。
    #
    # 这样 init 命令可以重复执行，用来补齐缺失目录。
    base_dir.mkdir(parents=True, exist_ok=True)

    # 本地工作目录结构。
    #
    # indexes  : 后续保存 RepoIndex
    # cache    : 后续保存缓存
    # overlays : 后续保存 Workspace Overlay
    # traces   : 后续保存执行 Trace
    # patches  : 后续保存 PatchSuggestion
    # logs     : 后续保存 RepoGuide 自身日志
    subdirs = [
        "indexes",
        "cache",
        "overlays",
        "traces",
        "patches",
        "logs",
    ]

    for subdir in subdirs:
        (base_dir / subdir).mkdir(parents=True, exist_ok=True)

    config_path = base_dir / "config.yml"

    # 默认配置文件。
    #
    # 当前只是落盘，不参与实际扫描逻辑。
    # 后续可让 scanner / config loader 读取 scan.ignore_dirs。
    config_content = """\
version: 1

project:
  name: null

scan:
  ignore_dirs:
    - .git
    - node_modules
    - target
    - dist
    - build
    - out
    - venv
    - .venv
    - __pycache__
    - .idea
    - .vscode
    - .mypy_cache
    - .pytest_cache

test:
  allowed_commands:
    - pytest
    - python -m pytest
    - mvn test
    - npm test
"""

    if config_path.exists() and not force:
        typer.echo(f"RepoGuide structure already exists at {base_dir}")
        typer.echo(f"Skipped existing config: {config_path}")
        typer.echo("Use --force to overwrite config.yml.")
        return

    config_path.write_text(config_content, encoding="utf-8")

    typer.echo(f"Initialized RepoGuide structure at {base_dir}")


def main() -> None:
    """
    CLI 入口函数。

    该函数会被 pyproject.toml 中的 project.scripts 注册为：

        repoguide = "repoguide.cli.app:main"

    因此安装后可以直接执行：

        repoguide version
        repoguide map .
        repoguide init
    """
    app()


if __name__ == "__main__":
    main()