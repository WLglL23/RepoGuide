# 15_api_server_design.md

### 文档目的

设计后期 FastAPI 服务化接口，但强调：**API 只是 Core SDK 的服务包装，不应污染内核设计。**

### 设计原则

1. API 不是第一阶段目标。
2. API 不负责核心逻辑，只调用 Core Service。
3. Web 页面只是 API 的消费者，不反向定义内核。
4. 涉及本地 patch / test 权限的接口必须更严格。

### REST API 设计

| 接口 | 请求参数 | 响应结构 | 错误码 | 调用 Core Service | 是否需本地权限 | 是否适合 Web |
|---|---|---|---|---|---|---|
| `POST /repos/index` | `root_path`、`ref`、`full` | `repo_id`、索引摘要 | 400/500 | `RepoGuide.index` | 是 | 适合本地 Web |
| `GET /repos/{repo_id}/map` | `refresh` | `ProjectMap` | 404/500 | `RepoGuide.map` | 否 | 是 |
| `POST /repos/{repo_id}/ask` | `question`、`session_id` | `AnswerResult` | 404/422/500 | `RepoGuide.ask` | 否 | 是 |
| `POST /repos/{repo_id}/explain-api` | `path`、`method` | `ApiExplanation` | 404/422 | `RepoGuide.explain_api` | 否 | 是 |
| `POST /repos/{repo_id}/explain-flow` | `feature_query` | `FlowExplanation` | 404/422 | `RepoGuide.explain_flow` | 否 | 是 |
| `POST /repos/{repo_id}/diagnose` | `log_text` 或 `log_path` | `Diagnosis` | 404/422/500 | `RepoGuide.diagnose` | 是 | 条件适合 |
| `POST /repos/{repo_id}/diagnose-diff` | `log_text/log_path`、`ref` | `Diagnosis` | 404/422/500 | `RepoGuide.diagnose_diff` | 是 | 条件适合 |
| `POST /repos/{repo_id}/suggest-fix` | `diagnosis_id` | `PatchSuggestion` | 404/422 | `RepoGuide.suggest_fix` | 否 | 是 |
| `POST /repos/{repo_id}/apply-patch` | `patch_id`、`confirm` | `ApplyPatchResult` | 403/404/409 | `RepoGuide.apply_patch` | **是** | 谨慎 |
| `POST /repos/{repo_id}/test` | `command`、`timeout` | `TestRunResult` | 403/422/500 | `RepoGuide.test` | **是** | 谨慎 |
| `GET /traces/{run_id}` | 无 | `TraceRun` | 404 | `RepoGuide.trace` | 否 | 是 |

### 建议的响应结构

建议统一返回：

- `success`
- `run_id`
- `data`
- `warnings`
- `errors`

这样 CLI、Web、第三方集成都能统一处理。

### 是否适合 Web 调用的判断

#### 适合 Web 的

- map
- ask
- explain-api
- explain-flow
- trace

#### 需要谨慎的

- index
- diagnose
- diagnose-diff
- apply-patch
- test

因为这些接口往往需要读取本地文件系统、执行命令或修改工作区。

### 本地 CLI 和 API Server 的关系

建议关系如下：

- **CLI**：直接调用 Core SDK，是第一交付形态。
- **API Server**：把同一组 Core SDK 能力包装成 HTTP 服务。
- **Web**：调用 API Server 展示结果。

也就是说：

```text
Core SDK 是源头
CLI / API 是两个薄包装
Web 是 API 的消费者
```

而不是：

```text
先写 Web，再把逻辑拆回后端
```

### 设计结论

API Server 的正确定位是“后期扩展的服务化壳层”，而不是产品的起点。

---
