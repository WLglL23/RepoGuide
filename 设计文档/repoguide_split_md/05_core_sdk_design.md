# 05_core_sdk_design.md

### 文档目的

定义 SDK 目录结构、核心类、接口边界以及稳定接口与可替换实现的划分。

### 建议目录结构

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

### 目录职责说明

| 目录 | 职责 |
|---|---|
| `core/scanner/` | 扫描仓库、识别文件、建立 RepoSnapshot |
| `core/parser/` | 做 AST / Tree-sitter / 规则解析，抽取符号、API、依赖 |
| `core/indexer/` | 构建 RepoIndex，生成图与检索索引 |
| `core/retriever/` | 混合检索入口，支持关键词 / 路径 / 符号 / 图邻居 / 向量 |
| `core/context/` | 上下文预算、切片拼装、证据格式化 |
| `core/diagnosis/` | 日志解析、diff 分析、根因推理、诊断输出 |
| `core/patch/` | 修复计划、patch 生成、风险检查 |
| `core/testing/` | 测试执行、失败解析、结果结构化 |
| `core/tracing/` | TraceRun、步骤记录、工具调用和审计 |
| `cli/` | 命令定义、参数解析、终端输出 |
| `api/` | 后期服务化包装层 |
| `storage/` | SQLite/DuckDB/FAISS/文件系统等存储实现 |
| `config/` | 配置模型、项目配置、运行策略 |
| `docs/` | 设计文档、用户手册、输出模板 |
| `tests/` | 核心单元测试、集成测试、评测样本 |

### 核心类与接口签名

以下只给接口签名与职责说明，不给实现代码。

```text
class RepoGuide:
    init_project(root_path, config) -> RepoHandle
    index(root_path, ref=None, full=False) -> RepoIndex
    map(repo_id, refresh=False) -> ProjectMap
    ask(repo_id, question, session=None, overlay=None) -> AnswerResult
    explain_api(repo_id, api_path, method=None, overlay=None) -> ApiExplanation
    explain_flow(repo_id, feature_query, overlay=None) -> FlowExplanation
    build_overlay(repo_id, log_paths=None, test_paths=None) -> WorkspaceOverlay
    diff(repo_id, ref="HEAD") -> DiffAnalysis
    diagnose(repo_id, log_input=None, overlay=None) -> Diagnosis
    diagnose_diff(repo_id, log_input=None, ref="HEAD") -> Diagnosis
    suggest_fix(repo_id, diagnosis_id) -> PatchSuggestion
    apply_patch(repo_id, patch_id, confirm=False) -> ApplyPatchResult
    test(repo_id, command=None, profile=None) -> TestRunResult
    trace(run_id) -> TraceRun

class RepoScanner:
    scan(root_path, ignore_rules=None) -> RepoSnapshot

class RepoSnapshot:
    from_scan(scan_result) -> RepoSnapshot

class RepoFile:
    summarize() -> FileSummary

class RepoIndexer:
    build(snapshot, parse_options=None) -> RepoIndex
    update(index, changed_files) -> RepoIndex

class RepoIndex:
    lookup_file(path) -> RepoFile
    lookup_symbol(name, fuzzy=False) -> list[CodeSymbol]
    lookup_api(path, method=None) -> list[ApiEndpoint]

class RepoRetriever:
    retrieve(query, repo_index, overlay=None, strategy=None, top_k=20) -> list[CodeReference]

class CodeReference:
    format_evidence() -> EvidenceItem

class ContextBuilder:
    build(task_type, question, references, overlay=None, budget=None) -> LLMContext

class ProjectMapper:
    generate(repo_index, overlay=None) -> ProjectMap

class ApiExplainer:
    explain(api_path, method, repo_index, overlay=None) -> ApiExplanation

class FlowExplainer:
    explain(feature_query, repo_index, overlay=None) -> FlowExplanation

class WorkspaceOverlayBuilder:
    build(repo_id, root_path, log_paths=None, test_paths=None) -> WorkspaceOverlay

class GitDiffAnalyzer:
    analyze(root_path, ref="HEAD", include_staged=True, include_untracked=True) -> DiffAnalysis

class LogParser:
    parse(log_input, language_hint=None) -> ParsedLog

class DiagnosisEngine:
    diagnose(repo_index, overlay, parsed_log=None, diff_analysis=None) -> Diagnosis

class PatchPlanner:
    plan(diagnosis, constraints=None) -> FixPlan

class PatchGenerator:
    generate(repo_index, overlay, fix_plan) -> PatchSuggestion

class TestRunner:
    detect_test_commands(repo_index) -> list[TestCommand]
    run(root_path, command=None, timeout=None) -> TestRunResult

class TraceRecorder:
    start(command, user_input, repo_id=None) -> TraceRun
    record_step(run_id, step_name, inputs=None, outputs=None, metadata=None) -> None
    finalize(run_id, status, outputs=None, error=None) -> TraceRun
```

### 核心类职责与交互关系

| 类 / 接口 | 负责什么 | 输入 | 输出 | 与谁交互 | 稳定性 |
|---|---|---|---|---|---|
| RepoGuide | 顶层 Facade，统一对外服务 | 用户命令、repo_id、问题 | 各类结构化结果 | 全部核心模块 | **核心稳定接口** |
| RepoScanner | 文件扫描与快照 | root_path | RepoSnapshot | FileClassifier | **核心稳定接口** |
| RepoIndexer | 索引构建与更新 | RepoSnapshot | RepoIndex | Parser、Extractor、Storage | **核心稳定接口** |
| RepoRetriever | 混合检索 | query、RepoIndex、Overlay | CodeReference 列表 | ContextBuilder、Diagnosis | **核心稳定接口** |
| ContextBuilder | 上下文预算与拼装 | 任务类型、证据、overlay | LLMContext | AnswerGenerator、Diagnosis | **核心稳定接口** |
| WorkspaceOverlayBuilder | 本地增量上下文 | git/log/test 输入 | WorkspaceOverlay | GitDiffAnalyzer、LogParser | **核心稳定接口** |
| DiagnosisEngine | 根因分析 | RepoIndex、Overlay、ParsedLog | Diagnosis | Retriever、PatchPlanner | **核心稳定接口** |
| PatchPlanner / PatchGenerator | 修复建议与 patch | Diagnosis | PatchSuggestion | TestRunner | **可演进接口** |
| TestRunner | 受控执行测试 | command、repo_path | TestRunResult | DiagnosisEngine、TraceRecorder | **可演进接口** |
| TraceRecorder | 可观测性 | 运行步骤 | TraceRun | 全部模块 | **核心稳定接口** |

### 哪些属于可替换实现

以下更适合做成抽象接口 + 插件实现：

- Parser 后端：Tree-sitter / 规则解析 / 语言专用解析器。
- 向量索引：FAISS / Chroma / 不启用向量检索。
- LLM Provider：本地模型 / 云 API。
- Storage：SQLite / DuckDB / 混合文件格式。
- Test 执行器：pytest / mvn / npm。
- Git Reader：subprocess git / GitPython。

### 设计结论

Core SDK 的关键不是类数量，而是**对真实场景的抽象稳定性**。顶层 `RepoGuide` 应保持清晰，底层解析器、索引器和生成器允许替换，但数据模型要尽量长期稳定。

---
