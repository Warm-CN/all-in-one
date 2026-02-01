# Ubuntu 云服务器部署指南 (FastAPI + Vue 3)

本指南介绍如何将本项目部署到 Ubuntu 云服务器上，使用 **Nginx** 作为 Web 服务器，**Gunicorn + Uvicorn** 作为后端应用服务器，并使用 **Systemd** 进行进程管理。

## 1. 准备工作

### 系统更新与基础包
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-venv python3-pip nodejs npm nginx mysql-server
```

### 环境依赖
- **Python**: 3.10+
- **Node.js**: 18+
- **MySQL**: 8.0+

## 2. 数据库配置

1. 登录 MySQL: `sudo mysql`
2. 创建数据库并分配权限：
   ```sql
   CREATE DATABASE club_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'club_user'@'localhost' IDENTIFIED BY 'your_strong_password';
   GRANT ALL PRIVILEGES ON club_management.* TO 'club_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

## 3. 获取代码与后端设置

1. **克隆项目**:
   ```bash
   cd /var/www
   sudo git clone <your-repo-url> all_in_one
   sudo chown -R $USER:$USER all_in_one
   cd all_in_one
   ```

2. **后端环境**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn uvicorn
   ```

3. **配置环境变量**:
   创建 `.env` 文件并填入生产环境配置：
   ```text
   DEBUG=False
   DB_HOST=localhost
   DB_USER=club_user
   DB_PASSWORD=your_strong_password
   DB_NAME=club_management
   SECRET_KEY=使用openssl_rand_base64_(32)_生成的随机字符串
   BACKEND_CORS_ORIGINS=http://your_domain.com,https://your_domain.com
   ```

4. **初始化数据库**:
   ```bash
   python3 scripts/rebuild_database.py
   python3 scripts/init_admin.py
   ```

## 4. 后端进程管理 (Systemd)

创建服务文件: `sudo nano /etc/systemd/system/club-backend.service`

```ini
[Unit]
Description=Gunicorn instance to serve Club Management API
After=network.target

[Service]
User=your_ubuntu_user
Group=www-data
WorkingDirectory=/var/www/all_in_one
Environment="PATH=/var/www/all_in_one/.venv/bin"
# 根据核心数调整 workers，通常为 2n+1
ExecStart=/var/www/all_in_one/.venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 127.0.0.1:8001

[Install]
WantedBy=multi-user.target
```

启动并设置开机自启：
```bash
sudo systemctl start club-backend
sudo systemctl enable club-backend
```

## 5. 前端部署

1. **构建前端**:
   ```bash
   cd /var/www/all_in_one/frontend
   # 创建前端生产环境变量
   echo "VITE_API_BASE_URL=/api" > .env.production
   npm install
   npm run build
   ```

## 6. Nginx 配置 (反向代理)

创建 Nginx 配置：`sudo nano /etc/nginx/sites-available/club_system`

```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    # 前端静态文件
    location / {
        root /var/www/all_in_one/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Swagger 文档代理 (可选)
    location /docs {
        proxy_pass http://127.0.0.1:8001/docs;
    }
}
```

启用配置并重启 Nginx：
```bash
sudo ln -s /etc/nginx/sites-available/club_system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 7. 安全建议 (可选)

- **HTTPS**: 使用 Certbot 获取免费 SSL 证书。
  ```bash
  sudo apt install certbot python3-certbot-nginx
  sudo certbot --nginx -d your_domain.com
  ```
- **防火墙**: 仅开放 80, 443 和 SSH 端口。
  ```bash
  sudo ufw allow 'Nginx Full'
  sudo ufw allow OpenSSH
  sudo ufw enable
  ```

---
© 2024 Club Management System Deployment Guide
