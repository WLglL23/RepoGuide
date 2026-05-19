# RepoGuide 当前项目状态

更新时间：2026-05-19

## 当前结论

RepoGuide 当前真实阶段是：本地扫描 + 项目地图生成 + 本地 JSON 索引 + 项目级配置读取已经形成基础闭环；v3 的 `CodeSymbol`、`ApiEndpoint`、`RepoIndex` 数据模型已经起步，但尚未接入 Python/FastAPI parser、结构化索引生成、调用链分析、LLM 问答、Agent 编排、Patch 生成或 Web/API 服务阶段。

这份文档以当前源码和本地检查结果为准。README 和历史设计文档可作为方向参考，但不能直接等同于已完成能力。

## 功能进度表

| 模块 | 当前状态 | 说明 |
|---|---|---|
| 本地目录扫描 | 已实现 | `repoguide/core/scanner/repo_scanner.py` 提供 `scan_repo()`，会遍历本地目录并收集路径、文件名、大小、扩展名、修改时间。 |
| 忽略规则 | 部分实现 | 内置忽略 `.git`、`.venv`、`node_modules`、`__pycache__` 等目录；支持简化版 `.gitignore`；支持隐藏模板文件白名单。 |
| 文件角色分类 | 已实现 | `FileClassifier` 基于文件名、通配符、路径片段、扩展名识别 `readme`、`build_manifest`、`config`、`entrypoint_candidate`、`test` 等角色。 |
| 项目类型识别 | 已实现但较粗 | `ProjectTypeIdentifier` 基于构建文件、入口文件、依赖文本和语言文件数量识别 `java-springboot`、`python-fastapi`、`node-project`、`python-project`、`java-project`、`unknown`。 |
| 语言检测 | 已实现 | `LanguageDetector` 只按扩展名识别 `.py`、`.java`、`.js`、`.ts`、`.xml`、`.yml`、`.yaml`、`.toml`、`.json`、`.sql`、`.md`。 |
| 核心数据模型 | 已实现基础模型 | 已有 `RepoFile`、`RepoSnapshot`、`ProjectMap`，支持 `to_dict()` / `from_dict()` 序列化。 |
| 项目地图生成 | 已实现基础版本 | `ProjectMapper` 可从扫描快照生成重要文件、入口候选、配置候选、构建文件、测试文件、推荐命令、顶层目录树、语言统计、角色统计。 |
| Core Facade | 已实现 | `RepoGuide` 对外提供 `map()`、`index()`、`build_snapshot()`、`build_project_map()`。 |
| 本地索引 | 已实现基础版本 | `LocalIndexStore` 将 `RepoSnapshot` 和 `ProjectMap` 保存为 `.repoguide/indexes/repo_snapshot.json`、`.repoguide/indexes/project_map.json`。 |
| CLI | 已实现基础命令 | `repoguide/cli/app.py` 声明 Typer 命令 `version`、`init`、`index`、`map`。当前 `tests/test_cli.py` 已通过。 |
| 配置读取 | 已实现基础集成 | `ConfigLoader`、`RepoGuideConfig`、`DEFAULT_CONFIG_YAML` 已存在，并传入 `SnapshotBuilder` 影响扫描；`test.allowed_commands` 目前只是配置字段，尚未被测试执行器使用。 |
| 接口模型 | 已起步 | `ApiEndpoint` 已有 dataclass 和 `to_dict()` / `from_dict()`，但还没有 API 路由抽取逻辑。 |
| Python 符号解析 | 已实现第一步 | `PythonParser` 使用标准库 `ast` 提取顶层函数、类、类方法到 `CodeSymbol`；尚未接入 RepoIndex。 |
| RepoIndex 聚合模型 | 已起步 | `RepoIndex` 已能聚合 snapshot、project_map、symbols、api_endpoints，但还没有 builder 或 storage 接入。 |
| git diff 诊断 | 未实现 | 当前没有读取 `git status`、`git diff` 并定位问题的核心模块。 |
| LLM / Agent / Patch / API Server / Web UI | 未实现 | README 和设计文档中有路线图，但当前源码未落地。 |

## 接口清单

### Python SDK

公开入口：

```python
from repoguide import RepoGuide
```

当前主要接口：

```python
RepoGuide.map(root_path: str, refresh: bool = False) -> ProjectMap
RepoGuide.index(root_path: str) -> ProjectMap
RepoGuide.build_snapshot(root_path: str) -> RepoSnapshot
RepoGuide.build_project_map(snapshot: RepoSnapshot) -> ProjectMap
```

行为边界：

- `map(refresh=False)` 优先读取 `.repoguide/indexes/project_map.json`，读取不到才临时扫描；临时扫描不保存索引。
- `map(refresh=True)` 委托 `index()`，会重新扫描并保存索引。
- `index()` 会加载配置、构建快照、生成项目地图并写入本地 JSON 索引。
- `build_snapshot()` 只构建快照，不生成地图，不保存索引。
- `build_project_map()` 只做 `RepoSnapshot -> ProjectMap` 转换，不扫描磁盘。

### CLI

打包入口在 `pyproject.toml`：

```toml
[project.scripts]
repoguide = "repoguide.cli.app:main"
```

源码中声明的命令：

```bash
repoguide version
repoguide init .
repoguide index .
repoguide map .
repoguide map . --refresh
repoguide map . -r
```

当前 `tests/test_cli.py` 已通过，说明基础 CLI 行为可验证。后续若继续改 CLI，需要保持现有测试通过。

### 配置文件

配置路径：

```text
.repoguide/config.yml
```

当前配置模型：

```yaml
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
  include_hidden_templates:
    - .env.example
    - .env.sample
    - .env.template

test:
  allowed_commands:
    - pytest
    - python -m pytest
    - mvn test
    - npm test
```

当前实际使用情况：

- `project.name` 会影响 `RepoSnapshot.project_name`。
- `scan.ignore_dirs` 会传入扫描器，与内置忽略目录合并。
- `scan.include_hidden_templates` 会传入扫描器，与内置隐藏模板白名单合并。
- `test.allowed_commands` 只是保留字段，尚无 TestRunner 使用它。

### 数据模型

`RepoFile` 表示单个文件：

```text
path
name
size
extension
modified_time
role
language
```

`RepoSnapshot` 表示一次扫描快照：

```text
repo_id
root_path
project_name
project_type
files
file_count
created_at
entrypoints
config_files
build_files
test_files
important_files
```

`ProjectMap` 表示聚合后的项目地图：

```text
repo_id
root_path
project_name
project_type
generated_at
file_count
important_files
entrypoint_candidates
config_candidates
build_files
test_files
possible_run_commands
top_level_tree
language_breakdown
role_summary
top_languages
metadata
```

### 本地索引

索引目录：

```text
.repoguide/indexes/
```

当前索引文件：

```text
repo_snapshot.json
project_map.json
```

读写接口：

```python
LocalIndexStore.save_snapshot(snapshot)
LocalIndexStore.load_snapshot()
LocalIndexStore.save_project_map(project_map)
LocalIndexStore.load_project_map()
LocalIndexStore.has_snapshot()
LocalIndexStore.has_project_map()
LocalIndexStore.has_index()
```

读取失败策略：文件不存在、JSON 损坏、字段缺失或反序列化失败时，`load_*()` 返回 `None`，由上层决定是否重新扫描。

## 数据流

### `repoguide map .`

```text
CLI map
  -> RepoGuide.map(path, refresh=False)
  -> LocalIndexStore.load_project_map()
  -> 如果缓存可用：返回 ProjectMap
  -> 如果缓存不可用：ConfigLoader.load()
  -> SnapshotBuilder.build()
  -> scan_repo()
  -> classify_files()
  -> identify_project_type()
  -> generate_project_map_from_snapshot()
  -> 输出项目地图
```

临时扫描不会保存 `.repoguide/indexes/`。

### `repoguide index .`

```text
CLI index
  -> RepoGuide.index(path)
  -> ConfigLoader.load()
  -> SnapshotBuilder.build()
  -> generate_project_map_from_snapshot()
  -> LocalIndexStore.save_snapshot()
  -> LocalIndexStore.save_project_map()
  -> 输出索引完成信息
```

这是当前唯一明确的索引持久化主流程。

### `repoguide map . --refresh`

```text
CLI map --refresh
  -> RepoGuide.map(path, refresh=True)
  -> RepoGuide.index(path)
  -> 重新扫描并覆盖本地索引
  -> 输出最新项目地图
```

## 当前风险

### 1. Python 命令必须显式使用项目虚拟环境

全局 `python` / `py` 在当前 Codex 执行上下文中不可用，但项目虚拟环境可用。后续验证请使用：

```powershell
E:\Project\My\RepoGuide\.venv\Scripts\python.exe -m compileall repoguide main.py
E:\Project\My\RepoGuide\.venv\Scripts\python.exe -m pytest -q
```

2026-05-19 验证结果：全量测试 `45 passed`。

### 2. 源码中存在明显乱码

多个源码文件的中文注释和部分字符串显示为乱码。风险最高的是：

```text
repoguide/cli/app.py
repoguide/core/mapper/project_map_formatter.py
main.py
```

尤其是 CLI 和 formatter 里存在用户可见输出字符串。当前 `compileall` 和测试已通过，说明至少没有语法级损坏；但用户可见文案仍建议后续逐步修正。

### 3. v3 模型尚未接入主流程

以下文件已经不再是空文件，但仍只是模型层：

```text
repoguide/core/models/api_endpoint.py
repoguide/core/models/code_symbol.py
repoguide/core/models/repo_index.py
```

它们不代表接口解析、符号索引或综合索引已经接入。下一步应实现 parser 和 index builder。

### 4. README 与源码版本边界不一致

README 说当前阶段是 `v2.2 本地索引持久化`，但源码已经出现 v2.3 配置读取相关实现：

```text
repoguide/config/config_loader.py
repoguide/config/config_model.py
repoguide/config/default_config.py
SnapshotBuilder.build(..., config=...)
RepoGuide.index/map/build_snapshot 加载 ConfigLoader
```

建议后续把 README 降级为入口说明，把真实进度集中维护在本文档或一个版本化 changelog 中。

## 下一步建议

1. 扩展 FastAPI decorator 识别，把 `@app.get()`、`@router.post()` 等提取为 `ApiEndpoint`。
2. 新增 RepoIndex builder：把 `RepoSnapshot`、`ProjectMap`、symbols、api_endpoints 聚合为 `RepoIndex`。
3. 扩展 `LocalIndexStore` 保存和读取 `repo_index.json`。
4. 最后再考虑 CLI 展示命令，例如 `repoguide symbols` 或 `repoguide apis`。

## 一句话路线判断

RepoGuide 现在最应该做的不是继续往上堆 Agent 或 Web UI，而是把 v3 的结构化索引做成一个小而清楚的闭环：模型 -> parser -> index builder -> 本地 JSON。
