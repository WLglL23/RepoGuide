# 12_diagnosis_design.md

### 文档目的

定义错误诊断能力，覆盖 Java 与 Python 常见问题，并给出结构化诊断流程与输出格式。

### 支持的 Java 常见错误

| 错误类型 | 典型线索 | 首要检查 |
|---|---|---|
| NullPointerException | `NullPointerException` | 栈顶用户代码、最近改动、判空与注入 |
| BeanCreationException | Spring 启动失败 | Bean 定义、配置、依赖注入 |
| NoSuchBeanDefinitionException | 找不到 Bean | `@Service/@Component`、扫描路径、接口实现 |
| SQLSyntaxErrorException | SQL 语法错 | Mapper XML、字段名、表结构、参数绑定 |
| DataIntegrityViolationException | 约束冲突 | 唯一键、非空、外键、实体字段 |
| ClassNotFoundException | 类找不到 | 依赖、包路径、构建输出 |
| Port already in use | 端口冲突 | 配置端口、系统进程 |
| Redis connection failed | Redis 连接失败 | Redis 配置、环境、网络 |
| JWT 鉴权失败 | 401 / token invalid | token 生成/解析、密钥、拦截器 |
| 事务未生效 | 数据未回滚 | `@Transactional` 边界、自调用、异常捕获 |

### 支持的 Python 常见错误

| 错误类型 | 典型线索 | 首要检查 |
|---|---|---|
| ModuleNotFoundError | import 失败 | 环境、依赖、包路径 |
| ImportError | 导入失败 | 名称改动、循环导入 |
| AttributeError | 属性不存在 | 对象类型、字段变动 |
| TypeError | 参数类型或个数不对 | 函数签名、Pydantic 模型 |
| KeyError | 字典 key 缺失 | 输入数据结构变更 |
| Pydantic validation error | 模型校验失败 | 请求字段、类型、必填项 |
| FastAPI 422 | 请求体验证失败 | request body/schema |
| database connection error | DB 连接失败 | 配置、驱动、环境 |
| pytest failed assertion | 测试断言失败 | 最近业务改动、预期值改变 |

### 诊断流程

#### 诊断主流程

1. 错误类型识别。
2. 栈顶文件定位。
3. 区分用户代码与框架代码。
4. 最近修改相关性分析。
5. 调用链反查。
6. 配置检查。
7. 依赖检查。
8. 生成修复建议。

#### 规则解释

- **用户代码优先**：如果栈顶首先落在框架代码，要向上回溯到最近用户代码帧。
- **最近修改优先**：diff 中命中的文件和行应获得更高怀疑权重。
- **配置并列检查**：很多错误根因不在业务代码，而在 yaml / env / pom / requirements。
- **调用链反查**：定位当前错误点在业务流中的上下游，判断是否是上游数据不满足导致。

### 根因排序建议

DiagnosisEngine 建议至少输出 Top-3 根因假设，并为每条给出：

- 原因摘要
- 支持证据
- 反证或不确定点
- 建议检查步骤
- 修复方向

### 诊断输出格式

建议采用固定结构：

#### 错误摘要

- 错误类型
- 首次出现位置
- 影响范围
- 当前 confidence

#### 关键证据

- 日志证据
- diff 证据
- 调用链证据
- 配置证据

#### 可能原因排序

- 原因 1：最可能根因
- 原因 2：次优可能
- 原因 3：备选假设

#### 涉及文件

列出路径、函数、行号和角色。

#### 建议修复步骤

例如：

1. 先恢复空值保护逻辑。
2. 检查 bean 注入是否仍使用旧名称。
3. 验证 token 解析返回值是否可能为空。
4. 跑登录相关测试。

#### 建议运行的测试

- 单元测试命令
- 接口测试命令
- 集成测试命令

#### 是否可以生成 Patch

系统必须明确表态：

- 可以生成低风险 patch
- 可以生成 patch 草案，但建议人工确认
- 当前证据不足，不建议直接生成 patch

### 设计结论

诊断能力的好坏，不仅在于能否识别异常名，更在于能否把**日志、最近修改、调用链与配置**放在一起解释。RepoGuide 的诊断应当始终是一份**结构化的工程分析报告**，而不是一句“请检查空指针”。

---
