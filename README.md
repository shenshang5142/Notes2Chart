# 学习笔记图表生成系统

基于 Vue 3 + Django + Ollama 的智能学习笔记分析平台，支持文件上传、RAG 问答、12 种图表自动生成（ECharts/Mermaid）、知识图谱构建（Neo4j）以及关键词雷达图分析

---

## 项目结构

```
notes/
├── frontend/          # Vue 3 前端（端口: 3000）
├── backend/           # Django 后端（端口: 4567）
└── README.md
```

---

## 一、前端 (frontend/)

**技术栈**: Vue 3 + Vite + Element Plus + ECharts + Axios + Neo4j Driver

### 目录结构

```
frontend/
├── index.html                  # 入口 HTML
├── package.json                # 依赖与脚本
├── vite.config.js              # Vite 配置（含 /api 代理 → 127.0.0.1:4567）
├── launch.bat                  # Windows 启动脚本
└── src/
    ├── main.js                 # 应用入口（注册 Element Plus、路由、全局方法）
    ├── App.vue                 # 根组件
    ├── style.css               # 全局样式
    ├── api/
    │   └── user.js             # 用户 API 封装
    ├── assets/
    │   ├── img/                # 静态图片资源
    │   └── js/
    │       ├── common.js       # 全局公共方法
    │       └── constant.js     # 常量定义
    ├── components/
    │   ├── HelloWorld.vue      # 示例组件
    │   ├── Home.vue            # 布局容器（侧边栏 + 顶栏）
    │   └── SentenceDetail.vue  # 语句详情页
    ├── router/
    │   └── index.js            # 路由配置（Hash 模式）
    ├── utils/
    │   └── http/
    │       ├── axios.js        # Axios 实例（拦截器、错误处理）
    │       └── http.js         # HTTP 工具方法
    └── view/
        ├── Login.vue           # 登录页
        ├── Home.vue            # 主页布局
        ├── Welcome.vue         # 系统首页/欢迎页
        ├── aboutp/
        │   └── aboutp.vue      # 关于项目
        ├── menus/
        │   ├── menu1.vue       # 知识图谱展示（Neo4j + ECharts）
        │   ├── menu2.vue       # 文件上传 + AI 问答 + 图表生成（核心）
        │   └── menu3.vue       # 关键词雷达图 + 词频统计
        └── user/
            ├── Index.vue       # 用户列表
            └── Detail.vue      # 用户详情
```

### 路由表

| 路径             | 页面               | 说明                          |
| ---------------- | ------------------ | ----------------------------- |
| `/login`         | Login.vue          | 登录页面                      |
| `/index`         | Welcome.vue        | 系统首页                      |
| `/menus/menu1`   | menu1.vue          | 知识图谱展示                  |
| `/menus/menu2`   | menu2.vue          | 文件上传 & AI 问答 & 图表生成 |
| `/menus/menu3`   | menu3.vue          | 学习成长雷达图                |
| `/user/detail`   | Detail.vue         | 用户中心                      |
| `/aboutp/aboutp` | aboutp.vue         | 关于项目                      |
| `/sentence/:id`  | SentenceDetail.vue | 语句详情                      |

### 启动方式

```bash
cd frontend
npm install
npm run dev        # 开发模式，端口 3000
npm run build      # 生产构建
```

---

## 二、后端 (backend/)

**技术栈**: Django 4.2 + Django REST Framework + SimpleUI + Ollama (LLM) + Neo4j + ChromaDB + BGE Reranker

### 目录结构

```
backend/
├── requirements.txt            # Python 依赖
└── djangoproject/              # Django 项目根目录
    ├── manage.py               # Django 命令行入口
    ├── launch.bat              # Windows 启动脚本
    ├── db.sqlite3              # SQLite 数据库
    ├── knowledge/              # 项目文档资料
    ├── media/uploads/          # 用户上传文件存储
    ├── parse_notes.py          # Ollama 向量化工具（独立脚本）
    ├── staticfiles/            # 静态文件（admin CSS/JS）
    ├── chroma/                 # ChromaDB 向量存储
    ├── djangoment/             # Django 项目配置
    │   ├── settings.py         # 项目设置（SQLite、CORS、SimpleUI 等）
    │   ├── urls.py             # 路由注册
    │   ├── wsgi.py             # WSGI 入口
    │   └── asgi.py             # ASGI 入口
    └── djangoapp1/             # 主应用
        ├── models.py           # 数据模型（SimpleUser、Mushroom）
        ├── serializers.py      # 序列化器（用户注册/登录）
        ├── views.py            # 接口视图（4 个 API）
        ├── middleware.py        # 自定义中间件（CSRF 处理）
        ├── admin.py            # Django Admin 配置
        └── big_models/
            ├── ask_notes.py    # RAG 问答引擎（Ollama 向量 + 相似度检索 + LLM 生成）
            └── api_neo.py      # 知识图谱服务（FastAPI，端口 8718）
```

### API 接口一览

| 方法 | 路径                     | 功能               | 说明                                                         |
| ---- | ------------------------ | ------------------ | ------------------------------------------------------------ |
| POST | `/user/reg`              | 用户注册           | 接收 username + password                                     |
| POST | `/user/login`            | 用户登录           | 验证密码，返回状态                                           |
| POST | `/upload`                | 文件上传           | 存储到 `media/uploads/`                                      |
| POST | `/sendmessage`           | AI 问答 + 图表生成 | 接收 message + chartType，RAG 检索后调用 Ollama 生成         |
| POST | `/analyze-keywords`      | 关键词分析         | 分析所有已上传文件，返回 Top6 关键词（雷达图）及其余词频（表格） |
| POST | `/build-knowledge-graph` | 知识图谱构建       | FastAPI 服务（端口 8718），调用 Ollama 抽取实体关系写入 Neo4j + ChromaDB |
| POST | `/hybrid-search`         | 混合检索           | 向量检索 + BM25 + BGE 重排序                                 |

### RAG 问答流程 (ask_notes.py)

```
用户提问 → 向量化问题 → 余弦相似度检索知识库 → 拼接 Prompt → Ollama(qwen2.5:7b) 生成答案
```

- **Embedding 模型**: `nomic-embed-text`（Ollama）
- **对话模型**: `qwen2.5:7b`（Ollama）
- **Ollama 地址**: `http://127.0.0.1:11434`
- **支持图表类型**: line, bar, pie, scatter, radar, surface3d, bar3d, heatmap, table, tree, graph, flowchart

### 知识图谱服务 (api_neo.py)

独立 FastAPI 应用（端口 8718），提供：

- 实体关系抽取（调用 Ollama LLM）
- Neo4j 图数据库存储
- ChromaDB 向量存储
- 混合检索：DVR（稠密向量）+ BM25（稀疏）+ BGE Reranker（精排）

### 启动方式

```bash
cd backend/djangoproject
pip install -r ../requirements.txt
python manage.py runserver 127.0.0.1:4567

# 知识图谱服务（独立启动）
python djangoapp1/big_models/api_neo.py    # FastAPI 端口 8718
```


---

## 系统架构总览

```
┌──────────────────────────────────────────────────────────┐
│                    前端 (Vue 3 :3000)                     │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐  │
│  │ Login   │ │ AI 问答   │ │ 知识图谱  │ │ 雷达图/词频  │  │
│  │         │ │ 图表生成  │ │ (Neo4j)  │ │             │  │
│  └─────────┘ └──────────┘ └──────────┘ └─────────────┘  │
└────────────┬──────────────────────┬──────────────────────┘
             │ /api 代理             │ 直连 :8718
             ▼                       ▼
┌──────────────────────┐  ┌──────────────────────┐
│  Django (:4567)       │  │  FastAPI (:8718)     │
│  ┌─────────────────┐ │  │  ┌────────────────┐  │
│  │ RAG 问答引擎     │ │  │  │ 知识图谱构建    │  │
│  │ - 向量检索       │ │  │  │ - 实体关系抽取  │  │
│  │ - 相似度匹配     │ │  │  │ - Neo4j 存储    │  │
│  │ - LLM 生成       │ │  │  │ - ChromaDB 向量  │  │
│  └─────────────────┘ │  │  └────────────────┘  │
│  ┌─────────────────┐ │  │  ┌────────────────┐  │
│  │ 文件上传/用户    │ │  │  │ 混合检索 (HRM)  │  │
│  └─────────────────┘ │  │  │ - DVR + BM25   │  │
│                      │  │  │ - BGE Reranker  │  │
└──────────┬───────────┘  │  └────────────────┘  │
           │              └──────────────────────┘
           ▼                         │
┌──────────────────────┐            │
│  Ollama (:11434)     │◄───────────┘
│  - qwen2.5:7b        │
│  - nomic-embed-text  │
│  (192.168.31.125)    │
└──────────────────────┘

```

---

## 外部依赖服务

| 服务     | 地址                   | 用途                        |
| -------- | ---------------------- | --------------------------- |
| Ollama   | `192.168.31.125:11434` | LLM 推理 + Embedding 向量化 |
| Neo4j    | `localhost:7687`       | 知识图谱存储                |
| ChromaDB | `localhost:8000`       | 向量数据库                  |
