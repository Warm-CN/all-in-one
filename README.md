# 社团统一管理系统 (All-In-One Club Management System)

本项目是一个功能齐全的社团管理平台，旨在简化社团的日常运营、用户认证、会议室预约及活动报名等流程。系统采用前后端分离架构，提供完善的角色权限控制 (RBAC)。

## 🚀 功能特性

- **身份认证与权限管理**
  - 基于 JWT 的安全认证系统。
  - 多级角色控制：`Visitor (游客)`, `Member (成员)`, `Admin (管理员)`。
  - 完善的登录、注册及个人信息管理功能。
- **会议室预约系统**
  - 实时查看会议室详情与空闲状态。
  - 预约申请提交、审批及历史记录查询。
- **日程管理**
  - 集成可视化日历日程管理功能，支持查看与发布个人/团队日程。
- **报名与招新系统**
  - 支持招新面试管理、报名申请及数据统计。
- **管理后台**
  - 用户权限分配、预约审批、成员管理等全局配置功能。
- **响应式适配**
  - 针对移动端进行了深度适配，支持在手机上顺畅操作各项功能。

## 🛠 技术栈

### 后端 (Backend)
- **框架**: FastAPI (高性能 Python Web 框架)
- **数据库**: MySQL / SQLite
- **ORM**: SQLAlchemy (2.0+)
- **数据库迁移**: Alembic
- **安全认证**: python-jose (JWT), Passlib (Bcrypt 密码哈希)
- **核心依赖**: Pydantic, Uvicorn

### 前端 (Frontend)
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **UI 组件库**: Element Plus
- **样式**: Tailwind CSS
- **状态管理**: Pinia
- **路由**: Vue Router
- **网络请求**: Axios

## 📂 项目结构

```text
├── alembic/              # 数据库迁移文件
├── app/                  # 后端核心代码
│   ├── api/v1/           # API 接口路由
│   ├── core/             # 配置文件、数据库初始化、安全配置
│   ├── models/           # SQLAlchemy 数据模型
│   ├── schemas/          # Pydantic 数据验证模型
│   └── services/         # 业务逻辑层
├── docs/                 # 项目详细开发文档
├── frontend/             # Vue 3 前端工程
│   ├── src/api/          # 前端接口请求
│   ├── src/views/        # 页面组件
│   ├── src/store/        # Pinia 状态树
│   └── src/layout/       # 全局布局组件
├── scripts/              # 数据库初始化及工具脚本
├── main.py               # 后端入口文件
└── requirements.txt      # 后端依赖配置
```

## 🚥 快速开始

### 1. 克隆项目
```bash
git clone git@github.com:Warm-CN/all-in-one.git
cd all-in-one
```

### 2. 后端配置与启动
1. **创建虚拟环境** (推荐使用 Python 3.10+):
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
2. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```
3. **数据库初始化**:
   - 运行重建数据库脚本:
     ```bash
     python scripts/rebuild_database.py
     ```
   - 初始化管理员账户:
     ```bash
     python scripts/init_admin.py
     ```
4. **启动服务**:
   ```bash
   python main.py
   ```
   接口文档访问地址: [http://localhost:8001/docs](http://localhost:8001/docs)

### 3. 前端启动
1. **进入前端目录**:
   ```bash
   cd frontend
   ```
2. **安装依赖**:
   ```bash
   npm install
   ```
3. **运行开发服务器**:
   ```bash
   npm run dev
   ```
   

## 📖 开发指南
更多详细信息请参阅 `docs/` 目录下的相关文档：
- [后端开发指南](docs/后端开发指南.md)
- [配置指南](docs/配置指南.md)
- [认证系统使用指南](docs/第二阶段-认证系统使用指南.md)

## 📄 许可证
© 2026 All In One. 仅供内部学习与参考使用。
