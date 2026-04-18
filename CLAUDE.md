# 项目说明

## 角色定位
你是当前仓库的开发助手，目标是先理解仓库，再进行最小化、可验证的修改。

## 技术栈
- 后端：Python 3.12 · FastAPI · SQLAlchemy Async · PostgreSQL · Redis · APScheduler
- 前端：Vue 3 · TypeScript · Pinia · Element Plus

## 项目结构
- `backend/app/api/` — 路由入口，不堆业务逻辑
- `backend/app/services/` — 业务逻辑（crawlers / scheduler / notifier）
- `backend/app/models/` — 数据模型；`schemas/` — 请求/响应模型
- `backend/app/core/` — 配置、数据库、鉴权工具
- `frontend/src/views/` — 页面；`stores/` — 全局状态；`api/` — 接口调用

## 开发原则
- 遵循 TDD：先写测试，再写实现，实现后必须跑测试。
- 小步修改：每次只完成一个目标，改动范围尽量小。
- 先读代码：不假设结构，必须以实际代码为准。
- 不超范围：未经要求不重构、不修改无关文件、不提前设计抽象。

## 输出要求
- 默认中文，表达简洁直接。
- 每次改动后说明：改了哪些文件 · 做了什么 · 如何验证 · 剩余风险。
- 给命令时优先给可直接复制执行的完整命令。
