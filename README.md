# RepoGuide

RepoGuide 是一个面向 **项目交接、陌生仓库理解、本地开发诊断** 的代码仓库理解工具。

当前项目处于 **v0 纯文本原型阶段**。  
这一阶段的目标不是做完整 Agent，也不是做代码 RAG 问答系统，而是先完成一个最小可运行闭环：

> 输入一个本地项目路径，扫描项目目录，识别关键文件、项目类型、入口候选、配置候选，并输出一份基础项目地图。

后续 RepoGuide 会逐步扩展为支持接口理解、调用链分析、Git diff 诊断、错误日志诊断、Patch 建议和测试验证的本地开发辅助系统。

---

## 当前版本状态

当前版本：`v0`

当前阶段目标：

- 本地目录扫描
- 文件角色分类
- 项目类型候选识别
- 项目地图生成
- 文本格式化输出
- 基础测试覆盖

当前阶段不包含：

- LLM 问答
- 向量检索
- AST / Tree-sitter 深度解析
- 接口解析
- 调用链追踪
- Git diff 分析
- 错误日志诊断
- Patch 生成
- 测试命令执行
- API Server
- Web UI

---

## 项目定位

RepoGuide 的长期目标是：

> 将一个陌生代码仓库转换成一个可交互、可追踪、可诊断的项目知识系统，帮助开发者快速理解项目结构、启动方式、核心模块、接口流程，并在本地修改出错时定位问题来源。

RepoGuide 不是：

- 普通全文搜索工具
- 普通代码 RAG 问答壳子
- 单纯的代码补全工具
- 一开始就做 Web 页面的展示项目

RepoGuide 更关注：

- 本地项目结构理解
- 项目交接文档生成
- 接口与调用链解释
- 本地工作区状态分析
- Git diff 与错误日志联合诊断
- Patch 建议与测试验证闭环

---

## 当前已实现能力

### 1. 本地目录扫描

当前可以扫描一个本地项目目录，并收集文件基础信息：

- 文件相对路径
- 文件名
- 文件大小
- 文件扩展名
- 修改时间

扫描器会默认忽略常见无关目录，例如：

```text
.git
node_modules
__pycache__
venv
.venv
.idea
.vscode
.mypy_cache
.pytest_cache
target
dist
build
out
```

同时支持读取简化版 `.gitignore` 规则。

---

### 2. 文件角色分类

当前通过文件名、扩展名和路径规则识别文件角色。

已支持的文件角色包括：

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

当前识别结果是 **候选判断**，不是完整语义解析。

---

### 4. 项目地图生成

当前可以生成结构化项目地图，包含：

- 项目根路径
- 项目类型
- 文件数量
- 重要文件
- 入口候选文件
- 配置候选文件
- 构建文件
- 测试文件
- 推荐运行命令
- 顶层目录结构

---

### 5. 文本格式化输出

当前可以将项目地图格式化为人类可读文本。

示例输出：

```text
RepoGuide v0 Project Map

Project Root:
E:\STUDY\My\RepoGuide

Detected Project Type:
python-project

File Count:
12

Important Files:
- README.md
- main.py
- pytest.ini

Entrypoint Candidates:
- main.py

Config Candidates:
- none

Build Files:
- none

Test Files:
- tests/test_v0_pipeline.py

Possible Run Commands:
- python main.py
- pytest

Top-level Structure:
RepoGuide/
  repoguide/
  tests/
  main.py
  pytest.ini
  README.md
```

---

## 项目结构

当前项目结构如下：

```text
RepoGuide/
  .venv/
  repoguide/
    __init__.py
    core/
      __init__.py
      scanner/
        __init__.py
        repo_scanner.py
      classifier/
        __init__.py
        file_classifier.py
      mapper/
        __init__.py
        project_mapper.py
        project_map_formatter.py
  tests/
    test_v0_pipeline.py
  设计文档/
  .gitignore
  main.py
  pytest.ini
  README.md
```

核心目录说明：

| 路径 | 职责 |
|---|---|
| `repoguide/core/scanner/` | 本地仓库扫描 |
| `repoguide/core/classifier/` | 文件角色分类与项目类型识别 |
| `repoguide/core/mapper/` | 项目地图生成与格式化 |
| `tests/` | 测试用例 |
| `main.py` | 当前 v0 命令入口 |
| `设计文档/` | 项目设计文档 |

---

## 快速开始

### 1. 进入项目目录

```bash
cd RepoGuide
```

### 2. 创建虚拟环境

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

### 3. 安装测试依赖

当前 v0 主要依赖 Python 标准库。  
如果需要运行测试，安装 `pytest`：

```bash
pip install pytest
```

### 4. 运行 RepoGuide v0

扫描当前项目：

```bash
python main.py .
```

扫描其他本地项目：

```bash
python main.py E:\STUDY\My\SomeProject
```

或者：

```bash
python main.py /path/to/your/project
```

---

## 使用示例

### 扫描当前项目

```bash
python main.py .
```

输出示例：

```text
RepoGuide v0 Project Map

Project Root:
E:\STUDY\My\RepoGuide

Detected Project Type:
python-project

File Count:
12

Important Files:
- README.md
- main.py
- pytest.ini

Entrypoint Candidates:
- main.py

Config Candidates:
- none

Build Files:
- none

Test Files:
- tests/test_v0_pipeline.py

Possible Run Commands:
- python main.py
- pytest

Top-level Structure:
RepoGuide/
  repoguide/
  tests/
  main.py
  pytest.ini
  README.md
```

---

## 运行测试

执行：

```bash
pytest
```

如果测试通过，说明当前 v0 主流程可以正常运行：

```text
scanner -> classifier -> project_mapper -> formatter
```

当前测试重点不是覆盖所有边界，而是保证 v0 核心链路不断：

1. 能扫描目录
2. 能分类文件
3. 能识别项目类型候选
4. 能生成项目地图
5. 能格式化输出文本

---

## 核心模块说明

### Scanner

路径：

```text
repoguide/core/scanner/repo_scanner.py
```

职责：

- 接收本地项目路径
- 递归扫描文件
- 忽略无关目录
- 读取简化版 `.gitignore`
- 返回文件元信息列表

主要函数：

```text
scan_repo(root_path)
scan_local_directory(root)
load_gitignore(root_path)
should_ignore_by_gitignore(rel_path, ignore_list)
normalize_path(path)
```

输出数据示例：

```python
{
    "path": "repoguide/core/scanner/repo_scanner.py",
    "name": "repo_scanner.py",
    "size": 2048,
    "extension": ".py",
    "modified_time": 1710000000.0
}
```

---

### Classifier

路径：

```text
repoguide/core/classifier/file_classifier.py
```

职责：

- 根据文件名、路径、扩展名识别文件角色
- 根据文件集合识别项目类型候选

主要类：

```text
FileClassifier
ProjectTypeIdentifier
```

主要函数：

```text
classify_file(path)
classify_files(files)
identify_project_type(files, repo_root)
```

文件角色示例：

```text
README.md -> readme
main.py -> entrypoint_candidate
requirements.txt -> build_manifest
tests/test_v0_pipeline.py -> test
```

---

### Project Mapper

路径：

```text
repoguide/core/mapper/project_mapper.py
```

职责：

- 聚合扫描和分类结果
- 生成结构化项目地图
- 给出候选运行命令
- 生成顶层目录结构

主要类：

```text
ProjectMapper
```

主要函数：

```text
generate_project_map(files, root_path, project_type)
```

输出结构示例：

```python
{
    "root_path": "...",
    "project_type": "python-project",
    "file_count": 12,
    "important_files": [...],
    "entrypoint_candidates": [...],
    "config_candidates": [...],
    "build_files": [...],
    "test_files": [...],
    "possible_run_commands": [...],
    "top_level_tree": "..."
}
```

---

### Project Map Formatter

路径：

```text
repoguide/core/mapper/project_map_formatter.py
```

职责：

- 将 `project_map` 字典转换为可读文本
- 保持输出格式稳定
- 为后续 CLI 输出做准备

主要函数：

```text
format_project_map(project_map)
```

---

## 当前 v0 数据流

当前主流程如下：

```text
用户输入本地路径
  ↓
scan_repo()
  ↓
classify_files()
  ↓
identify_project_type()
  ↓
generate_project_map()
  ↓
format_project_map()
  ↓
终端输出 Project Map
```

对应代码入口：

```text
main.py
```

---

## 当前设计边界

当前 v0 只做静态扫描和规则判断。

### 当前不会做

- 不读取整个代码内容做语义理解
- 不调用 LLM
- 不上传代码
- 不生成 Patch
- 不执行测试命令
- 不读取 Git diff
- 不分析错误日志
- 不生成接口文档
- 不追踪调用链

### 当前会做

- 扫描本地目录
- 忽略常见无关目录
- 识别关键文件
- 输出基础项目地图
- 提供候选启动命令

---

## 安全说明

RepoGuide 的长期设计原则之一是 **本地优先、安全默认**。

当前 v0 阶段：

- 不调用云端模型
- 不上传代码
- 不自动修改文件
- 不执行危险命令
- 不默认扫描真实 `.env` 文件

扫描器只允许以下环境模板文件进入分析：

```text
.env.example
.env.sample
.env.template
```

真实 `.env` 文件应避免进入项目地图输出。

---

## `.gitignore` 建议

建议 `.gitignore` 至少包含：

```gitignore
.venv/
venv/
__pycache__/
.pytest_cache/
.mypy_cache/
.idea/
.vscode/
dist/
build/
target/
*.pyc
```

如果后续生成 `.repoguide/` 本地缓存目录，也建议加入：

```gitignore
.repoguide/cache/
.repoguide/indexes/
.repoguide/overlays/
.repoguide/traces/
.repoguide/patches/
.repoguide/logs/
```

---

## 当前开发进度

```text
[x] 创建项目基础目录
[x] 实现本地目录扫描器
[x] 实现默认忽略规则
[x] 支持简化版 .gitignore
[x] 实现文件角色分类
[x] 实现项目类型候选识别
[x] 实现项目地图生成
[x] 实现项目地图文本格式化
[x] 添加 v0 pipeline 测试
[x] 编写 README
[ ] 正式 CLI 命令封装
[ ] RepoSnapshot / RepoFile 数据模型
[ ] RepoIndex 本地索引
[ ] 接口解析
[ ] 调用链分析
[ ] Git diff 诊断
[ ] 错误日志诊断
[ ] Patch 建议
[ ] API Server
[ ] Web UI
```

---

## 开发路线

RepoGuide 会按照从小到大的方式开发。

### v0：纯文本原型

目标：

- 验证输入输出
- 扫描本地项目
- 输出基础项目地图
- 不接 LLM
- 不做 Web
- 不做诊断

当前正在完成。

---

### v1：Core SDK

目标：

- 引入更稳定的数据模型
- 定义 `RepoSnapshot`
- 定义 `RepoFile`
- 定义 `ProjectMap`
- 将当前 dict 结构逐步规范化
- 为后续索引和检索打基础

---

### v2：CLI 工具

目标：

将当前 `python main.py .` 升级为正式 CLI 命令：

```bash
repoguide init
repoguide index .
repoguide map
repoguide ask "这个项目怎么启动？"
repoguide explain-api "/user/login"
repoguide explain-flow "用户登录流程"
```

v2 重点是本地开发者交互闭环。

---

### v3：代码结构解析

目标：

支持主流后端项目结构解析。

Java / Spring Boot：

- `@SpringBootApplication`
- `@RestController`
- `@Controller`
- `@RequestMapping`
- `@GetMapping`
- `@PostMapping`
- `@Service`
- `@Mapper`
- DTO / VO / Entity
- Mapper XML
- `application.yml`
- `pom.xml`

Python / FastAPI：

- `FastAPI()`
- `APIRouter`
- `@router.get`
- `@router.post`
- Pydantic Model
- `Depends`
- `requirements.txt`
- `pyproject.toml`
- pytest 测试文件

---

### v4：本地工作区诊断

目标：

引入 RepoGuide 的核心差异点：

```text
Base Repo Index + Workspace Overlay
```

支持：

```bash
repoguide diff
repoguide diagnose --log error.log
repoguide diagnose-diff --log error.log
```

能力包括：

- 读取 `git status`
- 读取 `git diff HEAD`
- 分析未提交修改
- 解析错误日志
- 定位最近修改中最可疑的区域
- 输出结构化诊断结果

---

### v5：LLM 问答增强

目标：

在已有结构化索引和检索结果基础上接入 LLM。

原则：

- 先检索证据，再生成回答
- 不把整个仓库塞给模型
- 回答必须尽量包含文件路径、函数名、行号或证据摘要
- 不输出无依据结论

---

### v6：Agent 编排

目标：

针对复杂任务做多节点编排。

例如：

```text
问题分类
  ↓
检索计划
  ↓
代码检索
  ↓
上下文构建
  ↓
回答生成
  ↓
证据校验
  ↓
最终输出
```

Agent 不是第一阶段目标，只作为后续复杂任务的增强层。

---

### v7：Patch 和测试闭环

目标：

支持从诊断结果生成修复建议。

流程：

```text
Diagnosis
  ↓
PatchSuggestion
  ↓
用户确认
  ↓
Apply Patch
  ↓
Run Test
  ↓
如果失败，回流 Diagnosis
```

原则：

- 不默认自动改代码
- Patch 必须可预览
- 用户确认后才应用
- 测试命令需要白名单
- 测试失败后继续分析

---

### v8：API Server

目标：

用 FastAPI 封装 Core SDK 能力。

API 只是 Core 的服务化包装，不应该让 Web 逻辑污染核心模块。

---

### v9：Web UI

目标：

在 Core 和 API 稳定后再做 Web 展示。

可能页面：

- 项目总览页
- 模块地图页
- 接口列表页
- 对话问答页
- 报错诊断页
- Patch 展示页
- Trace 执行链路页

Web 是展示层，不是项目核心。

---

## 设计原则

### 1. 本地优先

RepoGuide 优先分析本地工作区，而不是远程仓库。

真实开发问题通常来自：

- 未提交修改
- 新增文件
- 删除文件
- 本地配置
- 当前错误日志
- 当前测试结果
- 当前 git diff

---

### 2. 结构化索引优先

RepoGuide 不应该一开始就把整个项目丢给 LLM。

正确顺序是：

```text
扫描
  ↓
分类
  ↓
结构化索引
  ↓
检索相关证据
  ↓
必要时再调用 LLM
```

---

### 3. 证据优先

后续所有回答都应该尽量带证据：

- 文件路径
- 类名
- 函数名
- 行号范围
- 代码片段摘要
- 配置来源
- 日志来源
- diff 来源

---

### 4. Core + CLI 优先

RepoGuide 先做核心能力和 CLI，不提前做 Web。

原因：

- 问题发生在本地工作区
- CLI 更贴近开发者工作流
- Web 容易提前诱导项目变成展示壳
- Core 稳定后，API 和 Web 才有价值

---

### 5. 安全默认

RepoGuide 不应该默认做高风险动作：

- 不默认上传整个仓库
- 不默认读取敏感配置
- 不默认自动改代码
- 不默认执行危险命令
- Patch 必须人工确认

---

## 后续计划

近期建议优先做：

1. 完善 v0 测试样例
2. 增加更多 sample 项目测试
3. 将当前 dict 结构演进为数据模型
4. 增加 `RepoSnapshot` 和 `RepoFile`
5. 把 `main.py` 改造成更正式的 CLI 雏形
6. 逐步实现 `.repoguide/` 本地目录结构

暂时不要做：

- Web
- LangGraph 编排
- Patch 自动修复
- 复杂向量数据库
- 大规模 Agent 工作流

---

## 适合的第一阶段提交信息

如果当前 v0 功能和测试已经完成，可以提交：

```bash
git add .
git commit -m "Implement v0 project scanner and mapper"
```

---

## 项目总结

RepoGuide 当前是一个 v0 原型，已经完成本地仓库扫描、文件分类、项目类型候选识别和项目地图生成。

它的长期目标是成为一个面向项目交接和本地开发诊断的代码仓库理解 Agent：

- 帮新人快速理解陌生项目
- 帮开发者定位接口和调用链
- 帮用户结合本地 diff 和错误日志诊断问题
- 帮用户生成可审查的 Patch 建议
- 帮用户通过测试验证修复结果

当前阶段只做最小可靠基础，不提前扩大范围。