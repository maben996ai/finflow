# 上线前检查清单

> 按顺序执行，全部打勾后方可切换生产流量。

---

## 一、依赖与构建

- [ ] 在有 Node 环境的机器执行 `cd frontend && npm install`，生成 `package-lock.json`
- [ ] 将 `package-lock.json` 提交到仓库
- [ ] 将 `frontend/Dockerfile` 第 4 行改回 `RUN npm ci`（删除 if 分支）

---

## 二、服务器环境

- [ ] 阿里云香港 ECS 安装 Docker + Docker Compose（建议 Compose v2）
- [ ] 开放安全组端口：`80`（HTTP）、`443`（HTTPS）
- [ ] 配置域名 DNS A 记录，指向 ECS 公网 IP
- [ ] 验证 DNS 解析生效：`dig your-domain.com`

---

## 三、环境变量

- [ ] 服务器上复制 `.env.example` → `.env`
- [ ] 填写 `SECRET_KEY`（生产必须换掉默认值，建议 `openssl rand -hex 32`）
- [ ] 填写 `YOUTUBE_API_KEY`（Google Cloud Console 申请）
- [ ] 确认 `DATABASE_URL` / `REDIS_URL` 指向正确容器名
- [ ] 此时 `NGINX_CONF_FILE` 保持 `nginx.http.conf`（证书就绪前不启用 HTTPS）

---

## 四、首次启动与数据库迁移

```bash
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

- [ ] 所有容器状态为 `healthy` / `running`
- [ ] `alembic upgrade head` 执行成功，无报错
- [ ] 访问 `http://your-domain.com` 返回前端页面
- [ ] 访问 `http://your-domain.com/api/docs` 返回 FastAPI 文档

---

## 五、HTTPS 证书申请

```bash
# 在宿主机安装 certbot（以 Ubuntu 为例）
sudo apt install certbot
# 停止 nginx，释放 80 端口给 certbot standalone 验证
docker compose -f docker-compose.prod.yml stop nginx
sudo certbot certonly --standalone -d your-domain.com
# 完成后重启
docker compose -f docker-compose.prod.yml start nginx
```

- [ ] `certbot` 成功申请证书，文件位于 `/etc/letsencrypt/live/your-domain.com/`
- [ ] 将 `nginx.https.conf` 中 `your-domain.com` 替换为实际域名（443 block 及 ssl_certificate 路径，共 3 处）
- [ ] 修改 `.env`：`NGINX_CONF_FILE=nginx.https.conf`
- [ ] 重启 nginx：`docker compose -f docker-compose.prod.yml up -d --no-deps nginx`
- [ ] 验证 HTTPS：`curl -I https://your-domain.com`
- [ ] 验证 HTTP → HTTPS 跳转：`curl -I http://your-domain.com`

---

## 六、证书自动续期

```bash
# 添加 crontab（宿主机）
sudo crontab -e
# 加入以下行：每天凌晨 3 点检查续期
0 3 * * * certbot renew --quiet && docker compose -f /path/to/finflow/docker-compose.prod.yml exec nginx nginx -s reload
```

- [ ] crontab 已添加
- [ ] 手动执行 `certbot renew --dry-run` 验证续期流程无误

---

## 七、功能冒烟测试

- [ ] 注册新账号，登录成功
- [ ] 添加一个 B 站 UP 主链接，博主信息正确解析
- [ ] 添加一个 YouTube 频道链接，博主信息正确解析
- [ ] 等待或手动触发抓取，信息流出现视频卡片
- [ ] 配置飞书 Webhook，触发一次抓取，飞书群收到推送消息
- [ ] 抓取日志页面显示正常

---

## 八、上线后监控

- [ ] 检查 `docker compose logs -f` 无持续报错
- [ ] 检查 `/api/crawl-logs` 抓取日志，近期无大量 `failed`
- [ ] 确认 PostgreSQL 数据卷持久化：重启容器后数据不丢失
