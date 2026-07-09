# 社团统一管理系统

这是一个基于 FastAPI + Vue 3 的社团统一管理系统，当前包含用户认证、成员管理、会议室预约、日程管理、招新报名、竞赛队伍与赛事管理、共建模块等。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI, SQLAlchemy, Pydantic, JWT, SlowAPI |
| 数据库 | MySQL 8.x, PyMySQL |
| 前端 | Vue 3, Vite, Pinia, Vue Router, Element Plus, Tailwind CSS, html-to-image |
| 部署 | Nginx, systemd, Uvicorn |

## 快速启动

### 后端

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

编辑 `.env`，至少填写 `DB_PASSWORD` 和 `SECRET_KEY`，并确保 MySQL 中存在 `club_management` 数据库。

```powershell
python main.py
```

后端默认运行在 `http://localhost:8001`，接口文档为 `http://localhost:8001/docs`。

### 前端

```powershell
cd frontend
npm install
npm run dev
```

前端开发服务器默认运行在 `http://localhost:3000`，并通过 Vite 代理请求 `http://localhost:8001`。

### 初始化管理员

首次建库后运行：

```powershell
python scripts/init_admin.py
```

默认管理员账号：

| 字段 | 值 |
|------|----|
| 学号 | `110` |
| 密码 | `654321` |

登录后请尽快修改默认密码。

## 文档索引

| 文档 | 用途 |
|------|------|
| [docs/DEPLOY.md](docs/DEPLOY.md) | 服务器部署、升级、备份、Nginx、systemd、HTTPS、排错 |
| [docs/配置指南.md](docs/配置指南.md) | 本地/生产环境变量、数据库、前后端配置 |
| [docs/数据库配置指南.md](docs/数据库配置指南.md) | MySQL 安装、.env 字段说明、建库建表、管理员初始化 |
| [docs/后端开发指南.md](docs/后端开发指南.md) | 后端目录结构、模型、权限、接口概览 |
| [frontend/README.md](frontend/README.md) | 前端目录、环境变量、构建说明 |
| [docs/API_会议室预约.md](docs/API_会议室预约.md) | 会议室预约接口细节 |
| [docs/API_日程管理.md](docs/API_日程管理.md) | 日程查询与管理接口细节 |
| [docs/共建模块设计.md](docs/共建模块设计.md) | 共建模块元素选择模式设计文档 |

## 生产部署入口

服务器部署请优先阅读 [docs/DEPLOY.md](docs/DEPLOY.md)。生产环境建议：

- 后端仅监听 `127.0.0.1:8001`，由 Nginx 对外转发。
- 前端使用 `npm run build` 生成 `frontend/dist`，由 Nginx 托管。
- `.env` 中 `DEBUG=False`，`SECRET_KEY` 使用随机强密钥。
- 部署前备份数据库与 `uploads/`。
