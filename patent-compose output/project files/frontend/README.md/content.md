# DBAgent Frontend

## 📖 功能模块

### 🔐 图谱管理

管理员统一创建或删除知识图谱的入口。

- **权限验证**：用户需输入正确的管理员密码通过验证后方可操作
- **创建图谱**：显示数据库源中所有数据库名，用户可选择任意数据库创建知识图谱
- **删除图谱**：已存在知识图谱的数据库名下会显示对应的图谱名称，验证用户可选择删除
- **异步构建**：支持同时创建多张知识图谱，即使管理员离线，后端仍会继续构建进程直至完成或出错

### 💬 会话管理

分为「新建聊天」和「历史会话管理」两部分。

#### 新建聊天
- 仅可选择**已存在知识图谱**的数据库来新建会话
- 会话将以选定数据库作为唯一查询对象
- 新建后自动加入历史会话列表并自动选中

#### 历史会话管理
- 展示用户所有未删除的历史会话，按查询对象分类呈现
- 用户可随时切换至任意历史会话继续操作

> **权限控制**：用户可选的查询对象受管理员严格控制。当数据库不存在知识图谱时，用户无法选择它新建聊天，也无法访问以它为查询对象的历史会话，直到管理员完成知识图谱创建。

### 🗨️ 聊天区

用户与数据库进行知识问答的核心区域。

| 功能 | 说明 |
|------|------|
| **自然语言问答** | 发送关于数据库的任何问题，系统执行 Text2SQL 后将思考过程和查询结果以对话形式展示 |
| **思考过程审查** | 可阅读 AI 的思考内容与 SQL 查询语句，确认查询逻辑是否符合预期 |
| **重新生成** | 回复不符合预期或系统响应失败时，可一键重新生成回复 |
| **上下文延续** | 发送新问题时，历史问答自动作为上下文一同发送给大模型 |
| **消息删除** | 可删除任意一对历史问答，删除后该问答不再参与后续上下文 |
| **跳转图表区** | 可选择任意问题的查询结果，一键跳转至图表区可视化查看 |

### 📊 图表区

图表区主要包含**「源表格」**和**「图表展示区」**两部分。

#### 源表格

以表格形式展示查询的原始数据，支持丰富的交互操作：

- **分页浏览**：数据量较大时自动分页，确保任何数据规模下界面流畅运行
- **列操作**：支持列筛选、列排序、删除列、修改列宽
- **单元格编辑**：双击即可修改任意单元格的值和字段名
- **行选择与删除**：可选择若干行从源副本中批量删除
- **操作撤销**：前端实时保存所有对表操作记录，支持逐步撤销至上一次修改前状态
- **重置源副本**：一键撤销所有对表操作，恢复原始数据

#### 图表展示区

提供多种常用图表的自定义创建功能：

| 图表类型 | 适用场景 |
|----------|----------|
| 📈 曲线图 | 趋势分析、时间序列 |
| 📊 柱状图 | 分类对比、数值比较 |
| 🔵 散点图 | 相关性分析、分布观察 |
| 📉 面积图 | 趋势叠加、占比变化 |
| 🥧 饼图 | 占比分析、结构展示 |
| 📊 直方图 | 频率分布、数据集中趋势 |
| 📦 箱线图 | 异常值检测、数据离散程度 |

**自定义配置**：
- 从表格中选择任意列作为 X 轴（按需）
- 选择任意多列作为数据列
- 可选择部分行进行统计，而非全部数据
- 已创建的图表可单独删除，互不影响

---

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 框架 | Vue 3 (Composition API + `<script setup>`) |
| 构建工具 | Vite 7 |
| UI 组件库 | Element Plus |
| HTTP 客户端 | Axios |
| Markdown 渲染 | Marked |
| 图表库 | Plotly.js |
| Web 缓存 | localStorage, sessionStorage |

---

## 🖼️ 界面预览

### 聊天区
![聊天区](./public/chat.png)

### 图表区
![图表区](./public/chart.png)

### 图谱管理
![图谱管理](./public/kg.png)

---

## 🚀 快速开始

### 环境要求

- Node.js 18+
- npm 或 pnpm

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

应用默认运行在 `http://localhost:5173`，API 请求自动转发至后端 `http://localhost:8000`。

### 生产构建

```bash
npm run build
```

构建产物输出至 `dist/` 目录，可部署至 Nginx 等静态服务器。

### 预览构建产物

```bash
npm run preview
```

---

## ⚙️ 配置说明

### API 地址

在 `src/App.vue` 中配置后端地址：

```javascript
axios.defaults.baseURL = 'http://localhost:8000'
```

生产环境中可修改为实际后端地址，或通过 Nginx 反向代理。

### 用户标识

用户首次访问时自动生成唯一标识，持久化存储于 `localStorage`：

```javascript
const userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
```

### 会话消息缓存

会话消息缓存在 `localStorage` 中，键名为 `sessionMessagesCache`，切换会话时自动加载恢复。

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