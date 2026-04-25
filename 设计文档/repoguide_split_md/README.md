# RepoGuide 工程设计文档说明

本目录由原始设计文档拆分而来。每个 Markdown 文件对应 RepoGuide 项目的一个设计主题，方便后续按模块继续补充、修改或让 AI 分阶段生成更细的工程文档。

RepoGuide 的整体定位是：**面向项目交接与本地开发诊断的代码仓库理解 Agent**。项目设计遵循三个核心原则：

1. **先 Core SDK 与 CLI，后 API，再到 Web**。
2. **本地工作区优先**，需要理解未提交修改、错误日志和测试结果。
3. **回答必须可溯源**，输出应尽量带文件路径、符号、行号和证据说明。

## 文件说明

| 文件 | 简单介绍 | 适合什么时候看 |
|---|---|---|
| [01_project_overview.md](./01_project_overview.md) | 项目总览，说明 RepoGuide 要解决什么问题、面向哪些用户、核心场景是什么，以及它和普通代码 RAG、Copilot、Cursor 类工具的区别。 | 最先阅读，用来确认项目方向和边界。 |
| [02_user_scenarios.md](./02_user_scenarios.md) | 用户场景设计，围绕新人接手项目、生成交接文档、解释接口、追踪功能调用链、本地报错诊断和 patch 验证展开。 | 想确认产品到底服务哪些真实需求时阅读。 |
| [03_architecture.md](./03_architecture.md) | 总体架构设计，定义 Core SDK、CLI、Agent Orchestrator、Local Runtime、API Server、Web UI 等层次，以及核心数据流。 | 开始做工程架构、模块拆分前阅读。 |
| [04_development_roadmap.md](./04_development_roadmap.md) | 开发路线图，从 v0 文本原型到 v9 Web UI，按阶段说明每一版要做什么、不做什么、如何验收。 | 制定开发计划、安排优先级时阅读。 |
| [05_core_sdk_design.md](./05_core_sdk_design.md) | Core SDK 设计，说明核心目录结构、顶层 Facade、扫描器、索引器、检索器、诊断器、patch、测试、trace 等接口边界。 | 准备创建项目目录和核心类时阅读。 |
| [06_data_model_design.md](./06_data_model_design.md) | 数据模型设计，定义 RepoSnapshot、RepoFile、CodeSymbol、ApiEndpoint、RepoIndex、WorkspaceOverlay、Diagnosis、PatchSuggestion、TraceRun 等核心对象。 | 设计 Pydantic model、数据库表或内部数据结构时阅读。 |
| [07_cli_design.md](./07_cli_design.md) | CLI 设计，定义 `repoguide init/index/map/ask/explain-api/diagnose/suggest-fix/test/trace` 等命令及输出格式。 | 准备用 Typer 或 Click 写命令行工具时阅读。 |
| [08_indexing_and_parsing_design.md](./08_indexing_and_parsing_design.md) | 索引与解析设计，说明如何解析 Java/Spring Boot、Python/FastAPI、README、配置、SQL、测试文件，并构建符号、API 和调用关系。 | 实现代码扫描、语言识别、AST/Tree-sitter 解析时阅读。 |
| [09_retrieval_and_context_design.md](./09_retrieval_and_context_design.md) | 检索与上下文设计，强调混合检索、证据优先和上下文预算控制，而不是简单向量搜索。 | 实现 ask、explain-api、diagnose 等功能的召回和上下文拼装时阅读。 |
| [10_agent_workflow_design.md](./10_agent_workflow_design.md) | Agent 工作流设计，把项目问答、接口解释、功能调用链、报错诊断、patch 建议拆成可 trace 的节点。 | 准备用 LangGraph 或自研流程编排时阅读。 |
| [11_workspace_overlay_design.md](./11_workspace_overlay_design.md) | Workspace Overlay 设计，说明如何把 git diff、未提交文件、错误日志、测试结果叠加到 Base Repo Index 上进行本地诊断。 | 做本地 bug 诊断、diff 分析、日志关联时重点阅读。 |
| [12_diagnosis_design.md](./12_diagnosis_design.md) | 诊断能力设计，覆盖 Java 和 Python 常见错误类型，并定义日志解析、栈定位、diff 关联、根因排序和修复建议输出。 | 实现 `diagnose` 和 `diagnose-diff` 时阅读。 |
| [13_patch_and_test_design.md](./13_patch_and_test_design.md) | Patch 与测试闭环设计，说明 patch 不能默认自动应用，必须有风险等级、回滚方案、测试建议和人工确认。 | 实现修复建议、补丁预览、测试执行和失败回流时阅读。 |
| [14_storage_and_trace_design.md](./14_storage_and_trace_design.md) | 存储与 Trace 设计，定义 `.repoguide/` 目录、索引存储、overlay 存储、patch 存储和每次执行的 trace 记录。 | 做本地持久化、运行记录、调试审计和后续可视化时阅读。 |
| [15_api_server_design.md](./15_api_server_design.md) | API Server 设计，说明后期如何用 FastAPI 把 Core SDK 能力包装成 REST API，并强调 API 只是薄封装。 | Core 和 CLI 稳定后，准备服务化时阅读。 |
| [16_web_ui_later_design.md](./16_web_ui_later_design.md) | Web UI 后置设计，规划项目总览页、模块地图页、接口列表页、问答页、诊断页、Patch 页和 Trace 页。 | 后期准备做前端展示和演示页面时阅读。 |
| [17_evaluation_design.md](./17_evaluation_design.md) | 评测体系设计，定义项目地图准确率、API 抽取准确率、调用链准确率、诊断 Top-K 命中率、Patch 成功率等指标。 | 想证明项目效果、做实验报告或优化迭代时阅读。 |
| [18_security_and_privacy_design.md](./18_security_and_privacy_design.md) | 安全与隐私设计，强调本地代码默认不出端、上下文最小化、敏感信息脱敏、危险命令限制、patch 和测试需要确认。 | 做企业可用性、安全边界和权限控制时阅读。 |
| [19_resume_packaging.md](./19_resume_packaging.md) | 简历包装设计，给出 RepoGuide 在实习简历中的项目背景、技术栈和项目经历写法。 | 项目做出阶段成果后，准备写简历或面试讲述时阅读。 |
| [20_final_summary.md](./20_final_summary.md) | 最终总结，浓缩 RepoGuide 的核心价值、推荐开发顺序、可延后功能、简历亮点和主要风险点。 | 快速回顾整体方案，或给别人介绍项目时阅读。 |

## 推荐阅读顺序

### 只想快速了解项目

1. [01_project_overview.md](./01_project_overview.md)
2. [02_user_scenarios.md](./02_user_scenarios.md)
3. [20_final_summary.md](./20_final_summary.md)

### 准备正式开发

1. [03_architecture.md](./03_architecture.md)
2. [04_development_roadmap.md](./04_development_roadmap.md)
3. [05_core_sdk_design.md](./05_core_sdk_design.md)
4. [06_data_model_design.md](./06_data_model_design.md)
5. [07_cli_design.md](./07_cli_design.md)

### 准备实现核心能力

1. [08_indexing_and_parsing_design.md](./08_indexing_and_parsing_design.md)
2. [09_retrieval_and_context_design.md](./09_retrieval_and_context_design.md)
3. [10_agent_workflow_design.md](./10_agent_workflow_design.md)
4. [11_workspace_overlay_design.md](./11_workspace_overlay_design.md)
5. [12_diagnosis_design.md](./12_diagnosis_design.md)

### 准备做增强功能

1. [13_patch_and_test_design.md](./13_patch_and_test_design.md)
2. [14_storage_and_trace_design.md](./14_storage_and_trace_design.md)
3. [15_api_server_design.md](./15_api_server_design.md)
4. [16_web_ui_later_design.md](./16_web_ui_later_design.md)

### 准备展示、评测或写简历

1. [17_evaluation_design.md](./17_evaluation_design.md)
2. [18_security_and_privacy_design.md](./18_security_and_privacy_design.md)
3. [19_resume_packaging.md](./19_resume_packaging.md)
4. [20_final_summary.md](./20_final_summary.md)

## 开发优先级建议

建议先按以下顺序推进：

```text
v0 文本原型
→ v1 Core SDK
→ v2 CLI
→ v3 代码结构解析
→ v4 Workspace Overlay + 诊断
→ v5 LLM 证据化问答
→ v6 Agent 编排
→ v7 Patch + Test
→ v8 API Server
→ v9 Web UI
```

前期不要急着做 Web，也不要一开始就堆复杂 Agent。RepoGuide 的核心竞争力应先落在：

- 本地仓库扫描；
- 结构化索引；
- 接口和调用链理解；
- git diff 与日志联合诊断；
- 带证据的回答；
- 可 trace 的工程流程。

## 项目一句话介绍

**RepoGuide 是一个本地优先的代码仓库理解与诊断工具，目标是帮助开发者快速接手陌生项目，并在本地修改出错时结合仓库结构、git diff、错误日志和测试结果定位问题。**
