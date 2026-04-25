# 10_agent_workflow_design.md

### 文档目的

设计 Agent 工作流，但避免空泛地说“用 Agent”。每类任务都要拆成清晰节点，明确定义输入、输出、失败处理、Trace 记录点与人工确认点。

### 总体原则

- 能用规则做的优先用规则做。
- LLM 主要用于总结、归纳、补充叙述和 patch 草案生成。
- 每个节点都要能单独 trace。
- 高风险动作必须人工确认。

### 项目问答流程

#### 节点设计

| 节点 | 输入 | 输出 | 实现建议 | 失败时怎么办 |
|---|---|---|---|---|
| QuestionClassifier | 用户问题 | 问题类型 | 规则 + 小模型 | 回退为通用问答 |
| RetrievalPlanner | 问题类型、索引 | 检索策略 | 规则 | 使用默认混合检索 |
| CodeRetriever | 策略、RepoIndex、Overlay | CodeReferences | 检索引擎 | 若命中差，放宽策略 |
| ContextBuilder | 引用集、预算 | LLMContext | 规则 | 缩减背景槽位 |
| AnswerGenerator | 上下文 | 草案回答 | LLM | 若失败，输出结构化证据列表 |
| EvidenceVerifier | 草案、证据 | 校验后回答 | 规则 + LLM | 删去无依据结论 |
| FinalFormatter | 回答、引用 | CLI/API 输出 | 规则 | 输出简化格式 |

#### Trace 重点

- 问题分类结果
- 检索计划
- 召回文件与符号
- 被丢弃的证据
- 回答中的证据覆盖率

### 接口解释流程

#### 节点设计

| 节点 | 输入 | 输出 | 规则 / LLM |
|---|---|---|---|
| RouteResolver | API path + method | 精确 handler 候选 | 规则 |
| ControllerParser | handler | 控制器元信息 | 规则 |
| DTOResolver | 参数与 body 相关符号 | 请求结构 | 规则 |
| ServiceChainTracer | handler 下游调用 | 调用链草图 | 规则优先 |
| MapperResolver | service / mapper / SQL | 表与查询关系 | 规则优先 |
| ApiDocGenerator | 结构化信息 | 自然语言接口文档 | LLM |
| EvidenceVerifier | 文档草案 | 证据化接口说明 | 规则 |

#### 失败策略

- 若路径匹配不到，改用模糊路径匹配。
- 若调用链不完整，明确标注“以下链路为部分结果”。
- 若请求体模型推断不完整，输出字段来源与不确定性说明。

### 功能调用链流程

#### 节点设计

| 节点 | 输入 | 输出 | 规则 / LLM |
|---|---|---|---|
| FeatureIntentParser | 功能描述 | 关键词、候选模块 | 规则 + LLM |
| EntryPointFinder | 关键词、API 索引 | 入口点候选 | 规则 |
| CallGraphExpander | 入口点 | 调用图扩展结果 | 规则 |
| RelatedFileRetriever | 图节点 | 文件与配置证据 | 规则 |
| FlowSummarizer | 图与证据 | 流程解释 | LLM |
| MissingLinkReporter | 不完整图 | 缺口说明 | 规则 |

#### 失败策略

- 若找不到入口点，先返回“最相近的模块和接口”。
- 若图断裂，输出缺失点，不伪造链路。

### 报错诊断流程

#### 节点设计

| 节点 | 输入 | 输出 | 规则 / LLM |
|---|---|---|---|
| LogParser | error log | ParsedLog | 规则 |
| StackTraceLocator | ParsedLog | 关键文件、行号、用户代码栈 | 规则 |
| DiffAnalyzer | git diff | 可疑变更区域 | 规则 |
| RelatedCodeRetriever | 栈、diff、RepoIndex | 相关代码证据 | 规则 |
| RootCauseAnalyzer | 证据集 | 根因假设排序 | 规则 + LLM |
| FixAdvisor | 根因结果 | 修复建议 | LLM |
| ConfidenceEstimator | 证据覆盖度 | confidence | 规则 |

#### 失败策略

- 无日志时，退化为仅 diff 诊断。
- 无 diff 时，做日志 + Base Repo Index 诊断。
- 若 stack trace 全是框架代码，则回溯到最近用户代码帧与入口链路。

### Patch 建议流程

#### 节点设计

| 节点 | 输入 | 输出 | 人工确认 |
|---|---|---|---|
| DiagnosisLoader | diagnosis_id | Diagnosis | 否 |
| FixPlanGenerator | Diagnosis | FixPlan | 否 |
| PatchGenerator | FixPlan + Code Context | PatchSuggestion | 否 |
| PatchRiskChecker | PatchSuggestion | 风险分级 | 否 |
| TestPlanGenerator | PatchSuggestion | 建议测试方案 | 否 |
| HumanApprovalRequired | PatchSuggestion | apply / reject | **是** |

### 哪些节点需要人工确认

必须人工确认的步骤：

- apply patch
- 执行非白名单测试命令
- 覆盖配置文件
- 多文件高风险 patch
- 可能破坏环境的命令执行

### 哪些节点必须记录 Trace

几乎所有节点都建议记录，但最关键的是：

- 检索计划
- 证据集合
- 诊断假设排序
- patch 风险分级
- 测试结果
- 最终输出与失败原因

### 工作流设计结论

RepoGuide 的 Agent 不应追求炫技式自治，而应成为一种**可拆解、可 trace、可审计的工程流程编排器**。

---
