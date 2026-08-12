# DBAgent

> 以 Text2SQL 为核心，扩展了源数据处理与数据可视化的智能数据库问答系统。

### ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🗣️ **自然语言查询** | 用日常语言提问，自动转换为 SQL 并执行 |
| 🧠 **知识图谱增强** | 从数据库 Schema 自动构建知识图谱，提升查询准确性 |
| 🔍 **查询溯源** | 获取问答依据，支持思考过程与原始结果查看 |
| 📊 **数据可视化** | 支持曲线图、柱状图、饼图等 7 种图表类型 |
| 📋 **交互式表格** | 支持编辑、排序、分页、批量操作 |
| 💬 **多会话管理** | 支持多个数据库会话，历史记录持久化 |
| 👥 **多用户支持** | 自动识别用户身份，隔离会话数据，支持多用户同时使用 |

---

## 🏗️ 系统全景

### 系统架构

![系统架构](./assets/image1.png)

### 系统流程图

![系统流程图](./assets/image2.png)

---

## 📖 使用指南

### 一、图谱管理

图谱管理用于为数据库构建、查看和删除知识图谱，从而提升 Text2SQL 的查询准确率。

#### 1. 打开图谱管理

1. 在侧边栏底部点击 **「图谱管理」** 按钮
2. 输入管理员密码进行身份验证（密码在 `config/db.py` 中配置）
3. 验证通过后进入图谱管理面板

#### 2. 创建图谱

- 在图谱管理面板中，找到目标数据库
- 点击右侧 **「创建」** 按钮
- 系统自动从数据库 Schema 提取实体与关系，构建完成后保存至 MongoDB
- 创建过程中按钮显示为「创建中...」，请耐心等待

#### 3. 删除图谱

- 已创建图谱的数据库右侧显示 **「删除」** 按钮
- 点击后将从 `db.json` 中移除映射关系，并删除 MongoDB 中对应的图谱数据库
- ⚠️ 删除操作不可恢复，请谨慎操作

#### 4. 图谱映射说明

| 配置项 | 说明 |
|--------|------|
| `DB_KG` | 数据库名称 → 知识图谱名称的映射 |
| `KG_DB` | 知识图谱的 MongoDB 存储配置 |

---

### 二、会话管理

会话管理用于创建、切换和删除聊天会话，每个会话绑定一个特定的数据库。

#### 1. 新建聊天

1. 点击侧边栏顶部的 **「新建聊天」** 按钮
2. 在弹出的对话框中选择目标数据库
3. 确认后系统自动创建新会话并切换至该会话

#### 2. 切换会话

- 在侧边栏 **「历史会话」** 区域，按数据库分组展示所有会话
- 点击任意会话即可切换，系统自动加载该会话的历史消息

#### 3. 删除会话

- 将鼠标悬停在会话条目上，右侧出现 **「×」** 删除按钮
- 点击后弹出确认对话框，确认后永久删除该会话及其所有历史消息
- ⚠️ 删除操作不可恢复

#### 4. 会话命名

- 会话名称格式为 `时间戳_数据库名`
- 侧边栏显示时自动去除时间戳前缀，仅显示数据库名称

---

### 三、聊天区

聊天区是与系统进行自然语言交互的核心区域。

#### 1. 发送消息

- 在底部输入框中输入自然语言问题
- 点击 **「发送」** 按钮或按 `Enter` 键发送
- 系统自动将问题转换为 SQL，执行查询并返回结果

#### 2. 消息展示

每条助手回复包含以下部分：

| 模块 | 说明 |
|------|------|
| **思考** | 展示 AI 的推理过程，点击可展开/收起 |
| **查询结果** | 展示 SQL 执行返回的数据表格，默认显示前 5 行，点击可展开全部 |

#### 3. 消息操作

| 操作 | 说明 |
|------|------|
| **删除消息** | 用户消息右上角的 **「×」** 按钮，同时删除对应的助手回复 |
| **重新生成** | 助手回复下方的 **「重新生成」** 按钮，基于相同问题重新生成回答 |
| **前往图表区查看** | 点击后自动跳转至图表区，展示查询结果的依据数据 |

---

### 四、图表区

图表区提供数据可视化与交互式表格编辑功能。

#### 1. 数据表格

进入图表区后，查询结果以交互式表格形式展示，支持以下操作：

| 功能 | 操作方式 |
|------|----------|
| **编辑单元格** | 双击单元格进入编辑模式，修改后按 `Enter` 保存或 `Esc` 取消 |
| **重命名列** | 双击列名进入编辑模式，修改后按 `Enter` 保存 |
| **删除列** | 点击列名右侧的删除图标 |
| **排序** | 点击列名进行升序/降序排序 |
| **分页** | 底部提供分页导航，支持翻页跳转 |
| **多选** | 勾选行首复选框，支持批量操作 |
| **批量删除** | 选中多行后点击 **「批量删除」** 按钮 |
| **加载原数据** | 点击 **「加载原数据」** 重新从后端获取原始数据 |

#### 2. 图表配置

在表格右侧的配置面板中，可以创建可视化图表：

| 配置项 | 说明 |
|--------|------|
| **图表类型** | 支持曲线图、柱状图、散点图、面积图、饼图、直方图、箱线图共 7 种类型 |
| **X 轴** | 选择作为横坐标的列（饼图/直方图/箱线图无需配置） |
| **数据列/类别列** | 选择作为纵坐标的列，支持多选（饼图为类别列，仅可选一列） |
| **数据行** |  选中多行或不选中任何行（默认展示所有数据） |

#### 3. 创建图表

1. 选择图表类型
2. 配置 X 轴和数据列
3. 点击 **「添加图表」** 按钮
4. 图表自动渲染至底部图表展示区域

#### 4. 图表操作

| 操作 | 说明 |
|------|------|
| **展开/收起图表** | 点击图表区域上方的切换按钮 |
| **删除图表** | 点击图表右上角的 **「×」** 按钮 |

---

## 🚀 部署指南

### 后端部署

#### 安装依赖

```bash
# 创建并激活虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
cd backend
pip install -r requirements.txt
```

#### 启动服务

```bash
python main.py
```

服务默认运行在 `http://127.0.0.1:8000`

---

### 前端部署

#### 安装依赖

```bash
cd frontend
npm install
```

#### 开发模式

```bash
npm run dev
```

应用默认运行在 `http://localhost:5173`，API 请求自动转发至后端 `http://localhost:8000`。

#### 生产构建

```bash
npm run build
```

构建产物输出至 `dist/` 目录，可部署至 Nginx 等静态服务器。

#### 预览构建产物

```bash
npm run preview
```

---

## 🌐 Nginx 部署示例

```nginx
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    # 认证接口
    location /auth/ {
        proxy_pass http://backend:8000/auth/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 聊天接口（支持长超时与流式响应）
    location /chat/ {
        proxy_pass http://backend:8000/chat/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
        proxy_buffering off;
    }

    # 图谱管理接口
    location /graph/ {
        proxy_pass http://backend:8000/graph/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 前端静态资源
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

## ⚙️ 配置说明

### 后端配置

| 文件 | 说明 |
|------|------|
| `config/db.py` | MySQL/MongoDB 连接配置、管理员密码 |
| `config/kg.py` | 知识图谱阈值（最大样本数、并发数、外键阈值等） |
| `config/llm.py` | LLM 客户端配置、提示词模板 |
| `config/paths.py` | 路径配置（历史、评估结果等） |
| `config/db.json` | 数据库与知识图谱映射关系 |

### 前端配置

| 文件 | 说明 |
|------|------|
| `src/App.vue` | 后端 API 地址配置 |
| `vite.config.js` | Vite 构建配置 |
| `package.json` | 依赖与脚本配置 |