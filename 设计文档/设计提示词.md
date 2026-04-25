你现在是一名资深 AI 工程架构师、后端架构师、Agent 系统设计专家和开发者工具产品经理。请帮我完整设计一个名为 **RepoGuide** 的工程项目。

## 一、项目定位

项目名称：

**RepoGuide：面向项目交接的代码仓库理解与诊断 Agent**

项目目标：

RepoGuide 不是普通的 RAG 问答系统，也不是单纯的代码搜索工具，而是一个面向开发者接手陌生项目、项目交接、新人上手、接口理解、调用链分析、本地报错诊断和后续 Patch 修复的代码仓库理解 Agent。

用户在本地项目目录中使用 RepoGuide，可以询问：

- 这个项目怎么启动？
- 这个项目有哪些核心模块？
- 某个接口的请求参数和返回值是什么？
- 登录流程、打卡流程、订单流程等业务功能是怎么运行的？
- 某个 Controller 到 Service、Mapper、数据库或 Redis 的调用链是怎样的？
- 我本地改了代码后出现报错，可能是哪里引起的？
- 根据报错日志和 git diff，应该怎么修？
- 是否可以生成修复建议、diff patch 或测试建议？

核心价值：

把一个陌生代码仓库转化成一个可交互、可追踪、可诊断的项目知识系统，降低新人接手项目和本地排查 bug 的成本。

## 二、重要设计原则

请严格按照以下原则设计：

1. **先本地 CLI / SDK，最后再考虑 Web**
   - 不要一开始设计 Web 页面。
   - 项目应先从核心分析库开始，再做 CLI，再做诊断，再做 Patch，再做 API，最后再做 Web。
   - Web 只是最终展示层，不应该影响核心架构。
2. **先工程设计文档，不生成代码**
   - 本次输出只需要详细设计文档。
   - 不要直接生成任何代码实现。
   - 可以给出接口签名、数据结构字段、模块职责、伪流程，但不要写具体业务代码。
3. **不要堆工具名**
   - 不要把项目设计成“LangChain + LangGraph + RAG + Docker + FastAPI”的工具堆砌。
   - 要围绕真实开发场景设计：项目交接、代码仓库理解、接口分析、调用链追踪、本地修改诊断、错误日志分析、Patch 建议、测试验证。
4. **本地工作区优先**
   - RepoGuide 不应该只能分析远程仓库。
   - 远程仓库只是项目基线。
   - 真正重要的是当前本地工作区，包括：
     - 已提交代码
     - 未提交修改
     - 新增文件
     - 删除文件
     - 当前错误日志
     - 当前测试结果
     - 当前 git diff
5. **Base Repo Index + Workspace Overlay 双层上下文**
   - Base Repo Index 表示稳定版本的项目结构索引。
   - Workspace Overlay 表示当前本地未提交修改、错误日志、测试结果等增量上下文。
   - 回答问题和诊断错误时，应综合：
     - Base Repo Index
     - Workspace Overlay
     - 用户问题
     - 报错日志
     - git diff
     - 相关文件内容
6. **回答必须可溯源**
   - 所有项目问答、接口解释、调用链解释、报错诊断都必须尽量附带来源：
     - 文件路径
     - 类名
     - 函数名
     - 行号范围
     - 相关代码片段摘要
   - 不允许输出没有依据的泛泛回答。
7. **从小到大逐层扩展**
   - RepoGuide v1：本地代码仓库结构分析 CLI
   - RepoGuide v2：项目问答、接口解释、调用链解释
   - RepoGuide v3：本地 git diff + error log 诊断
   - RepoGuide v4：Patch 建议和测试验证
   - RepoGuide v5：FastAPI 服务化
   - RepoGuide v6：Web 可视化平台

## 三、请你输出的内容要求

请你按照正经工程项目设计流程，输出一套完整设计文档。不要写代码。请用 Markdown 组织。

你需要输出以下文档，每个文档都要有清晰标题、目的、内容、模块、流程、关键接口和设计理由。

------

# 需要输出的设计文档清单

## 01_project_overview.md

内容包括：

1. 项目背景
2. 项目要解决的问题
3. 目标用户
4. 核心使用场景
5. 项目边界
6. 不做什么
7. RepoGuide 和普通 RAG / 代码搜索工具 / Cursor / Copilot 的区别
8. 项目最终能力图
9. MVP 版本定义
10. 项目亮点总结

重点说明：

RepoGuide 的核心不是“问答”，而是“代码仓库理解 + 本地工作区诊断 + 项目交接”。

------

## 02_user_scenarios.md

请详细设计应用场景。

至少包括：

### 场景一：新人接手陌生项目

用户问题示例：

- 这个项目怎么启动？
- 有哪些模块？
- 应该先看哪些文件？
- 配置文件在哪里？
- 依赖 MySQL、Redis、MQ 吗？

需要说明系统如何分析：

- README
- package / pom / pyproject / requirements
- application.yml
- Dockerfile
- 项目入口文件
- Controller / Router
- Service 层
- 数据库相关文件

### 场景二：项目交接文档生成

用户问题：

- 帮我生成这个项目的交接文档。
- 帮我生成新人上手路线。
- 帮我总结核心模块和接口。

输出应该包括：

- 项目概览
- 技术栈
- 启动方式
- 模块划分
- 关键接口
- 数据库依赖
- 中间件依赖
- 常见问题
- 推荐阅读路径

### 场景三：接口理解

用户问题：

- `/user/login` 这个接口是干什么的？
- 它需要哪些参数？
- 返回值是什么？
- 会调用哪些 Service？
- 会查哪些表？
- 什么情况下会返回 401 / 404 / 500？

系统需要支持：

- Controller / Router 解析
- DTO / RequestBody 解析
- Response VO 解析
- Service 调用链追踪
- Mapper / SQL 关联
- 鉴权逻辑判断

### 场景四：功能调用链解释

用户问题：

- 登录流程是怎么走的？
- 每日打卡功能怎么实现的？
- 问答列表为什么要批量查用户？
- 某个功能从接口到数据库经过哪些步骤？

系统输出：

- Controller → Service → Mapper → DB / Redis / 外部 API 的调用链
- 每一步对应文件、函数、作用
- 关键业务判断
- 可能的异常分支

### 场景五：本地修改后报错诊断

用户本地改了代码，还没有提交，也没有 push。

用户输入：

- 报错日志
- 或测试失败日志
- 或运行命令输出
- 或直接执行 `repoguide diagnose-diff`

系统需要读取：

- git status
- git diff HEAD
- 未提交文件
- 新增文件
- 删除文件
- 报错日志
- 相关代码文件
- 项目索引

系统输出：

- 异常类型
- 报错位置
- 可能原因
- 最近修改中最可疑的部分
- 相关调用链
- 修复建议
- 是否建议生成 Patch

### 场景六：Patch 建议和测试验证

系统不应该一开始就自动修改文件。

应该先支持：

- 生成修复建议
- 生成 diff patch
- 用户确认后 apply
- 运行测试
- 如果测试失败，读取失败日志继续分析

------

## 03_architecture.md

请设计总体架构。

必须包含：

1. 分层架构

建议层次：

- RepoGuide Core SDK
- RepoGuide CLI
- RepoGuide Agent Orchestrator
- RepoGuide Local Runtime
- RepoGuide API Server
- RepoGuide Web UI

1. 核心模块

建议模块：

- RepoScanner：扫描项目文件
- LanguageDetector：识别语言和项目类型
- FileClassifier：识别文件角色
- CodeParser：解析类、函数、接口、注解、import
- ApiExtractor：提取接口
- DependencyAnalyzer：分析依赖关系
- CallChainTracer：调用链追踪
- RepoIndexer：构建 Base Repo Index
- WorkspaceOverlayBuilder：构建本地增量上下文
- GitDiffAnalyzer：分析 git diff
- LogParser：解析错误日志
- Retriever：检索相关代码
- ContextBuilder：构建 LLM 上下文
- AnswerGenerator：生成可溯源回答
- DiagnosisEngine：诊断错误
- PatchPlanner：生成修复计划
- PatchGenerator：生成 diff patch
- TestRunner：运行测试
- TraceRecorder：记录执行过程

1. 数据流

至少画出以下流程：

- 项目索引流程
- 项目问答流程
- 接口解释流程
- 调用链追踪流程
- 本地 diff 诊断流程
- Patch 建议流程
- 测试验证流程

1. 设计取舍

说明为什么先做 Core + CLI，而不是先做 Web。

------

## 04_development_roadmap.md

请设计从小到大的开发路线。

要求分阶段：

### v0：纯文本原型

目标：

- 验证输入输出
- 不接 LLM 也可以
- 能扫描项目文件
- 能列出项目结构

### v1：Core SDK

目标：

- 完成项目扫描
- 文件分类
- 基础索引
- 项目 map 输出

### v2：CLI 工具

目标：

支持命令：

- `repoguide init`
- `repoguide index .`
- `repoguide map`
- `repoguide ask "..."`
- `repoguide explain-api "/xxx"`
- `repoguide explain-flow "登录流程"`

### v3：代码结构解析

目标：

- Java / Spring Boot 项目解析
- Python / FastAPI 项目解析
- Controller / Router 识别
- Service / Mapper 识别
- DTO / VO 解析
- 配置文件解析

### v4：本地工作区诊断

目标：

支持命令：

- `repoguide diff`
- `repoguide diagnose --log error.log`
- `repoguide diagnose-diff --log error.log`

核心：

- Base Repo Index + Workspace Overlay
- git diff 分析
- error log 定位
- 最近修改影响分析

### v5：LLM 问答增强

目标：

- 接入 LLM
- RAG 检索相关代码
- 生成可溯源回答
- 引用文件、函数、行号
- 不允许无依据回答

### v6：Agent 编排

目标：

- 针对复杂任务进行多节点编排
- 问题分类
- 上下文规划
- 检索
- 诊断
- 回答校验
- 输出最终答案

### v7：Patch 和测试

目标：

- 生成 Patch 建议
- 用户确认后应用
- 运行 pytest / mvn test / npm test
- 失败日志二次诊断

### v8：FastAPI 服务化

目标：

- 把 Core 能力封装为 API
- 支持 repo_id
- 支持 session
- 支持 trace
- 为 Web 做准备

### v9：Web UI

目标：

- 项目总览页
- 文件地图页
- 接口列表页
- 对话问答页
- 报错诊断页
- Patch 展示页
- Trace 页

请每个阶段都说明：

- 目标
- 输入
- 输出
- 需要完成的模块
- 不做什么
- 验收标准

------

## 05_core_sdk_design.md

请详细设计 Core SDK。

要求设计以下目录结构，但不要写代码：

```text
repoguide/
  core/
    scanner/
    parser/
    indexer/
    retriever/
    context/
    diagnosis/
    patch/
    testing/
    tracing/
  cli/
  api/
  storage/
  config/
  docs/
  tests/
```

请详细说明每个目录职责。

请设计核心类和接口，只写签名和说明，不写实现：

- RepoGuide
- RepoScanner
- RepoSnapshot
- RepoFile
- RepoIndexer
- RepoIndex
- RepoRetriever
- CodeReference
- ContextBuilder
- ProjectMapper
- ApiExplainer
- FlowExplainer
- WorkspaceOverlayBuilder
- GitDiffAnalyzer
- LogParser
- DiagnosisEngine
- PatchPlanner
- PatchGenerator
- TestRunner
- TraceRecorder

请说明：

- 每个类负责什么
- 输入是什么
- 输出是什么
- 和其他模块怎么交互
- 哪些属于核心稳定接口
- 哪些属于后续可替换实现

------

## 06_data_model_design.md

请设计核心数据模型。

至少包括：

### RepoSnapshot

字段示例：

- repo_id
- root_path
- project_name
- detected_languages
- framework_type
- files
- config_files
- entrypoints
- test_files
- created_at

### RepoFile

字段示例：

- path
- language
- role
- size
- hash
- content_summary
- symbols
- imports
- exports

### CodeSymbol

字段示例：

- name
- type
- file_path
- start_line
- end_line
- signature
- decorators / annotations
- docstring / comment
- parent_symbol

### ApiEndpoint

字段示例：

- method
- path
- controller_file
- handler_name
- request_params
- request_body
- response_type
- auth_required
- service_calls
- mapper_calls
- related_tables

### CallChain

字段示例：

- chain_id
- entrypoint
- nodes
- edges
- confidence
- missing_links

### RepoIndex

字段示例：

- repo_id
- file_index
- symbol_index
- api_index
- dependency_graph
- call_graph
- vector_index
- metadata

### WorkspaceOverlay

字段示例：

- repo_id
- git_status
- changed_files
- added_files
- deleted_files
- untracked_files
- diff_summary
- raw_diff
- error_logs
- test_results
- generated_at

### Diagnosis

字段示例：

- diagnosis_id
- error_type
- error_location
- suspected_files
- suspected_changes
- root_cause_hypotheses
- evidence
- recommended_fix
- confidence
- next_actions

### PatchSuggestion

字段示例：

- patch_id
- diagnosis_id
- target_files
- diff_text
- explanation
- risk_level
- test_command
- rollback_plan

### TraceRun

字段示例：

- run_id
- command
- user_input
- steps
- retrieved_context
- llm_calls
- outputs
- errors
- started_at
- ended_at

请说明每个模型为什么需要，在哪些流程中使用。

------

## 07_cli_design.md

请设计 CLI。

要求：

1. 设计 CLI 命令树
2. 每个命令的用途
3. 输入参数
4. 输出格式
5. 失败情况
6. 示例交互

必须包含命令：

```bash
repoguide init
repoguide index .
repoguide map
repoguide ask "这个项目怎么启动？"
repoguide explain-api "/user/login"
repoguide explain-flow "用户登录流程"
repoguide diff
repoguide diagnose --log error.log
repoguide diagnose-diff --log error.log
repoguide suggest-fix --diagnosis <id>
repoguide apply-patch <patch_id>
repoguide test
repoguide trace <run_id>
```

请说明 `.repoguide/` 本地目录结构：

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

请说明哪些文件可以提交，哪些应该加入 `.gitignore`。

------

## 08_indexing_and_parsing_design.md

请详细设计索引和解析。

要求分语言说明。

### Java / Spring Boot

需要识别：

- `@SpringBootApplication`
- `@RestController`
- `@Controller`
- `@RequestMapping`
- `@GetMapping`
- `@PostMapping`
- `@PutMapping`
- `@DeleteMapping`
- `@Service`
- `@Component`
- `@Repository`
- `@Mapper`
- `@Autowired`
- `@Resource`
- DTO / VO / Entity
- Mapper XML
- application.yml / application.properties
- pom.xml

### Python / FastAPI

需要识别：

- FastAPI app
- APIRouter
- `@router.get`
- `@router.post`
- Pydantic Model
- dependency injection
- requirements.txt
- pyproject.toml
- pytest tests

### 通用文件

需要识别：

- README
- Dockerfile
- docker-compose.yml
- .env.example
- SQL schema
- migration files
- test files
- config files

请说明：

- 如何判断文件角色
- 如何抽取符号
- 如何抽取 API
- 如何构建调用关系
- 如何处理大文件
- 如何处理忽略目录，例如 node_modules、target、dist、.git、venv、**pycache**
- 什么时候使用规则解析
- 什么时候使用 AST / Tree-sitter
- 什么时候使用向量检索

------

## 09_retrieval_and_context_design.md

请设计检索和上下文构建。

要求说明：

1. 检索不是只做向量搜索
2. 应该结合：
   - 关键词检索
   - 文件路径匹配
   - 符号匹配
   - API 路径匹配
   - 调用图邻居扩展
   - git diff 相关文件提升权重
   - error log 文件和行号强制召回
   - 语义向量检索
3. 不同问题类型使用不同检索策略

问题类型包括：

- 项目总览
- 启动方式
- 接口解释
- 功能流程
- 报错诊断
- 本地 diff 诊断
- Patch 生成
- 测试建议

1. ContextBuilder 的上下文预算策略

请说明：

- 不能把整个项目塞给 LLM
- 需要按优先级组装上下文
- 必须包含来源信息
- 大文件需要切片
- 重复内容需要去重
- 对本地 diff 和错误日志要提高优先级

------

## 10_agent_workflow_design.md

请设计 Agent 工作流。

要求不要泛泛写“用 Agent”，而是分任务设计流程。

### 项目问答流程

节点：

- QuestionClassifier
- RetrievalPlanner
- CodeRetriever
- ContextBuilder
- AnswerGenerator
- EvidenceVerifier
- FinalFormatter

### 接口解释流程

节点：

- RouteResolver
- ControllerParser
- DTOResolver
- ServiceChainTracer
- MapperResolver
- ApiDocGenerator
- EvidenceVerifier

### 功能调用链流程

节点：

- FeatureIntentParser
- EntryPointFinder
- CallGraphExpander
- RelatedFileRetriever
- FlowSummarizer
- MissingLinkReporter

### 报错诊断流程

节点：

- LogParser
- StackTraceLocator
- DiffAnalyzer
- RelatedCodeRetriever
- RootCauseAnalyzer
- FixAdvisor
- ConfidenceEstimator

### Patch 建议流程

节点：

- DiagnosisLoader
- FixPlanGenerator
- PatchGenerator
- PatchRiskChecker
- TestPlanGenerator
- HumanApprovalRequired

请说明：

- 每个节点输入输出
- 节点失败时怎么办
- 哪些节点可用规则实现
- 哪些节点需要 LLM
- 哪些节点需要人工确认
- 哪些步骤需要 Trace 记录

------

## 11_workspace_overlay_design.md

请重点设计 Workspace Overlay。

这是项目的核心亮点之一。

要求说明：

1. 为什么远程仓库不是唯一真实状态
2. 为什么本地工作区才是用户遇到 bug 时的真实状态
3. Base Repo Index 和 Workspace Overlay 的关系
4. 如何读取：
   - git status
   - git diff HEAD
   - staged diff
   - untracked files
   - deleted files
   - error logs
   - test results
5. 如何把 Overlay 注入检索和诊断：

- 最近修改文件优先
- 报错栈文件强制召回
- diff 修改行附近代码优先
- 新增文件也要纳入候选
- 删除文件可能造成 import / 调用失败

1. 如何输出诊断证据：

- 哪个错误来自日志
- 哪个怀疑点来自 diff
- 哪个背景来自项目索引
- 哪个建议来自推理

1. 示例流程：

用户改了 LoginInterceptor，本地出现 NullPointerException。RepoGuide 如何结合 git diff、错误日志、调用链判断问题来源？

------

## 12_diagnosis_design.md

请详细设计报错诊断能力。

要求支持：

1. Java 常见错误：
   - NullPointerException
   - BeanCreationException
   - NoSuchBeanDefinitionException
   - SQLSyntaxErrorException
   - DataIntegrityViolationException
   - ClassNotFoundException
   - Port already in use
   - Redis connection failed
   - JWT 鉴权失败
   - 事务未生效
2. Python 常见错误：
   - ModuleNotFoundError
   - ImportError
   - AttributeError
   - TypeError
   - KeyError
   - Pydantic validation error
   - FastAPI 422
   - database connection error
   - pytest failed assertion
3. 诊断流程：

- 错误类型识别
- 栈顶文件定位
- 用户代码和框架代码区分
- 最近修改相关性分析
- 调用链反查
- 配置文件检查
- 依赖检查
- 修复建议生成

1. 输出格式：

- 错误摘要
- 关键证据
- 可能原因排序
- 涉及文件
- 建议修复步骤
- 建议运行的测试
- 是否可以生成 Patch

------

## 13_patch_and_test_design.md

请设计 Patch 和测试能力。

要求：

1. Patch 不应默认自动应用
2. 应该先生成 PatchSuggestion
3. 用户确认后才能 apply
4. 每个 Patch 必须包含：
   - 修改文件
   - diff
   - 修改原因
   - 风险等级
   - 回滚方案
   - 建议测试命令
5. 测试执行支持：

- pytest
- mvn test
- npm test

1. TestRunner 应该支持：

- 超时控制
- 输出截断
- 错误日志保存
- 测试结果结构化
- 失败后回传 DiagnosisEngine

1. 失败闭环：

```text
Patch → Run Test → Fail → Parse Failure → Diagnose Again → Suggest New Patch
```

1. 安全边界：

- 不允许自动删除大量文件
- 不允许修改隐藏配置文件中的敏感信息
- 不允许执行危险命令
- 不允许无确认执行 destructive 操作

------

## 14_storage_and_trace_design.md

请设计本地存储和 Trace。

要求：

1. `.repoguide/` 目录设计
2. Index 存储格式
3. Overlay 存储格式
4. TraceRun 存储格式
5. Patch 存储格式
6. 日志存储格式

Trace 每次记录：

- 用户命令
- 用户输入
- 问题分类
- 检索到的文件
- 使用的上下文
- LLM 调用摘要
- 工具调用
- 输出结果
- 错误
- 耗时
- token 消耗，如有
- 最终状态

请说明 Trace 如何用于：

- Debug
- 简历展示
- 后续 Web 可视化
- Agent 评测

------

## 15_api_server_design.md

请设计后期 FastAPI 服务化接口，但强调这是后期阶段。

要求：

1. API 只是 Core SDK 的服务化包装
2. 不要让 Web 逻辑污染 Core
3. 设计 REST API：

```http
POST /repos/index
GET  /repos/{repo_id}/map
POST /repos/{repo_id}/ask
POST /repos/{repo_id}/explain-api
POST /repos/{repo_id}/explain-flow
POST /repos/{repo_id}/diagnose
POST /repos/{repo_id}/diagnose-diff
POST /repos/{repo_id}/suggest-fix
POST /repos/{repo_id}/apply-patch
POST /repos/{repo_id}/test
GET  /traces/{run_id}
```

1. 每个接口说明：
   - 请求参数
   - 响应结构
   - 错误码
   - 调用哪个 Core Service
   - 是否需要本地权限
   - 是否适合 Web 调用
2. 说明本地 CLI 和 API Server 的关系。

------

## 16_web_ui_later_design.md

请只设计后期 Web，不要展开成前端代码。

Web 页面包括：

1. 项目总览页
2. 模块地图页
3. 文件浏览页
4. 接口列表页
5. 对话问答页
6. 报错诊断页
7. Git diff 分析页
8. Patch 展示页
9. Trace 执行链路页

请说明：

- 每个页面展示什么
- 依赖哪些 API
- 不负责哪些核心逻辑
- 为什么 Web 应该最后做

------

## 17_evaluation_design.md

请设计评测体系。

要求：

1. 不要只说“效果不错”
2. 需要设计可量化指标

指标包括：

- Project Map Accuracy
- API Extraction Accuracy
- Call Chain Accuracy
- Retrieval Precision
- Answer Citation Coverage
- Diagnosis Top-1 Accuracy
- Diagnosis Top-3 Accuracy
- Patch Success Rate
- First-pass Patch Success Rate
- Test Pass Rate
- Average Token Cost
- Average Runtime
- User Confirmation Rate

1. 评测数据集设计：

- Java Spring Boot 示例项目
- Python FastAPI 示例项目
- 人工注入 bug
- 历史 bug
- 错误日志样本
- 接口问答样本
- 调用链问答样本

1. 每个评测样本包含：

- repo_id
- question / log / diff
- expected_files
- expected_symbols
- expected_answer_points
- expected_root_cause
- expected_patch, optional
- test_command, optional

1. 输出评测报告格式。

------

## 18_security_and_privacy_design.md

请设计安全和隐私边界。

要求说明：

1. 本地项目代码可能敏感
2. 不应默认上传整个仓库到云端
3. CLI 优先本地处理
4. 发送给 LLM 的上下文必须最小化
5. 支持脱敏：
   - API key
   - token
   - password
   - .env
   - database url
   - private key
6. 危险命令限制
7. Patch 应用需要确认
8. 测试执行需要命令白名单
9. Web 版本的权限边界

------

## 19_resume_packaging.md

请设计这个项目最后应该如何写进简历。

要求：

1. 给出项目标题
2. 给出项目背景
3. 给出技术栈
4. 给出 5 到 6 条高质量项目经历描述
5. 不要写成工具堆砌
6. 重点突出：
   - 本地工作区增量分析
   - 代码结构化索引
   - 接口和调用链理解
   - 报错日志诊断
   - Patch 和测试闭环
   - Trace 可观测
   - 评测体系

请给出一版适合实习生简历的写法。

------

## 20_final_summary.md

最后请总结：

1. RepoGuide 的核心价值
2. 最小可行版本应该先做什么
3. 哪些功能可以延后
4. 哪些功能是简历亮点
5. 推荐开发顺序
6. 推荐技术栈
7. 最大风险点
8. 如何避免做成普通 RAG 项目

## 四、输出格式要求

请严格按照以下格式输出：

```text
# RepoGuide 工程设计文档

## 01_project_overview.md
...

## 02_user_scenarios.md
...

## 03_architecture.md
...
```

每个文档要详细，但不要写具体代码实现。

可以写：

- 模块职责
- 类和接口签名
- 数据结构字段
- 流程图
- 伪流程
- 命令示例
- API 设计
- 验收标准

不要写：

- 完整 Python 代码
- 完整 FastAPI 实现
- 完整前端页面代码
- 具体 LangGraph 节点实现代码
- 大段可运行程序

## 五、技术栈建议

请基于以下方向设计，但可以提出合理替代方案：

- Python
- Typer / Click：CLI
- FastAPI：后期 API Server
- Tree-sitter：代码结构解析
- GitPython 或 subprocess git：git 状态和 diff 读取
- SQLite / DuckDB：本地结构化索引
- ChromaDB / FAISS：可选向量索引
- LangGraph：后期 Agent 工作流编排
- pytest / mvn test / npm test：测试执行
- Pydantic：数据模型
- Rich：CLI 美化输出

注意：这些是建议，不要把项目写成技术栈堆砌。设计时必须始终围绕 RepoGuide 的实际场景。

## 六、最终提醒

这个项目的核心不是：

“我做了一个代码 RAG 问答系统。”

而是：

“我设计了一个面向项目交接和本地开发诊断的代码仓库理解 Agent。它能够从项目结构、接口、调用链、配置、git diff 和错误日志中构建可溯源上下文，帮助开发者理解陌生项目，并在本地修改出错时定位原因、给出修复建议，最终扩展到 Patch 和测试闭环。”

请按照这个定位，完整输出工程设计文档。