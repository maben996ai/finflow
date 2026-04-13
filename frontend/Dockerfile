FROM node:20-alpine AS base
WORKDIR /app
COPY package.json ./
RUN npm install

# ---- 开发阶段（docker-compose.yml 使用）----
FROM base AS dev
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ---- 构建阶段 ----
FROM base AS builder
COPY . .
RUN npm run build

# ---- 生产阶段（docker-compose.prod.yml 使用）----
FROM nginx:alpine AS prod
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.prod.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
