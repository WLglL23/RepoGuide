"""
RepoGuide CLI 应用

当前 CLI 属于 v2.2 阶段，新增本地索引持久化支持。

已支持命令：
- version       : 显示当前版本号
- map           : 输出项目地图（优先读取索引，支持 --refresh）
- index         : 扫描项目并保存索引
- init          : 初始化本地 .repoguide 目录结构

设计原则：
1. CLI 只做参数解析和输出，核心逻辑由 Core SDK 提供。
2. 增量索引能力：通过 repoguide index 固化扫描结果，
   随后 repoguide map 直接读取索引，避免重复扫描。
3. 当前使用 JSON 文件存储，后续可升级为 SQLite。
4. CLI 不直接实现扫描、分类、索引生成逻辑，只调用 RepoGuide Core Facade。
"""

from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path

import typer

from repoguide.core.mapper.project_map_formatter import format_project_map
from repoguide.core.repoguide import RepoGuide
from repoguide.storage.local_index_store import LocalIndexStore
from repoguide.config.config_loader import ConfigLoader


# -----------------------------------------------------------------------------
# 版本号读取
# -----------------------------------------------------------------------------
# 如果项目已经通过 pip install -e . 安装，则优先从包元数据读取版本。
# 如果尚未安装，则回退到硬编码版本号。
# -----------------------------------------------------------------------------
try:
    VERSION = package_version("repoguide")
except PackageNotFoundError:
    VERSION = "0.2.0"


# -----------------------------------------------------------------------------
# 默认配置文件内容
# -----------------------------------------------------------------------------
# init 命令会写入：
#
#   .repoguide/config.yml
#
# 当前 v2.2 阶段只负责落盘，不真正参与扫描逻辑。
# 后续可以新增 ConfigLoader，让 Scanner 读取 scan.ignore_dirs。
# -----------------------------------------------------------------------------
DEFAULT_CONFIG_CONTENT = """\
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


# -----------------------------------------------------------------------------
# Typer 应用对象
# -----------------------------------------------------------------------------
app = typer.Typer(
    name="repoguide",
    help="A local-first repository understanding tool for project handoff.",
    no_args_is_help=True,
)


def _resolve_project_root(path: str) -> Path:
    """
    校验并标准化项目路径。

    这个函数用于 CLI 层，避免 index/map/init 每个命令都重复写路径校验逻辑。

    Args:
        path: 用户输入的项目路径。

    Returns:
        标准化后的绝对路径。

    Raises:
        typer.Exit:
            当路径不存在或不是目录时退出。
    """
    root = Path(path).expanduser().resolve()

    if not root.exists():
        typer.echo(f"Error: 路径不存在 - {path}", err=True)
        raise typer.Exit(code=1)

    if not root.is_dir():
        typer.echo(f"Error: 目标不是目录 - {path}", err=True)
        raise typer.Exit(code=1)

    return root


@app.command("version")
def version_command() -> None:
    """
    显示 RepoGuide 当前版本。

    示例：
        repoguide version
    """
    typer.echo(f"RepoGuide {VERSION}")


@app.command("index")
def index_command(
    path: str = typer.Argument(
        ".",
        help="需要建立索引的项目目录，默认为当前目录。",
    ),
) -> None:
    """
    扫描项目并保存索引到 .repoguide/indexes/。

    索引包含：
    - repo_snapshot.json
    - project_map.json

    之后 repoguide map 可直接读取 project_map.json，
    避免每次都重新扫描。
    """
    root = _resolve_project_root(path)

    try:
        typer.echo(f"Indexing project at {root} ...\n")

        # 通过 Core Facade 执行索引：
        # 1. 扫描项目
        # 2. 生成 RepoSnapshot
        # 3. 生成 ProjectMap
        # 4. 保存 repo_snapshot.json 和 project_map.json
        project_map = RepoGuide.index(str(root))

        typer.echo("Index completed.\n")
        typer.echo(f"Project Type:\n{project_map.project_type}\n")
        typer.echo(f"File Count:\n{project_map.file_count}\n")
        typer.echo("Saved:")
        typer.echo("  .repoguide/indexes/repo_snapshot.json")
        typer.echo("  .repoguide/indexes/project_map.json")
        typer.echo("\nNext:")
        typer.echo("  repoguide map")

    except Exception as exc:
        typer.echo(f"Error during indexing: {exc}", err=True)
        raise typer.Exit(code=1) from exc


@app.command("map")
def map_command(
    path: str = typer.Argument(
        ".",
        help="项目根目录路径，默认为当前目录。",
    ),
    refresh: bool = typer.Option(
        False,
        "--refresh",
        "-r",
        help="强制重新扫描并更新索引。",
    ),
) -> None:
    """
    输出项目地图。

    默认行为：
    - 如果 .repoguide/indexes/project_map.json 存在且可读取，直接读取并输出。
    - 如果索引不存在或损坏，则临时扫描并输出，但不保存索引。
    - 使用 --refresh / -r 时，强制重新扫描并更新索引。
    """
    root = _resolve_project_root(path)

    try:
        store = LocalIndexStore(root)

        # 注意：
        # 不能只用 store.has_project_map() 判断是否使用了缓存。
        # 因为 project_map.json 可能存在但内容损坏。
        #
        # load_project_map() 返回非 None，才说明缓存确实可用。
        cached_before = store.load_project_map() is not None

        if refresh:
            typer.echo(f"Refreshing index for {root} ...\n")

        project_map = RepoGuide.map(str(root), refresh=refresh)

        if refresh:
            typer.echo("Index refreshed.\n")
        elif cached_before:
            typer.echo("Using cached index.\n")
        else:
            typer.echo(
                "No cached index found. Showing temporary scan result.\n"
                "Tip: Run 'repoguide index .' to save the index.\n"
            )

        output = format_project_map(project_map.to_dict())
        typer.echo(output)

    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
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

    创建目录结构：

        .repoguide/
          config.yml
          indexes/
          cache/
          overlays/
          traces/
          patches/
          logs/

    当前 v2.2 阶段：
    - init 只负责创建目录和默认配置。
    - index 才负责写入 repo_snapshot.json 和 project_map.json。
    """
    root = _resolve_project_root(path)

    base_dir = root / ".repoguide"
    base_dir.mkdir(parents=True, exist_ok=True)

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

        # 使用配置加载器处理 config.yml
        config_path = ConfigLoader.config_path(root)
        config_exists_before = config_path.exists()

        ConfigLoader.create_default_config(root, force=force)

        if config_exists_before and not force:
            typer.echo(f"RepoGuide structure already exists at {base_dir}")
            typer.echo(f"Skipped existing config: {config_path}")
            typer.echo("Use --force to overwrite config.yml.")
        else:
            typer.echo(f"Initialized RepoGuide structure at {base_dir}")


def main() -> None:
    """
    CLI 入口函数。

    pyproject.toml 中应配置：

        [project.scripts]
        repoguide = "repoguide.cli.app:main"

    安装后可以直接运行：

        repoguide version
        repoguide init .
        repoguide index .
        repoguide map .
        repoguide map . --refresh
    """
    app()


if __name__ == "__main__":
    main()