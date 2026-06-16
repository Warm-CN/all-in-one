# Vue 3 前端说明

前端使用 Vue 3 + Vite + Pinia + Vue Router + Element Plus，开发环境默认运行在 `http://localhost:3000`。

## 目录结构

```text
frontend/
├── src/
│   ├── api/                 # 后端接口封装
│   ├── assets/              # 图片与全局样式
│   ├── layout/              # 主布局
│   ├── router/              # 路由与登录守卫
│   ├── store/               # Pinia store
│   ├── utils/request.js     # Axios 实例、Token、错误处理
│   └── views/               # 页面
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## 开发启动

```bash
npm install
npm run dev
```

开发环境请求路径以 `/api` 开头，并由 `vite.config.js` 代理到 `http://localhost:8001`。

## 环境变量

开发环境通常不需要 `.env`。

生产构建前建议创建 `.env.production`：

```env
VITE_API_BASE_URL=
```

这样打包后的前端会请求当前域名下的 `/api/...`，再由 Nginx 转发到后端。

如果前后端不在同一域名，可改为完整后端地址：

```env
VITE_API_BASE_URL=https://api.example.com
```

此时后端 `.env` 中的 `BACKEND_CORS_ORIGINS` 必须包含前端域名。

## 构建

```bash
npm run build
```

构建产物在 `frontend/dist`，服务器部署时由 Nginx 直接托管。

## 主要页面

| 路由 | 页面 |
|------|------|
| `/login` | 登录/注册 |
| `/home` | 首页概览 |
| `/rooms` | 会议室预约 |
| `/contacts` | 通讯录 |
| `/recruitment` | 招新面试管理 |
| `/team-portal` | 公开竞赛队伍报名 |
| `/teams-center` | 竞赛队伍管理 |
| `/admin/recruitment` | 招新配置管理 |
| `/admin/rooms` | 会议室统计与导出 |
| `/admin/schedule` | 日程管理 |
| `/admin/events` | 赛事管理 |
| `/users` | 成员管理 |
| `/settings` | 账号设置 |

## 请求封装

`src/utils/request.js` 会：

- 从 `localStorage` 读取 `token` 并自动加到 `Authorization`。
- 处理后端 `{code, msg, data}` 响应格式。
- 遇到 `401` 清理本地登录状态并跳转 `/login`。
- 避免 `VITE_API_BASE_URL=/api` 时出现 `/api/api/...`。

## 默认管理员

后端执行 `python scripts/init_admin.py` 后，会创建默认管理员：

- 学号：`110`
- 密码：`654321`

登录后请尽快修改密码。
