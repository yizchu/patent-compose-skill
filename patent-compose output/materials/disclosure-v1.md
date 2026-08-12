# DBAgent 项目分析结果

## 项目概述
DBAgent 是一个基于 FastAPI 的智能数据库代理系统，集成了大语言模型（LLM）和知识图谱技术，提供自然语言到 SQL 的转换能力，以及数据库知识图谱的构建和查询功能。

## 项目架构

### 技术栈
- **后端框架**: FastAPI (Python)
- **数据库支持**: MySQL, SQLite, MongoDB
- **AI/LLM**: 大语言模型集成（Text-to-SQL）
- **知识图谱**: 自定义知识图谱构建和查询系统
- **前端**: 独立前端应用（package.json 可见）

### 目录结构
```
DBAgent/
├── backend/
│   ├── config/          # 配置模块
│   ├── db/              # 数据库操作模块
│   ├── knowledge_graph/ # 知识图谱模块
│   ├── llm/             # LLM 集成模块
│   ├── routers/         # API 路由模块
│   ├── utils/           # 工具模块
│   ├── history/         # 用户历史记录
│   └── main.py          # 应用入口
└── frontend/            # 前端应用
```

## 核心技术细节

### 1. 多数据库连接池管理系统
**来源文件**: `backend/db/connection_pool.py`, `backend/db/mysql_operations.py`, `backend/db/sqlite_operatons.py`, `backend/db/mongodb_operations.py`

- **统一连接池接口**: ConnectionPool 类提供统一的数据库连接管理接口，支持 MySQL、SQLite、MongoDB 多种数据库服务器
- **连接生命周期管理**: create_pool() 方法根据数据库服务器类型创建对应的连接池，connect() 和 close() 方法管理连接和游标的获取与释放
- **MySQL 连接封装**: MysqlConnection 类封装 MySQL 连接操作，提供 execute_sql() 方法执行 SQL 语句并自动处理结果
- **数据导入功能**: import_sqlite_to_mysql() 实现 SQLite 到 MySQL 的数据迁移，import_csv_to_mysql() 实现 CSV 文件导入 MySQL
- **MongoDB 连接管理**: connect_mongodb() 提供 MongoDB 客户端连接

### 2. 知识图谱构建与管理系统
**来源文件**: `backend/knowledge_graph/builder.py`, `backend/knowledge_graph/relationship_extractor.py`, `backend/knowledge_graph/attribute_extractor.py`, `backend/knowledge_graph/statistic_generator.py`

#### 2.1 知识图谱数据结构
- **KnowledgeGraph 类**: 核心数据结构，包含实体（entities）、关系（relationships）、实体分类（entity_classifications）三个字典
- **实体管理**: add_entity() 添加实体及其分类，get_relationships() 查询实体的关系
- **关系管理**: add_relationship() 添加实体间的关系，支持关系类型过滤
- **知识图谱信息生成**: generate_kginfo() 生成结构化的知识图谱文本描述，包含实体分类、关系列表、实体属性

#### 2.2 知识图谱构建流程
- **KnowledgeGraphBuilder 类**: 知识图谱构建器，从数据库自动生成知识图谱
- **单表实体构建**: build_entities_from_one_table() 从单个数据库表构建实体，包括表实体、列实体、列属性
- **全库实体构建**: build_entities_from_database() 遍历数据库所有表，支持获取外键关系和隐藏关系
- **数据库文档解析**: parse_db_doc() 解析数据库文档并更新知识图谱
- **MongoDB 持久化**: save_to_mongodb() 将知识图谱保存到 MongoDB，包括实体、关系、分类、统计信息
- **MongoDB 加载**: build_from_mongodb() 从 MongoDB 加载已有的知识图谱

#### 2.3 关系提取
- **表列关系生成**: generate_table_col_relationships() 从数据库表结构提取表与列的关系
- **外键检查**: check_foreign_key() 检查两表之间是否存在外键约束
- **跨表列关系获取**: get_crosstable_col_relationships() 获取跨表的列关系
- **隐藏关系探索**: explore_crosstable_col_relationships() 基于知识图谱信息探索潜在的跨表关系

#### 2.4 属性提取
- **TableAttribute 模型**: 表属性数据模型，包含表名、描述、列数、行数、列信息等
- **ColumnAttribute 模型**: 列属性数据模型，包含列名、类型、描述、示例值、统计信息等
- **数据规范化**: normalize() 函数对示例数据进行规范化处理
- **表属性获取**: get_table_attributes() 从数据库获取表的元数据和统计信息
- **列属性获取**: get_col_attributes() 获取列的详细属性，包括数据类型、示例值、统计信息

#### 2.5 统计信息生成
- **StatisticGenerator 类**: 统计信息生成器
- **通用统计**: _generate_common_stats() 生成列的通用统计信息（空值数、唯一值数等）
- **数值统计**: _generate_numeric_stats() 生成数值列的统计信息（最大值、最小值、平均值等）
- **字符串统计**: _generate_string_stats() 生成字符串列的统计信息（最大长度、最小长度、平均长度等）

### 3. LLM 集成与 Text-to-SQL 系统
**来源文件**: `backend/llm/text2sql.py`, `backend/llm/process.py`, `backend/config/llm.py`

- **Text-to-SQL 转换**: text2sql() 函数将自然语言消息转换为 SQL 查询
- **聊天处理**: one_chat() 函数处理单轮聊天对话
- **Text-to-SQL 提示词生成**: text2sql_SP() 生成带知识图谱上下文的 Text-to-SQL 提示词
- **数据库文档分析提示词**: generate_dbdoc_analysis_prompt() 生成数据库文档分析提示词，支持多种数据库服务器类型

### 4. 查询结果溯源算法
**来源文件**: `backend/routers/chat.py`

#### 4.1 溯源算法核心思想
SQL 查询语句可能包含限制行（LIMIT）、分组（GROUP BY）、集合运算（UNION/INTERSECT/EXCEPT）等子句，导致查询结果无法体现查询涉及到的所有数据。溯源算法将原始 SQL 查询语句转化为一段新的语句，应用到被查询数据库，获取查询涉及到的所有完整数据并发送至前端图表区呈现给用户。

#### 4.2 SQL AST 递归解析与转换
- **SQL 解析**: 使用 sqlglot 库的 parse_one() 函数将 SQL 字符串解析为抽象语法树（AST），支持指定数据库方言（dialect）
- **递归节点处理**: _process_node_recursive() 函数递归遍历 AST 节点，根据节点类型进行不同处理：
  - **子查询处理**: 遇到 exp.Subquery 节点时，提取内部节点并递归处理，保留括号结构返回新的 Subquery 节点
  - **集合运算处理**: 遇到 exp.Union/Intersect/Except 节点时，递归处理左右子节点，保持集合运算结构不变
  - **SELECT 语句块处理**: 遇到 exp.Select 节点时，调用 _transform_single_select() 进行具体转换
- **单 SELECT 语句转换**: _transform_single_select() 函数处理单个 SELECT 语句块（不包含 UNION），执行以下转换步骤：
  1. **列提取**: 遍历 SELECT 节点的所有子节点，提取 SELECT、JOIN、WHERE 中提到的所有列引用（exp.Column）
  2. **星号处理**: 检测并处理星号表达式（SELECT * 或 SELECT table.*），记录是否有星号及对应的表名
  3. **JOIN 等值对提取**: 提取 JOIN 条件中的等值对（exp.EQ），记录等值连接的列对
  4. **列去重**: 对 JOIN 等值列进行去重，等值条件中的两个列只保留一个，避免冗余
  5. **构建新 SELECT**: 根据提取的列构建新的 SELECT 语句，包含所有提到的列
  6. **保留 FROM 子句**: 复制原始 FROM 子句到新 SELECT 语句
  7. **保留 JOIN 子句**: 复制所有 JOIN 子句到新 SELECT 语句，保持表连接逻辑
  8. **保留 WHERE 子句**: 复制 WHERE 子句到新 SELECT 语句，保持数据筛选条件
  9. **移除限制子句**: 移除 ORDER BY、LIMIT、GROUP BY、HAVING、DISTINCT 等影响结果集完整性的子句

#### 4.3 溯源数据获取流程
- **SQL 转换调用**: get_data() 接口从历史记录中读取原始 SQL，调用 transform_sql() 函数进行溯源转换
- **溯源 SQL 执行**: 使用转换后的溯源 SQL 查询数据库，获取查询涉及到的所有完整数据
- **数据格式转换**: convert_bytes_to_str() 函数递归遍历查询结果，将所有 bytes 类型转换为字符串（优先 UTF-8 解码，失败则尝试 GBK 解码，最后使用 base64 编码）
- **前端图表展示**: 将溯源数据返回至前端图表区，呈现给用户完整的查询涉及数据

### 5. API 路由与业务逻辑
**来源文件**: `backend/routers/chat.py`, `backend/routers/graph.py`

#### 5.1 聊天路由
- **ChatState 类**: 聊天状态管理，维护用户会话历史
- **数据库列表获取**: get_databases() 获取可用数据库列表
- **会话管理**: get_sessions() 获取用户会话列表，select_chat() 选择/创建会话
- **问答接口**: ask_question() 处理用户问题，调用 LLM 生成 SQL 并执行查询，保存结果到历史记录
- **重新生成**: regenerate_output() 重新生成指定问题的回答
- **数据获取**: get_data() 获取问题对应的查询结果，调用溯源算法获取完整数据
- **SQL 方言转换**: transform_sql() 函数在不同数据库服务器间转换 SQL 语法，包括函数名替换、LIMIT/OFFSET 语法转换、日期函数转换等
- **递归节点处理**: _process_node_recursive() 和 _transform_single_select() 递归处理 SQL AST 节点进行转换
- **会话/消息删除**: delete_session(), delete_message() 删除会话或消息
- **登出**: logout() 清理用户会话状态

#### 5.2 图谱路由
- **管理员验证**: verify_admin() 验证管理员密码
- **图谱列表获取**: get_graphs() 获取可用的知识图谱列表
- **图谱删除**: delete_graph() 删除指定的知识图谱
- **图谱创建**: create_graph() 创建新的知识图谱，包括实体构建、关系提取、属性提取、统计生成、MongoDB 持久化

### 6. 配置管理系统
**来源文件**: `backend/config/db.py`, `backend/config/llm.py`, `backend/config/kg.py`, `backend/config/paths.py`

- **数据库配置**: 从 db.json 读取数据库连接配置
- **LLM 配置**: 大语言模型相关配置
- **知识图谱配置**: 知识图谱构建参数配置
- **路径管理**: get_user_history_root() 获取用户历史记录存储路径

### 7. 错误日志系统
**来源文件**: `backend/utils/error_logger.py`

- **模块化日志**: get_error_logger() 为不同模块创建独立的日志记录器
- **结构化错误记录**: log_error() 记录错误信息，包含模块名、路由名、错误详情和额外上下文

### 8. 用户历史记录管理
**来源文件**: `backend/history/` 目录下的 JSON 文件

- **会话历史**: 每个会话包含 system.json 和多轮对话 JSON 文件
- **问题记录**: 记录用户问题、生成的 SQL、查询结果、执行状态等
- **用户隔离**: 通过 user_id 隔离不同用户的历史记录

## 潜在专利点

1. **基于知识图谱增强的 Text-to-SQL 转换方法**: 利用自动构建的数据库知识图谱提供上下文，提升自然语言到 SQL 的转换准确率
2. **多数据库连接池统一管理系统**: 支持多种数据库类型的统一连接池管理接口
3. **数据库知识图谱自动构建方法**: 从关系型数据库自动提取实体、关系、属性并构建知识图谱
4. **跨表隐藏关系发现算法**: 基于知识图谱信息探索数据库表之间的潜在关联关系
5. **SQL 方言自动转换方法**: 在不同数据库服务器间自动转换 SQL 语法差异
6. **知识图谱驱动的数据库统计分析系统**: 基于知识图谱的列统计信息生成和管理
7. **智能数据库代理会话管理系统**: 支持多轮对话、历史追溯、结果重新生成的会话管理
8. **数据库文档自动解析与知识图谱更新方法**: 解析数据库文档并增量更新知识图谱
9. **基于 AST 递归解析的查询结果溯源算法**: 将包含限制、分组、集合运算的 SQL 查询转换为获取完整涉及数据的溯源 SQL，支持子查询和复杂集合运算的递归处理