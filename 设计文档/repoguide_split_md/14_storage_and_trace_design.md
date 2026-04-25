# 14_storage_and_trace_design.md

### 文档目的

设计本地存储格式和 Trace 体系，为调试、审计、评测、Web 展示和简历包装奠定基础。

### `.repoguide/` 目录设计

在 CLI 文档基础上，这里进一步细化存储结构：

```text
.repoguide/
  config.yml
  indexes/
    repo_meta.json
    repo_index.db
    vector/
  cache/
    file_summaries/
    parsed_ast/
  overlays/
    latest_overlay.json
    history/
  traces/
    <run_id>/
      manifest.json
      steps.jsonl
      outputs.json
      llm_calls.jsonl
  patches/
    <patch_id>.diff
    <patch_id>.json
    applied/
  logs/
    app.log
    commands.log
```

### Index 存储格式

建议采用分层存储：

| 类型 | 建议格式 | 作用 |
|---|---|---|
| 元数据 | JSON | 项目概览、版本、索引时间 |
| 结构化索引 | SQLite 或 DuckDB | 文件、符号、API、图关系 |
| 向量索引 | FAISS / Chroma 可选 | 语义召回 |
| 大文件摘要 | JSON | 降低重复解析成本 |

#### 为什么推荐 SQLite 起步

- 本地部署简单。
- 查询灵活。
- 适合存文件、符号、API、图边等结构化表。
- 后期 Web 服务化也容易迁移。

DuckDB 更适合分析型查询，可作为后续增强，而非一开始必须引入。

### Overlay 存储格式

Overlay 建议用 JSON 存储，便于序列化和回放：

- `git_status`
- `changed_files`
- `hunks`
- `logs_summary`
- `test_summary`

同时保留原始日志路径引用，避免重复保存超大文本。

### TraceRun 存储格式

每次执行一个独立目录，建议包含：

| 文件 | 内容 |
|---|---|
| `manifest.json` | run_id、命令、时间、最终状态 |
| `steps.jsonl` | 每一步节点日志 |
| `outputs.json` | 最终结果 |
| `llm_calls.jsonl` | prompt 摘要、token、响应摘要 |
| `context_refs.json` 可选 | 本次用到的文件与行号引用 |

### Patch 存储格式

每个 patch 应至少包含两部分：

1. `.diff`：可读的补丁文本。
2. `.json`：结构化说明，包括原因、风险、测试建议、适用 diagnosis、应用状态。

### 日志存储格式

- `app.log`：程序运行日志。
- `commands.log`：命令级记录。
- `diagnosis.log` 可选：诊断摘要。
- 日志中应避免落盘敏感变量明文。

### Trace 每次需要记录什么

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
- token 消耗
- 最终状态

### Trace 的价值

#### Debug

当输出错误时，可以定位是：

- 分类错了
- 检索错了
- 上下文预算不够
- 证据校验没拦住
- patch 风险控制不足

#### 简历展示

Trace 让项目从“一个模糊的 AI 工具”变成“一个有可观测性设计的工程系统”。

#### 后续 Web 可视化

Trace 天然适合展示：

- 任务流程图
- 检索证据链
- 诊断推理链
- patch 生成链

#### Agent 评测

Trace 能把失败样本收集起来，支持离线复盘和指标分析。

### 设计结论

Storage 和 Trace 不是附属工程细节，而是 RepoGuide 做“工程级产品”必须具备的基础设施。

---
