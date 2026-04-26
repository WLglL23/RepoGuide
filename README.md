# RepoGuide

RepoGuide 是一个面向 **项目交接、陌生仓库理解、本地开发诊断** 的代码仓库理解工具。

当前项目已完成到 **v2.2 本地索引持久化阶段**。

RepoGuide 当前可以通过命令行扫描本地项目，识别项目类型、关键文件、入口候选、配置文件、测试文件，并生成项目地图。同时支持将扫描结果保存到本地 `.repoguide/indexes/` 中，后续可以直接读取缓存索引，避免每次都重新扫描。

---

## 项目定位

RepoGuide 的长期目标是：

> 将一个陌生代码仓库转换成一个可交互、可追踪、可诊断的项目知识系统，帮助开发者快速理解项目结构、启动方式、核心模块、接口流程，并在本地修改出错时定位问题来源。

RepoGuide 不是普通的代码 RAG 问答壳子，也不是单纯的代码搜索工具。

它更关注：

- 新人接手陌生项目
- 项目交接文档生成
- 项目结构理解
- 启动方式分析
- 接口和调用链解释
- 本地 git diff 与错误日志诊断
- Patch 建议和测试验证闭环

当前阶段还没有实现完整 Agent 能力，但已经完成本地扫描、Core SDK、CLI 和本地索引缓存的基础闭环。

---

## 当前版本状态

当前版本：`0.2.0`

当前阶段：`v2.2 本地索引持久化`

已完成：

- v0：纯文本原型
- v1：Core SDK 雏形
- v2.1：Typer CLI 基础命令
- v2.2：本地索引持久化

当前支持命令：

```bash
repoguide version
repoguide init .
repoguide index .
repoguide map .
repoguide map . --refresh
```

当前暂不支持：

- LLM 问答
- 向量检索
- Java / Python AST 深度解析
- 接口解析
- 调用链追踪
- git diff 分析
- 错误日志诊断
- Patch 生成
- API Server
- Web UI

---

## 当前已实现能力

### 1. 本地目录扫描

RepoGuide 可以扫描一个本地项目目录，并收集文件基础信息：

- 文件相对路径
- 文件名
- 文件大小
- 文件扩展名
- 修改时间

默认忽略常见无关目录：

```text
.git
node_modules
target
dist
build
out
venv
.venv
__pycache__
.idea
.vscode
.mypy_cache
.pytest_cache
```

同时支持读取简化版 `.gitignore` 规则。

---

### 2. 文件角色分类

当前通过文件名、扩展名和路径规则识别文件角色。

已支持的文件角色：

```text
readme
build_manifest
config
infra
entrypoint_candidate
controller_candidate
service_candidate
repository_candidate
test
sql
unknown
```

示例：

| 文件 / 路径 | 识别角色 |
|---|---|
| `README.md` | `readme` |
| `pom.xml` | `build_manifest` |
| `requirements.txt` | `build_manifest` |
| `pyproject.toml` | `build_manifest` |
| `package.json` | `build_manifest` |
| `application.yml` | `config` |
| `.env.example` | `config` |
| `Dockerfile` | `infra` |
| `docker-compose.yml` | `infra` |
| `main.py` | `entrypoint_candidate` |
| `app.py` | `entrypoint_candidate` |
| `DemoApplication.java` | `entrypoint_candidate` |
| `tests/test_xxx.py` | `test` |
| `schema.sql` | `sql` |

---

### 3. 项目类型候选识别

当前支持基于规则识别项目类型候选：

```text
java-springboot
python-fastapi
node-project
python-project
java-project
unknown
```

识别规则示例：

| 条件 | 项目类型 |
|---|---|
| 存在 `pom.xml` / `build.gradle`，并存在 `*Application.java` | `java-springboot` |
| `requirements.txt` 或 `pyproject.toml` 中包含 `fastapi` | `python-fastapi` |
| 存在 `package.json` | `node-project` |
| Python 文件较多 | `python-project` |
| Java 文件较多 | `java-project` |

当前识别结果是候选判断，不是完整语义解析。

---

### 4. 语言检测

RepoGuide 当前支持基于扩展名进行简单语言检测。

支持：

```text
.py
.java
.js
.ts
.xml
.yml
.yaml
.toml
.json
.sql
.md
```

语言检测结果会进入 `RepoFile.language`，后续解析器和索引器可以根据语言字段选择不同策略。

---

### 5. Core SDK 数据模型

当前已经引入核心数据模型：

```text
RepoFile
RepoSnapshot
ProjectMap
```

#### RepoFile

表示仓库中的单个文件。

主要字段：

```text
path
name
size
extension
modified_time
role
language
```

#### RepoSnapshot

表示一次仓库扫描得到的结构化快照。

主要字段：

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

#### ProjectMap

表示从 `RepoSnapshot` 聚合得到的项目地图。

主要字段：

```text
root_path
project_type
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
```

---

### 6. Core Facade

当前提供统一 Core SDK 入口：

```python
from repoguide import RepoGuide

project_map = RepoGuide.map(".")
```

当前支持：

```python
RepoGuide.map(root_path, refresh=False)
RepoGuide.index(root_path)
RepoGuide.build_snapshot(root_path)
RepoGuide.build_project_map(snapshot)
```

核心流程：

```text
RepoGuide.map(path)
  ↓
优先读取 .repoguide/indexes/project_map.json
  ↓
如果没有索引，则临时扫描
  ↓
返回 ProjectMap
```

索引流程：

```text
RepoGuide.index(path)
  ↓
SnapshotBuilder.build(path)
  ↓
RepoSnapshot
  ↓
ProjectMapper.generate_project_map_from_snapshot(snapshot)
  ↓
ProjectMap
  ↓
LocalIndexStore 保存 JSON 索引
```

---

### 7. CLI 命令

RepoGuide 当前使用 Typer 提供命令行入口。

#### 查看版本

```bash
repoguide version
```

输出示例：

```text
RepoGuide 0.2.0
```

#### 初始化本地目录

```bash
repoguide init .
```

会创建：

```text
.repoguide/
  config.yml
  indexes/
  cache/
  overlays/
  traces/
  patches/
  logs/
```

#### 建立索引

```bash
repoguide index .
```

会扫描当前项目，并保存：

```text
.repoguide/indexes/repo_snapshot.json
.repoguide/indexes/project_map.json
```

输出示例：

```text
Indexing project at E:\STUDY\My\RepoGuide ...

Index completed.

Project Type:
python-project

File Count:
32

Saved:
  .repoguide/indexes/repo_snapshot.json
  .repoguide/indexes/project_map.json

Next:
  repoguide map
```

#### 查看项目地图

```bash
repoguide map .
```

行为：

- 如果存在可用索引，优先读取 `.repoguide/indexes/project_map.json`
- 如果没有索引，则临时扫描并输出项目地图
- 临时扫描不会自动保存索引

#### 强制刷新项目地图

```bash
repoguide map . --refresh
```

或：

```bash
repoguide map . -r
```

行为：

- 重新扫描项目
- 更新 `.repoguide/indexes/repo_snapshot.json`
- 更新 `.repoguide/indexes/project_map.json`
- 输出最新项目地图

---

## 输出示例

```text
RepoGuide v0 Project Map

Project Root:
E:\STUDY\My\RepoGuide

Detected Project Type:
python-project

File Count:
32

Important Files:
- README.md
- main.py
- pyproject.toml

Entrypoint Candidates:
- main.py

Config Candidates:
- none

Build Files:
- pyproject.toml

Test Files:
- tests/test_cli.py
- tests/test_local_index_store.py
- tests/test_repoguide_index.py

Possible Run Commands:
- python main.py
- pytest

Top-level Structure:
RepoGuide/
  repoguide/
  tests/
  main.py
  pyproject.toml
  README.md
```

---

## 项目结构

当前项目结构大致如下：

```text
RepoGuide/
  repoguide/
    __init__.py
    cli/
      __init__.py
      app.py
    core/
      __init__.py
      repoguide.py
      scanner/
        __init__.py
        repo_scanner.py
      classifier/
        __init__.py
        file_classifier.py
      language/
        __init__.py
        language_detector.py
      models/
        __init__.py
        repo_file.py
        repo_snapshot.py
        project_map.py
      snapshot/
        __init__.py
        snapshot_builder.py
      mapper/
        __init__.py
        project_mapper.py
        project_map_formatter.py
    storage/
      __init__.py
      local_index_store.py
  tests/
  main.py
  pyproject.toml
  pytest.ini
  README.md
  .gitignore
```

---

## 核心模块说明

### scanner

路径：

```text
repoguide/core/scanner/
```

职责：

- 扫描本地目录
- 忽略无关目录
- 读取简化版 `.gitignore`
- 返回文件元信息列表

---

### classifier

路径：

```text
repoguide/core/classifier/
```

职责：

- 识别文件角色
- 识别项目类型候选

---

### language

路径：

```text
repoguide/core/language/
```

职责：

- 根据扩展名推断语言
- 为后续 parser / indexer 提供基础字段

---

### models

路径：

```text
repoguide/core/models/
```

职责：

- 定义核心数据模型
- 当前包含：
  - `RepoFile`
  - `RepoSnapshot`
  - `ProjectMap`

---

### snapshot

路径：

```text
repoguide/core/snapshot/
```

职责：

- 串联 scanner、classifier、RepoFile 构造
- 生成 `RepoSnapshot`

---

### mapper

路径：

```text
repoguide/core/mapper/
```

职责：

- 将 `RepoSnapshot` 聚合为 `ProjectMap`
- 将 `ProjectMap` 格式化为文本输出

---

### storage

路径：

```text
repoguide/storage/
```

职责：

- 本地索引持久化
- 当前使用 JSON 文件
- 当前保存：
  - `repo_snapshot.json`
  - `project_map.json`

---

### cli

路径：

```text
repoguide/cli/
```

职责：

- 提供 Typer CLI 入口
- 当前支持：
  - `version`
  - `init`
  - `index`
  - `map`

---

## 本地索引目录

执行：

```bash
repoguide init .
```

后会创建：

```text
.repoguide/
  config.yml
  indexes/
  cache/
  overlays/
  traces/
  patches/
  logs/
```

执行：

```bash
repoguide index .
```

后会生成：

```text
.repoguide/indexes/
  repo_snapshot.json
  project_map.json
```

当前 `.repoguide/` 是本地运行目录，建议加入 `.gitignore`。

---

## 安装与使用

### 1. 创建虚拟环境

Windows PowerShell：

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux：

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. 安装项目

开发模式安装：

```bash
pip install -e .
```

安装开发依赖：

```bash
pip install -e ".[dev]"
```

### 3. 查看版本

```bash
repoguide version
```

### 4. 初始化本地目录

```bash
repoguide init .
```

### 5. 建立索引

```bash
repoguide index .
```

### 6. 查看项目地图

```bash
repoguide map .
```

### 7. 强制刷新索引

```bash
repoguide map . --refresh
```

---

## 运行测试

安装开发依赖：

```bash
pip install -e ".[dev]"
```

运行测试：

```bash
pytest
```

当前测试覆盖：

- Scanner 基础流程
- FileClassifier
- LanguageDetector
- RepoFile
- RepoSnapshot
- ProjectMap
- SnapshotBuilder
- ProjectMapper
- RepoGuide Core Facade
- LocalIndexStore
- CLI version / init / index / map

---

## `.gitignore` 建议

推荐至少包含：

```gitignore
# Python packaging metadata
*.egg-info/

# Python cache
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
venv/
.venv/

# Test / type-check cache
.pytest_cache/
.mypy_cache/

# IDE
.idea/
.vscode/

# Build outputs
dist/
build/
out/
target/
node_modules/

# Local env
.env

# RepoGuide local runtime files
.repoguide/
```

说明：

- `repoguide.egg-info/` 是 `pip install -e .` 生成的本地安装元数据，不应该提交
- `.repoguide/` 是 RepoGuide 的本地运行目录，不应该提交
- `.env` 可能包含敏感信息，不应该提交
- `.env.example`、`.env.sample`、`.env.template` 可以提交

---

## 当前数据流

### 临时查看项目地图

```text
repoguide map .
  ↓
RepoGuide.map(path, refresh=False)
  ↓
优先读取 .repoguide/indexes/project_map.json
  ↓
如果不存在，则临时扫描
  ↓
输出 Project Map
```

### 建立本地索引

```text
repoguide index .
  ↓
RepoGuide.index(path)
  ↓
SnapshotBuilder.build(path)
  ↓
RepoSnapshot
  ↓
ProjectMapper.generate_project_map_from_snapshot(snapshot)
  ↓
ProjectMap
  ↓
LocalIndexStore.save_snapshot(snapshot)
  ↓
LocalIndexStore.save_project_map(project_map)
```

### 刷新项目地图

```text
repoguide map . --refresh
  ↓
RepoGuide.map(path, refresh=True)
  ↓
RepoGuide.index(path)
  ↓
重新扫描并保存索引
  ↓
输出 Project Map
```

---

## 当前开发进度

```text
[x] v0 纯文本原型
[x] 本地目录扫描
[x] 文件角色分类
[x] 项目类型候选识别
[x] 项目地图生成
[x] 文本格式化输出

[x] v1 Core SDK 雏形
[x] RepoFile
[x] RepoSnapshot
[x] ProjectMap
[x] LanguageDetector
[x] SnapshotBuilder
[x] RepoGuide Core Facade

[x] v2.1 CLI 基础命令
[x] Typer CLI
[x] repoguide version
[x] repoguide init
[x] repoguide map

[x] v2.2 本地索引持久化
[x] LocalIndexStore
[x] repo_snapshot.json
[x] project_map.json
[x] repoguide index
[x] repoguide map --refresh

[ ] v2.3 配置读取
[ ] v3 代码结构解析
[ ] v4 本地工作区诊断
[ ] v5 LLM 问答增强
[ ] v6 Agent 编排
[ ] v7 Patch 和测试闭环
[ ] v8 API Server
[ ] v9 Web UI
```

---

## 后续路线

### v2.3：配置读取

目标：

- 读取 `.repoguide/config.yml`
- 让扫描器使用配置里的 ignore_dirs
- 支持项目级配置
- 支持测试命令白名单配置

---

### v3：代码结构解析

目标：

- 支持 Java / Spring Boot 基础解析
- 支持 Python / FastAPI 基础解析
- 识别 Controller / Router
- 识别 Service / Mapper
- 抽取 API 路由
- 建立基础符号索引

---

### v4：本地工作区诊断

目标：

- 读取 `git status`
- 读取 `git diff`
- 解析错误日志
- 结合最近修改和日志定位问题

---

### v5：LLM 问答增强

目标：

- 在已有结构化索引基础上接入 LLM
- 基于证据生成回答
- 回答必须尽量附带文件路径、符号和行号

---

### v6：Agent 编排

目标：

- 问题分类
- 检索规划
- 上下文构建
- 回答生成
- 证据校验
- Trace 记录

---

### v7：Patch 和测试闭环

目标：

- 生成 PatchSuggestion
- 用户确认后 apply
- 执行测试
- 测试失败后回流诊断

---

### v8：API Server

目标：

- 使用 FastAPI 封装 Core SDK
- 为后续 Web UI 提供接口

---

### v9：Web UI

目标：

- 项目总览页
- 模块地图页
- 接口列表页
- 报错诊断页
- Patch 展示页
- Trace 页面

---

## 设计原则

RepoGuide 当前和后续开发都遵循以下原则：

1. **本地优先**

   优先分析本地工作区，而不是远程仓库。

2. **Core SDK 优先**

   核心能力先沉淀在 Core SDK，CLI / API / Web 都只作为外层调用者。

3. **结构化索引优先**

   不一开始就把整个仓库塞给 LLM，而是先扫描、分类、建模和索引。

4. **证据优先**

   后续问答、接口解释、诊断结果都应尽量包含文件路径、函数名、行号或证据摘要。

5. **安全默认**

   不默认上传代码，不默认读取敏感 `.env`，不默认自动修改文件，不默认执行危险命令。

6. **Web 后置**

   Web 只是展示层，应该在 Core、CLI、索引、诊断能力稳定后再做。

---

## 项目总结

RepoGuide 当前已经完成从 v0 到 v2.2 的基础工程闭环：

```text
本地扫描
  ↓
文件分类
  ↓
核心数据模型
  ↓
项目地图生成
  ↓
CLI 命令
  ↓
本地 JSON 索引持久化
```

当前已经可以作为一个本地项目地图工具使用：

```bash
repoguide init .
repoguide index .
repoguide map .
```

后续会在这个基础上继续扩展配置读取、代码结构解析、接口理解、调用链分析、本地 diff 诊断、LLM 证据化问答、Patch 建议和测试闭环。