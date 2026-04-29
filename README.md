# FastAPI 学习与全栈项目 (FastapiLearning)

本项目旨在学习和实践 FastAPI 后端框架，配合 Vue3 前端构建一个前后端分离的完整项目。重点关注了 FastAPI 异步编程、Pydantic 数据验证、路由拆分以及 MySQL/Redis 的协同工作。

## 📁 项目结构说明

以下是项目的核心目录划分，方便快速了解各部分功能：

```text
FastapiLearning/
├── backend/            # FastAPI 后端源码
│   ├── main.py         # 应用程序入口
│   ├── routers/        # 路由分类 (新闻、用户、收藏、历史等 API endpoints)
│   ├── models/         # 数据库基础模型定义 (SQLAlchemy ORM)
│   ├── schemas/        # 数据序列化与请求验证模型 (Pydantic)
│   ├── crud/           # 数据库增删改查具体实现
│   ├── config/         # 数据库与缓存相关配置文件
│   ├── utils/          # 共用工具：JWT鉴权、自定义异常、统一响应格式等
│   └── cache/          # Redis 缓存操作逻辑
├── frontend/           # Vue3 + Vite 前端应用
│   ├── src/            # 前端源码 (包含 Vue 组件、Vite 配置、Vuex/Pinia 状态管理等)
│   └── public/         # 静态资源
└── base_knowledge/     # 知识基础与学习笔记 (Asyncio, FastAPI, MySQL, Redis 等)
```

## 🎯 核心学习重点 (FastAPI 后端)

本项目的后端设计深度实践了 FastAPI 的几大核心特性，非常适合作为进阶学习：

1. **异步编程 (Asyncio & ASGI)**：将复杂的 I/O 操作（数据库查询、缓存存取）全部替换为异步 `async/await`，大幅提高并发承载力。
2. **路由系统 (APIRouter 模块化)**：不把所有代码塞进 `main.py`，而是按业务（News、Users、Favorites）将路由隔离，便于维护与迭代。
3. **请求校验与序列化 (Pydantic)**：通过 `schemas` 下定义的严格类校验前端传来的字段格式，避免不规范数据进入数据库，实现自动输入审查。
4. **依赖注入 (Dependencies)**：在进行 JWT 用户身份鉴权、获取数据库 Session 实例时，利用 Depends()，实现权限检查逻辑与实际业务逻辑的解耦。
5. **异常与响应拦截 (Exception Handlers & Response)**：在 `utils` 目录中统一封装标准 JSON 返回格式与针对特定错误（如未授权、数据不存在）的统一拦截机制。

## 🚀 运行与启动指令

项目分为前后端，推荐在 VS Code 根目录下开启两个独立的终端分别处理。

### 1. 后端启动 (FastAPI)

后端使用轻量高效的 `uv` 来管理运行环境（注意目录名为 `backend`，并非原来误写的 `toutiao_backend`）：

```bash
# 切换到后端目录
cd backend

# 热更新启动 uvicorn 测试服务器，指定 8000 端口
uv run uvicorn main:app --reload --port 8000
```

> **提示**：启动成功后，可在浏览器中直接访问 `http://127.0.0.1:8000/docs` 查看并测试自动生成的 Swagger UI 交互式 API 文档页面。

### 2. 前端启动 (Vue3 + Vite)

前期初次接手项目时，需要安装一次依赖项包（已修正 `install` 拼写错误）：

```bash
# 切换到前端目录
cd frontend

# 初次运行，安装包依赖
npm install

# 启动本地开发服务服务器
npm run dev
```

> 待编译完成后，按照终端控制台打印的提示链接（一般是 `http://localhost:5173/` 端口）在浏览器中打开项目效果。