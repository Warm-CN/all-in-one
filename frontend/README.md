# Vue 3 前端项目说明

## 项目结构

```
frontend/
├── src/
│   ├── api/                # API 接口
│   │   └── auth.js        # 认证相关接口
│   ├── assets/            # 静态资源
│   ├── components/        # 公共组件
│   ├── layout/            # 布局组件
│   ├── router/            # 路由配置
│   │   └── index.js       # 路由主文件
│   ├── store/             # 状态管理
│   │   ├── index.js       # Pinia 入口
│   │   └── user.js        # 用户状态
│   ├── utils/             # 工具函数
│   │   └── request.js     # Axios 封装
│   ├── views/             # 页面
│   │   ├── Login.vue      # 登录页
│   │   └── Home.vue       # 首页
│   ├── App.vue            # 根组件
│   └── main.js            # 入口文件
├── index.html             # HTML 模板
├── vite.config.js         # Vite 配置
├── package.json           # 依赖配置
└── .env                   # 环境变量
```

## 安装依赖

```bash
cd frontend
npm install
```

## 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

## 构建生产版本

```bash
npm run build
```
