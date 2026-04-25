# 16_web_ui_later_design.md

### 文档目的

描述后期 Web 页面规划，但不展开前端代码实现，并强调 Web 应最后做。

### 页面设计总览

| 页面 | 展示什么 | 依赖哪些 API | 不负责什么 |
|---|---|---|---|
| 项目总览页 | 项目类型、模块、入口、依赖、启动说明 | `/map` | 不负责索引逻辑 |
| 模块地图页 | 模块树、关键目录、模块关系 | `/map` | 不负责解析 |
| 文件浏览页 | 文件摘要、符号、引用关系 | 后续 file/detail API | 不负责文件读取策略 |
| 接口列表页 | 路由列表、方法、处理器、鉴权 | `/explain-api`、API list | 不负责 API 抽取 |
| 对话问答页 | 问题、回答、证据引用 | `/ask` | 不负责检索与生成 |
| 报错诊断页 | 日志上传、Diagnosis 结果、证据链 | `/diagnose`、`/diagnose-diff` | 不负责根因分析 |
| Git diff 分析页 | changed files、hunk、关联影响 | `/diagnose-diff`、diff API | 不负责读取 git |
| Patch 展示页 | patch 预览、风险等级、测试建议 | `/suggest-fix`、`/apply-patch` | 不负责 patch 生成 |
| Trace 执行链路页 | 节点步骤、检索证据、LLM 摘要 | `/traces/{run_id}` | 不负责 trace 记录 |

### 每个页面应该展示什么

#### 项目总览页

- 项目名称、类型、语言、框架
- 主入口
- 启动方式
- 关键模块
- 关键依赖与环境变量位置

#### 模块地图页

- 目录树
- 模块关系图
- 每个模块的角色、关键文件、对外接口

#### 接口列表页

- API path + method
- controller / handler
- request / response 模型
- 鉴权与中间件

#### 报错诊断页

- 错误摘要
- Top-3 根因
- 证据分类展示
- 建议 patch
- 推荐测试命令

#### Patch 展示页

- diff 视图
- 风险等级
- 解释说明
- 应用按钮与确认框
- 回滚说明

#### Trace 执行链路页

- 执行时间线
- 每个节点输入/输出
- 检索文件列表
- 最终回答与校验结果

### 为什么 Web 应该最后做

1. 没有稳定 Core，Web 只能展示脆弱结果。
2. Web 早做会诱导团队优先做“看上去好看”的功能。
3. 本地工作区、test、patch 等能力，本质上先依赖 CLI 与本地 Runtime。
4. Web 的价值在于可视化、演示和协作，而不是定义产品内核。

### 设计结论

Web 是 RepoGuide 的放大器，不是 RepoGuide 的发动机。

---
