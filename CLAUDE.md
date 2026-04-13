# CLAUDE.md

本文件用于给 Claude Code / Codex 之类的代码代理提供仓库工作说明。

## 项目概览

FinFlow 是一个面向港美股投资者的金融信息聚合平台。当前一期目标是聚合 Bilibili 和 YouTube 财经博主的视频更新，在 Web 端统一展示，并支持飞书通知。

当前仓库状态：
- 前后端最小运行骨架已完成
- 开发环境约定已建立
- 业务功能仍在持续开发中

详细文档位于：
- [.context/finflow-prd.md](.context/finflow-prd.md) - 产品需求文档
- [.context/finflow-tdd.md](.context/finflow-tdd.md) - 技术设计文档

## 技术栈

- Python 3.12
- FastAPI
- SQLAlchemy Async
- PostgreSQL
- Redis
- APScheduler

- Vue 3
- TypeScript
- Vite
- Pinia
- Element Plus

## 仓库结构

```text
finflow/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── router/
│   │   ├── stores/
│   │   ├── types/
│   │   ├── views/
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
├── nginx/
├── docker-compose.yml
├── docker-compose.prod.yml
└── .env
```

## 关键命令

推荐优先使用 Docker 联调。

```bash
docker compose up
docker compose up --build
docker compose logs -f backend
docker compose logs -f frontend
```

```bash
cd frontend
npm install
npm run dev
npm run build
npm run type-check
```

```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
cd backend
ruff check .
ruff format .
```

默认地址：
- 前端：`http://localhost:5173`
- 后端：`http://localhost:8000`
- API 文档：`http://localhost:8000/api/docs`

## 环境变量

请基于 `.env.example` 维护仓库根目录 `.env`。

关键变量：

- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `YOUTUBE_API_KEY`
- `BILIBILI_SESSDATA`
- `NGINX_CONF_FILE`

注意：
- 当前代码实际使用的是 `SECRET_KEY`，不是 `JWT_SECRET_KEY`
- 从 `backend/` 目录单独启动后端时，也会自动读取仓库根目录 `.env`
- 前端开发时，`/api` 会通过 Vite 代理转发到后端

## 代码约定

- `api/` 仅放路由和请求入口，不堆业务逻辑
- 业务逻辑优先放在 `services/`
- 数据模型统一放在 `models/models.py`
- 请求和响应模型统一放在 `schemas/schemas.py`
- 配置、数据库、鉴权工具统一放在 `core/`
- API 调用统一放在 `src/api/`
- 路由统一在 `src/router/index.ts`
- 页面级组件放在 `src/views/`
- 可复用组件放在 `src/components/`
- 全局状态优先放在 `src/stores/`

## 开发优先级

继续开发时，优先按下面顺序推进：

1. 打通注册、登录与 token 持久化
2. 实现 Creator 添加后的真实解析与入库
3. 接入 Bilibili / YouTube 抓取逻辑
4. 实现视频流展示与筛选
5. 接入飞书通知
6. 补齐 Alembic 迁移与测试

## 代理注意事项

- 修改配置或启动方式时，优先同步更新本文件
- 如果前后端联调异常，先检查 `.env`、数据库、Redis、Vite 代理
- 若新增目录结构或核心命令，请同步更新本文档和 README
