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
   sudo git clone git@github.com:Warm-CN/all-in-one.git
   sudo chown -R $USER:$USER all-in-one
   cd all-in-one
   ```

2. **后端环境**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn uvicorn
   ```

3. **配置环境变量**:
   创建 `.env` 文件并填入测试预览环境配置：
   ```text
   DEBUG=True # 测试环境开启调试模式以方便查看报错
   DB_HOST=localhost
   DB_USER=club_user
   DB_PASSWORD=your_strong_password
   DB_NAME=club_management
   SECRET_KEY=<运行 python -c "import secrets; print(secrets.token_hex(32))" 生成>
   BACKEND_CORS_ORIGINS=http://your_domain.com,https://your_domain.com
   ```
   > **重要**：`SECRET_KEY` 和 `DB_PASSWORD` 不能为空或使用默认值，否则应用将拒绝启动。

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
WorkingDirectory=/var/www/all-in-one
Environment="PATH=/var/www/all-in-one/.venv/bin"
# 根据核心数调整 workers，通常为 2n+1
ExecStart=/var/www/all-in-one/.venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 127.0.0.1:8001

[Install]
WantedBy=multi-user.target
```

启动并设置开机自启：
```bash
sudo systemctl start club-backend
sudo systemctl enable club-backend
# 检查服务状态，确保正常运行
sudo systemctl status club-backend
```

**重要提示**：如果服务启动失败，使用以下命令查看详细错误日志：
```bash
sudo journalctl -u club-backend -n 50
```

## 5. 前端部署

### 方案 A：在服务器上构建（需要较高配置）
1. **构建前端**:
   ```bash
   cd /var/www/all-in-one/frontend
   # 创建前端生产环境变量
   echo "VITE_API_BASE_URL=" > .env.production
   npm install
   npm run build
   ```

### 方案 B：在本地 Windows 构建后上传（适用于低配置服务器）

如果服务器内存不足无法运行 `npm install` 或 `npm run build`，可以在本地构建后上传：

1. **在本地项目根目录创建环境变量文件**（Windows PowerShell）：
   ```powershell
   cd D:\code\python\all-in-one\frontend
   ```

2. **本地构建**：
   ```powershell
   npm run build
   ```

3. **上传到服务器**（使用 SCP 或 SFTP 工具如 WinSCP、FileZilla）：
   - 将整个 `frontend/dist` 文件夹上传到服务器的 `/var/www/all-in-one/frontend/dist`
   - 或者使用命令行（需要安装 OpenSSH）：
     ```powershell
     scp -r dist root@your_server_ip:/var/www/all-in-one/frontend/
     ```

4. **验证上传成功**：
   ```bash
   # 在服务器上执行
   ls -la /var/www/all-in-one/frontend/dist
   sudo systemctl reload nginx
   ```

## 6. Nginx 配置 (反向代理)

创建 Nginx 配置：`sudo nano /etc/nginx/sites-available/club_system`

```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    # 前端静态文件
    location / {
        root /var/www/all-in-one/frontend/dist;
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

## 7. 故障排查

### 问题：前端能显示但登录时提示"网络连接失败"

**原因**：前端无法连接到后端 API，通常是后端服务未启动或 Nginx 配置错误。

**排查步骤**：

1. **检查后端服务状态**：
   ```bash
   sudo systemctl status club-backend
   ```
   如果显示 `active (running)` 则正常，否则查看错误日志：
   ```bash
   sudo journalctl -u club-backend -n 50
   ```

2. **测试后端是否可访问**：
   ```bash
   curl http://127.0.0.1:8001/docs
   ```
   应该返回 HTML 内容。如果返回错误，说明后端未正常运行。

3. **检查 Nginx 日志**：
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```
   尝试登录时查看是否有 502/504 错误。

4. **常见修复方法**：
   - 后端未启动：`sudo systemctl restart club-backend`
   - .env 配置错误：检查数据库连接信息是否正确
   - 端口冲突：确认 8001 端口未被其他程序占用 `sudo lsof -i :8001`
   - Systemd 服务文件中的 `User` 字段需要改为实际的 Ubuntu 用户名

5. **如果后端服务正常但前端仍连接失败**：
   
   在浏览器按 `F12` 打开开发者工具 → Network 标签，尝试登录并查看失败的请求：
   - 如果请求 URL 是 `http://your_ip/api/auth/login`（正确）
   - 如果请求 URL 是 `http://localhost:8001/api/auth/login`（错误，说明前端配置问题）
   
   **解决方法**：确保前端构建时使用了正确的环境变量：
   ```bash
   cd /var/www/all-in-one/frontend
   cat .env.production  
   echo "VITE_API_BASE_URL=" > .env.production
   npm run build
   sudo systemctl reload nginx
   ```

6. **测试 Nginx 代理是否正常工作**：
   ```bash
   curl -X POST http://your_server_ip/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"student_id":"test","password":"test"}'
   ```
   应该返回 JSON 响应（即使用户名密码错误，也应该有响应）。如果返回 502/404，说明 Nginx 配置有问题。

### 问题：浏览器请求仍然指向 localhost:8000

**现象**：浏览器开发者工具显示请求 URL 为 `http://localhost:8000/api/...` 而不是服务器 IP。

**原因**：前端构建时环境变量未生效，仍使用代码中的默认配置。

**解决方法（适用于低配置服务器，本地构建方式）**：

1. **在本地 Windows 检查并创建环境变量文件**：
   ```powershell
   cd D:\code\python\all-in-one\frontend
   # 检查文件是否存在
   Get-Content .env.production
   # 如果不存在或内容错误，创建/覆盖
   echo "VITE_API_BASE_URL=/api" > .env.production
   ```

2. **删除旧构建并重新构建**：
   ```powershell
   Remove-Item -Recurse -Force dist
   npm run build
   ```

3. **上传新的 dist 文件夹到服务器**（覆盖旧的）

4. **在服务器重启 Nginx**：
   ```bash
   sudo systemctl reload nginx
   ```

5. **强制刷新浏览器**（Ctrl+F5），请求 URL 应改为服务器 IP。

## 8. 安全建议 (可选)

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
© 2026 Club Management System Deployment Guide
