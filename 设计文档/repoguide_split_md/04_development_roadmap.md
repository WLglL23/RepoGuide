# 04_development_roadmap.md

### 文档目的

给出从原型到产品化的渐进式路线，避免一开始设计过大、过重、过分依赖复杂 Agent 框架。

### 分阶段路线总览

| 版本 | 目标 | 输入 | 输出 | 需要完成的模块 | 不做什么 | 验收标准 |
|---|---|---|---|---|---|---|
| v0 纯文本原型 | 验证 I/O 结构 | 本地仓库路径 | 文件清单、目录树、手工规则项目摘要 | 扫描器、基础分类 | 不接 LLM、不做 patch | 能稳定列出目录、入口、配置候选 |
| v1 Core SDK | 完成核心扫描与基础索引 | 本地项目路径 | RepoSnapshot、RepoIndex、Project Map | Scanner、LanguageDetector、FileClassifier、Indexer | 不做诊断、不做 Web | 可以输出项目地图与关键文件 |
| v2 CLI 工具 | 建立本地交互闭环 | 仓库路径、用户命令 | `map / ask / explain-api / explain-flow` | CLI、ProjectMapper、Retriever、ContextBuilder 初版 | 不做 diff 诊断 | 能通过 CLI 完成结构理解 |
| v3 代码结构解析 | 支持 Java/Python 主流框架 | Java / Python 项目 | API 索引、符号索引、调用图初版 | CodeParser、ApiExtractor、DependencyAnalyzer、CallChainTracer | 不做 patch | 能解释常见接口与基础调用链 |
| v4 本地工作区诊断 | 支持 diff 与日志联合诊断 | git diff、error log、test log | Diagnosis | WorkspaceOverlayBuilder、GitDiffAnalyzer、LogParser、DiagnosisEngine | 不自动改代码 | 能定位最近修改引起的常见错误 |
| v5 LLM 问答增强 | 提升回答质量与可解释性 | 用户问题 + 检索结果 | 可溯源回答 | AnswerGenerator、EvidenceVerifier、LLM client | 不做复杂 multi-agent | 回答必须包含证据引用 |
| v6 Agent 编排 | 处理复杂任务和多步诊断 | 复杂问题、上下文 | 多节点 trace、任务型输出 | Orchestrator、Task Router、Planning、Verification | 不做大规模平台化 | 多步任务成功率明显提升 |
| v7 Patch 和测试 | 形成修复验证闭环 | Diagnosis、代码上下文 | PatchSuggestion、测试结果 | PatchPlanner、PatchGenerator、TestRunner | 不默认自动 apply | 用户确认后可应用 patch 并回传测试结果 |
| v8 FastAPI 服务化 | 稳定提供 API | repo_id、session、请求体 | REST API | API layer、Auth、Session、Trace endpoints | 不做复杂业务前端 | API 与 CLI 结果一致 |
| v9 Web UI | 可视化项目理解与调试链路 | API 数据 | 项目页、接口页、trace 页 | Web 层 | 不把核心逻辑置于前端 | 页面仅消费 API，不侵入内核 |

### v0：纯文本原型

#### 目标

先验证“用户真正需要什么输出”，而不是先追求复杂解析。

#### 推荐能力

- 扫描目录。
- 过滤忽略目录。
- 识别 README、配置、入口文件。
- 输出目录树与项目摘要。
- 基于规则给出“启动候选命令”和“关键文件列表”。

#### 验收标准

- 对 3 到 5 个典型仓库能给出可读的项目概览。
- 输出结果格式稳定。
- 不依赖 LLM。

### v1：Core SDK

#### 目标

建立所有后续功能复用的内核。

#### 要完成的事

- 定义 RepoSnapshot / RepoFile / RepoIndex 等核心模型。
- 落地扫描、分类、持久化。
- 实现项目地图生成。

#### 验收标准

- 输入仓库路径，能生成结构化索引文件。
- 可在二次调用时复用索引而无需全量重扫。

### v2：CLI 工具

#### 目标

用最贴近开发者工作方式的形式交付能力。

#### 命令范围

- `repoguide init`
- `repoguide index .`
- `repoguide map`
- `repoguide ask "..."`
- `repoguide explain-api "/xxx"`
- `repoguide explain-flow "登录流程"`

#### 验收标准

- 命令能串起来形成最小工作流。
- 每个输出都有来源引用。

### v3：代码结构解析

#### 目标

让输出不再依赖简单规则，而具备真实“理解”仓库的能力。

#### 要完成的事

- 支持 Java / Spring Boot 注解解析。
- 支持 Python / FastAPI 路由解析。
- 支持 DTO / VO / Entity / Pydantic Model 抽取。
- 支持 Service / Mapper / SQL 关联。

#### 验收标准

- 对典型 Spring Boot / FastAPI 项目，接口识别准确率达到可用水平。
- 调用链至少能覆盖核心 happy path。

### v4：本地工作区诊断

#### 目标

把 RepoGuide 从“理解工具”进化为“开发诊断工具”。

#### 命令

- `repoguide diff`
- `repoguide diagnose --log error.log`
- `repoguide diagnose-diff --log error.log`

#### 核心能力

- Base Repo Index + Workspace Overlay。
- diff 分析与行级可疑区域提取。
- 日志解析与栈定位。
- 根因假设排序。

#### 验收标准

- 能在人工注入 bug 的样本中，给出可信的 Top-3 根因。
- 输出中能明确区分日志证据、diff 证据与推理建议。

### v5：LLM 问答增强

#### 目标

利用 LLM 组织自然语言解释，但不允许牺牲证据链。

#### 核心原则

- 规则和索引先召回证据。
- LLM 负责总结、解释、归纳和补全缺失叙述。
- 不能无依据回答。
- 回答必须附带文件路径、符号与行号。

### v6：Agent 编排

#### 目标

处理复杂任务，例如“先理解接口，再定位报错，再给 patch 建议”。

#### 设计要求

- 编排是增强层，而不是前置依赖。
- 只有在多步问题上，才启用复杂规划。
- 所有节点必须可 trace。

### v7：Patch 和测试

#### 目标

形成“诊断—建议—验证”的工程闭环。

#### 验收标准

- 能生成 patch 草案。
- 用户确认后应用。
- 测试执行受控、可回滚、可追踪。
- 测试失败可自动回流诊断。

### v8：FastAPI 服务化

#### 目标

为后续 Web 和集成使用提供服务能力。

#### 核心要求

- API 只是封装 Core SDK。
- 不能把业务逻辑写死在接口处理层。

### v9：Web UI

#### 目标

提升可视化体验与结果展示。

#### 结论

Web 不是产品成立的前提，而是**当内核稳定后，用于放大可见性和演示价值**。

---
