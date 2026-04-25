# 07_cli_design.md

### 文档目的

设计 CLI 命令树、参数、输出格式与本地目录约定，让 RepoGuide 最先成为一个好用的本地工具。

### CLI 设计原则

- 命令语义应该贴近开发者操作。
- 默认输出适合人读。
- 支持 `--json` 以便脚本集成。
- 所有复杂结果有对应 `run_id` 或结果 ID 可追踪。
- 默认读本地 `.repoguide/` 配置和索引。

### 命令树

```bash
repoguide
├── init
├── index [path]
├── map
├── ask "<question>"
├── explain-api "<api_path>"
├── explain-flow "<feature_query>"
├── diff
├── diagnose --log error.log
├── diagnose-diff --log error.log
├── suggest-fix --diagnosis <id>
├── apply-patch <patch_id>
├── test
└── trace <run_id>
```

### 命令说明

| 命令 | 用途 | 输入参数 | 输出格式 | 常见失败情况 |
|---|---|---|---|---|
| `repoguide init` | 初始化配置目录 | `--path` 可选 | 初始化结果、配置说明 | 目录无写权限 |
| `repoguide index .` | 构建或更新索引 | 路径、`--full`、`--ref` | 索引摘要、项目类型、入口、模块 | 非仓库目录、解析失败 |
| `repoguide map` | 输出项目地图 | `--refresh` | 模块图、关键文件、启动说明 | 无索引 |
| `repoguide ask` | 项目问答 | 问题文本、`--json` | 可溯源回答 | 检索不到足够证据 |
| `repoguide explain-api` | 解释单个接口 | API path、method | 接口文档式说明 | 路径匹配不到或歧义 |
| `repoguide explain-flow` | 解释业务流程 | 功能描述 | 调用链+流程说明 | 无法定位入口点 |
| `repoguide diff` | 查看本地变化摘要 | `--ref` | 变更文件、影响模块、热点区域 | 非 git 仓库 |
| `repoguide diagnose --log` | 基于日志诊断 | 日志文件 | Diagnosis | 日志无法解析 |
| `repoguide diagnose-diff --log` | 日志 + diff 联合诊断 | 日志文件 | Diagnosis with overlay evidence | 无 diff、无日志 |
| `repoguide suggest-fix --diagnosis` | 生成修复建议 | diagnosis_id | PatchSuggestion | diagnosis 不存在 |
| `repoguide apply-patch` | 预览或应用 patch | patch_id、`--confirm` | 应用结果、变更摘要 | patch 冲突、未确认 |
| `repoguide test` | 执行测试 | `--command`、`--timeout` | 结构化测试结果 | 命令未白名单、超时 |
| `repoguide trace` | 查看某次执行链路 | run_id | Trace 详情 | run_id 不存在 |

### 示例交互

#### 初始化

```bash
repoguide init
```

输出应包括：

- `.repoguide/` 已创建
- 默认忽略规则
- 默认测试命令模板
- 下一步建议：`repoguide index .`

#### 项目索引

```bash
repoguide index .
```

输出应包括：

- 项目类型：`java-springboot` 或 `python-fastapi`
- 扫描文件数
- 识别到的入口文件
- 识别到的核心配置文件
- API 数量、符号数量、模块数量摘要

#### 问答

```bash
repoguide ask "这个项目怎么启动？"
```

输出应包括：

- 启动依赖
- 启动命令候选
- 环境变量和配置位置
- 文件证据引用

### 输出格式建议

默认输出使用 Rich 风格组织为：

- 摘要区
- 证据区
- 风险 / 缺失区
- 下一步建议区

同时支持：

```bash
repoguide ask "..." --json
```

返回结构化 JSON，便于未来 API 或脚本复用。

### `.repoguide/` 本地目录结构

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

### 目录职责

| 目录 | 内容 |
|---|---|
| `config.yml` | 项目级配置，如忽略规则、测试命令白名单、解析偏好 |
| `indexes/` | RepoIndex 持久化结果 |
| `cache/` | 中间缓存，如切片摘要、向量缓存 |
| `overlays/` | Workspace Overlay 历史记录 |
| `traces/` | 每次执行的 TraceRun |
| `patches/` | PatchSuggestion、patch 文件与应用记录 |
| `logs/` | RepoGuide 自身运行日志 |

### 哪些文件可以提交，哪些应加入 `.gitignore`

#### 默认建议加入 `.gitignore`

- `.repoguide/cache/`
- `.repoguide/indexes/`
- `.repoguide/overlays/`
- `.repoguide/traces/`
- `.repoguide/patches/`
- `.repoguide/logs/`

#### `config.yml` 的建议

- 如果 `config.yml` 只包含仓库通用规则、忽略模式、推荐测试命令，可以**允许提交**。
- 如果其中包含 LLM key、私有路径、个人偏好参数，则必须拆出为环境变量或本地覆盖文件，并加入 `.gitignore`。

### CLI 结论

CLI 是 RepoGuide 的第一交付界面。只要 CLI 体验足够顺畅，后续 API 和 Web 就只是在复用已经成熟的核心能力。

---
