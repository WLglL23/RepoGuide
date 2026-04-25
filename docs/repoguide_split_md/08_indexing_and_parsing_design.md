# 08_indexing_and_parsing_design.md

### 文档目的

定义索引和解析层如何理解仓库，尤其是 Java / Spring Boot 与 Python / FastAPI 的支持方案。

### 设计原则

- **先规则、再 AST、最后向量。**
- 优先用稳定、成本低、可解释的方法抽取结构。
- 向量检索只在“语义召回”阶段使用，不承担结构真相。

### Java / Spring Boot 解析设计

#### 需要识别的对象

- `@SpringBootApplication`
- `@RestController`
- `@Controller`
- `@RequestMapping`
- `@GetMapping`
- `@PostMapping`
- `@PutMapping`
- `@DeleteMapping`
- `@Service`
- `@Component`
- `@Repository`
- `@Mapper`
- `@Autowired`
- `@Resource`
- DTO / VO / Entity
- Mapper XML
- `application.yml` / `application.properties`
- `pom.xml`

#### 解析策略

| 解析对象 | 主要方法 | 说明 |
|---|---|---|
| 应用入口 | AST + 注解规则 | 找 `@SpringBootApplication` 和 `main` 方法 |
| Controller / API | AST + 注解规则 | 解析类级与方法级路由并合并路径 |
| 依赖注入 | AST | 解析构造器注入、字段注入、`@Resource` |
| Service / Repository / Mapper | AST + 命名约定 | 识别业务层与持久层 |
| DTO / VO / Entity | AST + 注解 + 类名模式 | 类名后缀 + `@Entity` / `@TableName` 等 |
| Mapper XML | XML 解析 | namespace、id、SQL、表名 |
| 配置 | YAML / Properties 解析 | DB、Redis、MQ、port、profiles |
| 构建文件 | XML 解析 | 多模块、依赖、插件、打包方式 |

#### 调用关系构建

Java 项目的调用关系建议分三层构建：

1. **显式调用边**：方法体中的直接方法调用。
2. **注入依赖边**：Controller → Service，Service → Mapper / Repository。
3. **框架推断边**：Controller handler → 参数 DTO → 返回 VO；Mapper 接口 → Mapper XML SQL 节点。

### Python / FastAPI 解析设计

#### 需要识别的对象

- FastAPI app
- APIRouter
- `@router.get`
- `@router.post`
- Pydantic Model
- dependency injection
- `requirements.txt`
- `pyproject.toml`
- pytest tests

#### 解析策略

| 解析对象 | 主要方法 | 说明 |
|---|---|---|
| FastAPI app | AST + 规则 | 找 `FastAPI()` 实例 |
| APIRouter | AST | 找 `APIRouter()` 与 `include_router()` |
| 路由 | AST + decorator 规则 | 解析 method、path、handler |
| Pydantic Model | AST | 提取字段、类型、默认值 |
| Depends 依赖 | AST | 识别注入链 |
| 构建文件 | 文本 / TOML 解析 | 判断项目依赖与命令 |
| pytest | 文件命名 + AST | 识别测试入口和断言文件 |

#### 调用关系构建

Python 的调用图相比 Java 更动态，因此建议采用：

- AST 显式函数调用 + import 依赖。
- FastAPI 路由到 handler 的确定映射。
- 对动态调用保守标注 `missing_links`。
- 对数据库 / ORM / 外部 API 通过库调用模式与变量命名增强识别。

### 通用文件解析

需要统一识别以下文件：

- `README`
- `Dockerfile`
- `docker-compose.yml`
- `.env.example`
- SQL schema
- migration files
- test files
- config files

#### 为什么这些文件重要

因为开发者接手项目时，真正最先看的并不是 Controller，而往往是：

- 如何启动。
- 依赖哪些环境。
- 是否需要 Docker、MySQL、Redis、MQ。
- 数据库表从哪来。
- 测试怎么跑。

### 如何判断文件角色

建议采用“**规则优先、内容补充、上下文增强**”三段式：

1. **路径规则**：例如 `controllers/`、`services/`、`mappers/`、`tests/`。
2. **文件内容规则**：注解、继承、装饰器、关键 import。
3. **仓库上下文规则**：被哪些文件引用、是否被 include_router、是否在 Spring 扫描路径中。

### 如何抽取符号

优先使用 AST / Tree-sitter 抽取：

- 类
- 函数
- 方法
- 构造器
- 变量定义
- 导入语句
- 注解 / 装饰器

对难以完整解析的文件，可退化为规则抽取，但必须标注 `confidence` 较低。

### 如何抽取 API

API 抽取不应只靠正则，而应组合：

- 注解 / 装饰器解析
- 类级与方法级路径合并
- handler 方法签名解析
- DTO / body model 关联
- auth 相关中间件/注解关联

### 如何构建调用关系

建议采用分层图结构：

- **Import Graph**：文件与模块依赖关系
- **Symbol Call Graph**：函数 / 方法之间的调用关系
- **Framework Edge**：由框架规则推断出的链路
- **Resource Edge**：到 DB、Redis、MQ、HTTP Client 的资源调用边

### 如何处理大文件

- 优先按符号切片，不按字符长度粗暴切。
- 对特别大的类或 mapper 文件，抽取摘要与热点区域。
- 保留大文件的：
  - 文件摘要
  - 关键符号索引
  - 行号映射
  - 变更热点窗口

### 如何处理忽略目录

默认忽略：

- `node_modules`
- `target`
- `dist`
- `.git`
- `venv`
- `__pycache__`
- `.idea`
- `.mypy_cache`
- `build`
- `out`

支持在 `config.yml` 自定义覆盖。

### 什么时候使用规则解析

适合：

- 文件角色判定
- README / Dockerfile / YAML / TOML / XML
- Spring 注解识别
- FastAPI 路由 decorator 初步识别
- 日志错误类型识别

### 什么时候使用 AST / Tree-sitter

适合：

- 类、方法、函数边界
- import、依赖注入、参数与返回类型
- 函数调用与类成员关系
- Pydantic / DTO 字段抽取

### 什么时候使用向量检索

只在以下情况作为补充：

- 功能流程的语义召回，例如“打卡流程”“邀请奖励流程”。
- README、文档、注释等弱结构文本语义检索。
- 作为精确检索失败后的补充召回。

### 设计结论

索引与解析层的成败，决定 RepoGuide 是“可解释的工程工具”，还是“黑盒聊天助手”。因此必须坚持：**结构信息来自解析，语义补充才来自向量。**

---
