# DBAgent Backend

## 📖 后端模块

### 🗄️ 库客户端

用于与数据库服务器建立连接并交互的核心组件。

- **连接池管理**：创建与数据库源之间的连接池，预设最大连接数（可自行配置），超出请求会被阻塞
- **预建连接**：启动时预先建立一定数量的连接，高并发下显著减少频繁创建与销毁连接的开销
- **知识图谱缓存器连接**：按需建立连接，因请求频率较低，无需额外连接池占用内存
- **核心职责**：获取元数据、查询数据库、保存/加载知识图谱

### ⚙️ 应用配置

系统维护和管理人员根据实际使用环境调整的配置项。

- 数据库源与知识图谱缓存器的连接方式
- 服务器性能相关的最大并发数与同时使用人数
- 提示词模板自定义

### 📂 用户存档

在后端服务器本地存储不同用户的历史会话和历史问答。
前端浏览器缓存中会存储一份与后端存档完全一致的历史问答，仅用于下次启动 Web 应用时快速展示。
Text2SQL 执行过程中直接使用后端存档向大模型提供历史问答信息，无需前端传递。

### 🚦 流量控制

防止系统因同时使用人数过多而超负荷。

- **用户数量控制**：严格按照应用配置的最大使用人数控制系统的同时使用人数，超出用户将被拒绝接入
- **连接池保护**：连接池超载时，用户执行需要连接数据库的功能会阻塞等待，控制数据库载荷
- **进程数量控制**：连接池可控制正在进行的大型进程数量在合理区间，同时阻塞其他大型进程，保护后端服务器内存

### 🏗️ 知识图谱构建与删除

| 操作 | 说明 |
|------|------|
| **构建** | 收到构建命令后，按程序构建完整知识图谱，以非关系型数据库形式存入知识图谱缓存器，并保存名称映射关系 |
| **删除** | 收到删除命令后，删除知识图谱缓存器中对应的数据库，清除名称映射关系，代表原数据库不再拥有对应知识图谱 |

### 🤖 Text2SQL

用户提出问题后的完整处理流程：

1. 从知识图谱缓存器中加载正确的知识图谱
2. 将知识图谱按规则转化为字符串类型
3. 将**提示词 + 知识图谱 + 历史问答 + 用户问题**发送给深度思考大模型生成 SQL 查询语句
4. 向被查询数据库发送 SQL 查询语句得到查询结果
5. 将大模型的思考内容和查询结果发送至前端聊天区呈现给用户

### 🔍 查询结果溯源

SQL 查询语句可能包含限制行、分组行、集合运算等子句，导致查询结果无法体现查询涉及到的所有数据。

本模块使用**「查询结果溯源算法」**将 SQL 查询语句转化为一段新的语句，应用到被查询数据库，获取查询涉及到的所有数据并发送至前端图表区呈现给用户。

### 👤 用户状态管理

后端维护正在使用系统的不同用户状态的核心机制。

- 无需前端传递即可知晓用户当前选中的历史会话、使用的知识图谱、历史问答等
- 避免前后端、后端与本地存储、后端与知识图谱缓存器之间频繁的大数据量交互
- 维护的用户状态数量为「流量控制」模块提供服务

### 🔐 管理员验证

将前端发来的验证请求与应用配置中的管理员密码比较，决定是否通过某位用户的管理员验证。

---

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 框架 | FastAPI + Uvicorn |
| 数据库 | MySQL (pymysql), MongoDB (pymongo) |
| LLM | DeepSeek API (openai SDK) |
| SQL 解析 | sqlglot |
| 连接池 | dbutils |
| 会话映射 | bidict |

---

## 📁 项目结构

```
backend/
├── main.py                     # FastAPI 应用入口
├── requirements.txt            # Python 依赖
├── test_text2sql.py            # Text2SQL 测试脚本
├── config/                     # 配置模块
│   ├── db.py                   # MySQL/MongoDB 连接配置 & 管理员密钥
│   ├── kg.py                   # 知识图谱相关阈值配置
│   ├── llm.py                  # LLM 客户端初始化 & 提示词模板
│   ├── paths.py                # 路径配置（历史、评估结果等）
│   └── db.json                 # 数据库与知识图谱映射关系
├── db/                         # 数据库操作模块
│   ├── connection_pool.py      # MySQL 连接池管理
│   ├── mysql_operations.py     # MySQL 查询/元数据操作
│   ├── mongodb_operations.py   # MongoDB 知识图谱存储
│   ├── sqlite_operatons.py     # SQLite 操作（预留）
│   └── *.sql                   # 示例数据库 SQL 脚本（来自 Spider1.0 数据集）
├── knowledge_graph/            # 知识图谱模块
│   ├── builder.py              # 知识图谱构建器（实体/关系/属性提取）
│   ├── attribute_extractor.py  # 实体属性提取（表结构、列统计等）
│   ├── relationship_extractor.py # 关系提取（外键关联等）
│   └── statistic_generator.py  # 统计信息生成
├── llm/                        # LLM 处理模块
│   ├── text2sql.py             # Text2SQL 转换（调用 DeepSeek）
│   ├── process.py              # 对话处理流程
│   ├── text2sql-stable.py      # 稳定版 Text2SQL
│   └── process-stable.py       # 稳定版对话处理
├── routers/                    # API 路由
│   ├── chat.py                 # 聊天接口（会话管理、消息处理、图表数据）
│   ├── chat-stable.py          # 稳定版聊天接口
│   └── graph.py                # 图谱管理接口（创建/删除/验证）
├── utils/                      # 工具模块
│   └── error_logger.py         # 错误日志记录
├── history/                    # 用户会话历史记录
└── log/                        # 运行日志
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- MySQL 8.0+
- MongoDB
- DeepSeek API Key

### 安装依赖

```bash
# 创建并激活虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 启动服务

```bash
python main.py
```

服务默认运行在 `http://127.0.0.1:8000`

---

## ⚙️ 配置说明

### config/db.py

编辑 `config/db.py` 配置数据库连接信息：

```python
MYSQL_DATABASE = {
    'host': '<mysql_host>',
    'port': 3306,
    'user': 'root',
    'password': '<password>',
    'charset': 'utf8mb4'
}

MONGODB_DATABASE = {
    'host': '<mongodb_host>',
    'port': 27017,
    'user': 'admin',
    'password': '<password>',
    'charset': 'utf8mb4'
}

ADMIN_KEY = "<admin_password>"  # 图谱管理密码
```

### config/kg.py

```python
MAX_EXAMPLES = 10      # 知识图谱中列样本最大数量
MAX_CONCURRENCY = 5    # 最大并发数
FK_THRES = 0.5         # 外键识别阈值
MAX_USERS = 10         # 最大用户数
```

### config/llm.py

编辑 `config/llm.py` 配置大模型 API Key：

```python
DEEPSEEK_CLIENT = OpenAI(
    api_key="<your_api_key>",
    base_url="<api_base_url>",
)
```