# FinFlow

FinFlow 是一个聚合 Bilibili、YouTube 等财经内容源的 Web 平台，目标是把投资者日常关注的视频更新、后续资讯与通知能力集中到一个统一入口。

当前仓库已经完成前后端最小运行骨架，适合继续迭代业务功能。

## 快速开始

### 1. 准备环境变量

```bash
cp .env.example .env
```

按需填写：
- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`
- `YOUTUBE_API_KEY`
- `NGINX_CONF_FILE`

### 2. Docker 开发模式

```bash
docker compose up
```

启动后默认地址：
- 前端：`http://localhost:5173`
- 后端：`http://localhost:8000`
- API 文档：`http://localhost:8000/api/docs`

### 3. 单独运行前后端

前端：

```bash
cd frontend
npm install
npm run dev
```

后端：

```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 常见问题

### 1. 前端请求接口返回 404

前端开发环境依赖 Vite 代理转发 `/api` 请求。

检查项：
- 确认 [frontend/vite.config.ts](/Users/yangyaqi/Projects/finflow/frontend/vite.config.ts) 里仍然存在 `/api` 代理
- 如果后端跑在宿主机本地而不是 Docker 容器里，把代理目标从 `http://backend:8000` 改成 `http://localhost:8000`

### 2. 后端启动时报数据库或 Redis 连接错误

通常是因为 PostgreSQL / Redis 还没有启动，或者 `.env` 里的连接串配置不正确。

可以优先执行：

```bash
docker compose up postgres redis backend
```

### 3. `docker compose` 命令不可用

不同环境下 Docker 命令可能不同：
- 新版通常使用 `docker compose`
- 老版可能使用 `docker-compose`

如果两者都不可用，需要先检查 Docker 是否正确安装。

### 4. 前端依赖安装失败

请先确认本机已安装 Node.js 和 npm：

```bash
node -v
npm -v
```

### 5. 后端依赖安装后仍无法启动

请确认依赖已安装在当前 Python 环境中，尤其是：
- `fastapi`
- `pydantic-settings`
- `sqlalchemy`
- `asyncpg`

## 目录说明

- `backend/`：FastAPI 后端
- `frontend/`：Vue 3 + Vite 前端
- `nginx/`：网关配置
- `.context/`：产品与技术文档

## 文档

- [CLAUDE.md](./CLAUDE.md)：给代码代理的仓库工作说明
- [.context/finflow-prd.md](./.context/finflow-prd.md)：产品需求文档
- [.context/finflow-tdd.md](./.context/finflow-tdd.md)：技术设计文档
