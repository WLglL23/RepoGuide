# 17_evaluation_design.md

### 文档目的

设计可量化评测体系，让 RepoGuide 的效果能够被验证、迭代和展示。

### 核心指标

| 指标 | 定义 |
|---|---|
| Project Map Accuracy | 项目地图中关键模块、入口、依赖识别的正确率 |
| API Extraction Accuracy | 接口路径、方法、handler、request/response 抽取准确率 |
| Call Chain Accuracy | 调用链节点与边的准确率 |
| Retrieval Precision | 检索前 K 个证据中相关项比例 |
| Answer Citation Coverage | 回答中有证据支持的关键结论占比 |
| Diagnosis Top-1 Accuracy | 根因第一名命中率 |
| Diagnosis Top-3 Accuracy | 根因前三名包含正确答案的比例 |
| Patch Success Rate | 生成 patch 后通过目标验证的比例 |
| First-pass Patch Success Rate | 首次 patch 即通过的比例 |
| Test Pass Rate | 建议测试命令通过比例 |
| Average Token Cost | 单任务平均 token 消耗 |
| Average Runtime | 单任务平均运行耗时 |
| User Confirmation Rate | patch 被用户确认采纳的比例 |

### 指标计算建议

#### Project Map Accuracy

可按模块、入口、关键配置三类加权计算：

- 模块识别准确率
- 启动入口识别准确率
- 中间件依赖识别准确率

#### API Extraction Accuracy

建议拆成：

- 路径准确率
- 方法准确率
- handler 准确率
- request body 字段准确率
- response model 准确率

#### Call Chain Accuracy

建议按边级 F1 评测，而不是只看节点是否出现。

#### Answer Citation Coverage

统计回答中非平凡结论里，有明确文件/函数/行号支持的比例。

### 评测数据集设计

建议构建四类数据集：

1. **Java Spring Boot 示例项目**
2. **Python FastAPI 示例项目**
3. **人工注入 bug 样本**
4. **历史 bug / 错误日志 / 调用链问答样本**

### 样本字段设计

每个评测样本建议包含：

- `repo_id`
- `question` / `log` / `diff`
- `expected_files`
- `expected_symbols`
- `expected_answer_points`
- `expected_root_cause`
- `expected_patch`，可选
- `test_command`，可选

### 样本类型举例

| 样本类型 | 示例 |
|---|---|
| 项目理解样本 | “这个项目怎么启动？” |
| 接口样本 | “解释 `/user/login`” |
| 调用链样本 | “每日签到流程怎么走？” |
| 错误日志样本 | Bean 创建失败、NPE、FastAPI 422 |
| diff 诊断样本 | 改 DTO 字段后 SQL 报错 |
| patch 样本 | 修复空指针、修复导入路径、修复 schema 不匹配 |

### 评测报告格式

建议每次评测输出以下结构：

- 评测日期与版本号
- 数据集说明
- 总体指标
- 分任务指标
- 分语言指标
- Top 失败样本
- 错误归因分析
- 下一轮优化建议

### 人工评测补充

除了自动评测，还应加入人工评分维度：

- 回答是否清楚
- 证据是否充分
- 诊断是否可信
- patch 是否过度修改
- trace 是否可理解

### 设计结论

评测体系的价值，不只是看“好不好”，更是看**哪里不好、为什么不好、下一轮怎么改**。这是 RepoGuide 从 demo 走向工程产品的关键一步。

---
