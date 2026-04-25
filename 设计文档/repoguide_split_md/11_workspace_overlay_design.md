# 11_workspace_overlay_design.md

### 文档目的

重点定义 Workspace Overlay，因为这是 RepoGuide 最关键、最有辨识度的能力之一。

### 为什么远程仓库不是唯一真实状态

在开发者日常工作中，真正引起问题的状态往往不在远程主干仓库，而在本地：

- 未提交修改。
- 新增文件。
- 删除文件。
- 临时配置改动。
- 尚未推送的 patch。
- 刚跑出的错误日志。
- 刚失败的测试结果。

如果系统只理解远程仓库，就无法回答“我刚改了什么，为什么现在挂了”。

### 为什么本地工作区才是用户遇到 bug 时的真实状态

开发者遇到的故障是**状态性**问题，而不是静态代码问题。  
例如：

- 一个新加的拦截器文件还没提交。
- 一个 import 指向了刚删除的工具类。
- 一个配置从 `application-dev.yml` 被临时改坏。
- 一个 SQL 参数对象字段改名，但 XML 还没同步。

这些都必须以 Workspace Overlay 表示，而不能硬塞进 Base Repo Index。

### Base Repo Index 和 Workspace Overlay 的关系

可以把二者理解为：

- **Base Repo Index**：稳定版本的结构化地图。
- **Workspace Overlay**：当前工作区的增量和运行期证据。

它们的关系不是替代，而是叠加：

```text
最终理解上下文 = Base Repo Index + Workspace Overlay + 当前用户问题
```

### Overlay 需要读取的内容

| 数据源 | 读取内容 | 用途 |
|---|---|---|
| `git status` | changed / staged / untracked / deleted | 变更范围感知 |
| `git diff HEAD` | 未提交改动 | 可疑修改定位 |
| staged diff | 暂存区变化 | 识别即将提交的变更 |
| untracked files | 新增文件 | 纳入候选证据 |
| deleted files | 删除文件 | 检查 import / 调用失效 |
| error logs | 栈、错误类型、位置 | 故障定位 |
| test results | 哪些测试失败、失败断言 | 验证链路和二次诊断 |

### Overlay 如何注入检索和诊断

#### 优先级规则

1. 最近修改文件优先。
2. 报错栈文件强制召回。
3. diff 修改行附近代码优先。
4. 新增文件必须纳入候选。
5. 删除文件应触发依赖缺失检查。
6. 如果最近修改涉及配置文件，则配置检查优先级上升。

#### 实现思路

Overlay 进入系统后，不只是“附加信息”，而应该改变排序与上下文构建：

- Retrieval 层对 changed files 增加 boost。
- Diagnosis 层对 diff hunk 周围符号增加怀疑权重。
- ContextBuilder 将日志摘要和变更摘要放在上下文顶部。
- PatchPlanner 优先建议最小修改面修复。

### 如何输出诊断证据

诊断结果中应明确区分证据来源：

| 证据类型 | 示例 |
|---|---|
| 日志证据 | “NPE 出现在 `LoginInterceptor.java:47`” |
| diff 证据 | “最近修改删除了 `userContext == null` 判空逻辑” |
| 项目索引证据 | “该拦截器由 WebMvcConfig 注册，作用于 `/api/**`” |
| 推理建议 | “高概率是登录态未写入 request attribute 导致” |

这样用户可以清楚知道：哪些是系统发现的事实，哪些是推理得出的建议。

### 示例流程：用户改了 LoginInterceptor，本地出现 NullPointerException

#### 已知条件

- 错误日志指向 `LoginInterceptor.preHandle()`。
- `git diff HEAD` 显示最近修改了 `LoginInterceptor`。
- Base Repo Index 知道该拦截器被配置在登录态鉴权链路上。
- 调用链显示 `LoginInterceptor` 会读取请求头 token 并调用 `UserContextService`。

#### RepoGuide 应如何工作

1. **LogParser** 识别 `NullPointerException`，抽取栈顶用户代码位置。
2. **StackTraceLocator** 定位到 `LoginInterceptor.java:47`。
3. **GitDiffAnalyzer** 找到这一行附近发生过修改，例如删除了 null 判断、改了注入字段、改了 token 解析逻辑。
4. **Retriever** 同时召回：
   - `LoginInterceptor`
   - `WebMvcConfig`
   - `UserContextService`
   - token 相关工具类
5. **DiagnosisEngine** 生成根因假设排序：
   - token 为空导致 userContext 为空；
   - 注入 bean 为空；
   - request attribute key 改名导致下游取值为空。
6. **Answer** 输出：
   - 日志证据；
   - diff 证据；
   - 调用链背景；
   - 修复建议；
   - 是否建议生成 patch。

### 设计结论

Workspace Overlay 不是二级功能，而是 RepoGuide 与普通“仓库问答工具”最本质的分界线。没有 Overlay，项目只能被“理解”；有了 Overlay，项目才能被“诊断”。

---
