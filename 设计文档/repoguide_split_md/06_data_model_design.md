# 06_data_model_design.md

### 文档目的

定义系统统一的数据模型，让扫描、解析、检索、诊断、patch 与 trace 使用同一套可组合的数据结构。

### 核心模型总览

| 模型 | 为什么需要 | 主要使用流程 |
|---|---|---|
| RepoSnapshot | 表示一次扫描得到的仓库静态快照 | 扫描、初始索引 |
| RepoFile | 表示单文件的结构化元信息 | 分类、解析、检索 |
| CodeSymbol | 表示类、函数、方法、常量等符号 | 符号索引、调用关系 |
| ApiEndpoint | 表示接口定义 | 接口解释、API 列表 |
| CallChain | 表示从入口到下游的链路 | 流程解释、诊断 |
| RepoIndex | 表示仓库级结构化索引 | 所有核心流程 |
| WorkspaceOverlay | 表示本地增量上下文 | diff 诊断、patch、测试 |
| Diagnosis | 表示一次错误分析结果 | 诊断、patch |
| PatchSuggestion | 表示一次修复建议 | patch 生成与应用 |
| TraceRun | 表示一次完整执行轨迹 | 调试、回溯、评测 |

### RepoSnapshot

#### 建议字段

- `repo_id`
- `root_path`
- `project_name`
- `detected_languages`
- `framework_type`
- `files`
- `config_files`
- `entrypoints`
- `test_files`
- `created_at`

#### 作用

RepoSnapshot 是最早期的“事实层”。它不关心复杂推理，只回答：当前仓库有什么、入口可能在哪里、配置和测试在哪里。

### RepoFile

#### 建议字段

- `path`
- `language`
- `role`
- `size`
- `hash`
- `content_summary`
- `symbols`
- `imports`
- `exports`

#### 作用

RepoFile 是所有高层能力的载体。文件角色的准确性会直接影响检索和调用链质量。

#### 推荐 role 枚举

- `entrypoint`
- `controller`
- `router`
- `service`
- `repository`
- `mapper`
- `dto`
- `vo`
- `entity`
- `config`
- `test`
- `migration`
- `sql`
- `readme`
- `build_manifest`
- `infra`
- `unknown`

### CodeSymbol

#### 建议字段

- `name`
- `type`
- `file_path`
- `start_line`
- `end_line`
- `signature`
- `decorators_or_annotations`
- `docstring_or_comment`
- `parent_symbol`

#### 作用

CodeSymbol 让系统不必总在“整文件”粒度工作，而能在类、方法、函数和模型粒度理解代码。

### ApiEndpoint

#### 建议字段

- `method`
- `path`
- `controller_file`
- `handler_name`
- `request_params`
- `request_body`
- `response_type`
- `auth_required`
- `service_calls`
- `mapper_calls`
- `related_tables`

#### 作用

ApiEndpoint 是接口解释、接口列表页、交接文档与故障排查的重要枢纽。

### CallChain

#### 建议字段

- `chain_id`
- `entrypoint`
- `nodes`
- `edges`
- `confidence`
- `missing_links`

#### 作用

CallChain 不要求 100% 完整，但要求对“链路已知部分”和“链路缺失部分”做明确表达。

### RepoIndex

#### 建议字段

- `repo_id`
- `file_index`
- `symbol_index`
- `api_index`
- `dependency_graph`
- `call_graph`
- `vector_index`
- `metadata`

#### 作用

RepoIndex 是系统真正的“仓库知识底座”。所有问答、解释、诊断、patch 都建立在它之上。

### WorkspaceOverlay

#### 建议字段

- `repo_id`
- `git_status`
- `changed_files`
- `added_files`
- `deleted_files`
- `untracked_files`
- `diff_summary`
- `raw_diff`
- `error_logs`
- `test_results`
- `generated_at`

#### 作用

WorkspaceOverlay 让系统知道“当前本地真实状态发生了什么变化”，这是 RepoGuide 区别于普通仓库问答系统的关键。

### Diagnosis

#### 建议字段

- `diagnosis_id`
- `error_type`
- `error_location`
- `suspected_files`
- `suspected_changes`
- `root_cause_hypotheses`
- `evidence`
- `recommended_fix`
- `confidence`
- `next_actions`

#### 作用

Diagnosis 是从“发现问题”到“建议修复”的中间层，它应该结构化、可排序、可审查。

### PatchSuggestion

#### 建议字段

- `patch_id`
- `diagnosis_id`
- `target_files`
- `diff_text`
- `explanation`
- `risk_level`
- `test_command`
- `rollback_plan`

#### 作用

PatchSuggestion 使 patch 具备治理属性，不再是一段随意改动，而是一份带解释、测试建议和回滚方案的可审阅产物。

### TraceRun

#### 建议字段

- `run_id`
- `command`
- `user_input`
- `steps`
- `retrieved_context`
- `llm_calls`
- `outputs`
- `errors`
- `started_at`
- `ended_at`

#### 作用

TraceRun 是调试系统本身、做评测、做可视化与写简历的基础。

### 设计结论

这些模型共同形成了三层抽象：

1. **事实层**：RepoSnapshot、RepoFile、CodeSymbol、ApiEndpoint、RepoIndex  
2. **增量层**：WorkspaceOverlay  
3. **推理与动作层**：Diagnosis、PatchSuggestion、TraceRun  

这样才能保证 RepoGuide 不是简单对话系统，而是带结构与状态的工程系统。

---
