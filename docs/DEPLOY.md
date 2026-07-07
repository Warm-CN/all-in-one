# Ubuntu 服务器部署指南

本文档面向 Ubuntu 22.04/24.04 云服务器，部署方式为：

- Nginx 对外提供前端静态文件与反向代理。
- FastAPI 后端通过 Uvicorn 监听 `127.0.0.1:8001`。
- systemd 管理后端进程。
- MySQL 保存业务数据。

示例部署目录统一使用 `/var/www/all-in-one`。命令中的域名、用户名、数据库密码请替换为你的实际值。

## 1. 部署前检查

需要准备：

| 项 | 示例 |
|----|------|
| 服务器系统 | Ubuntu 22.04 LTS 或 24.04 LTS |
| 域名 | `club.example.com`，没有域名可先用公网 IP |
| 后端端口 | `127.0.0.1:8001` |
| 前端目录 | `/var/www/all-in-one/frontend/dist` |
| 数据库 | `club_management` |
| 数据库用户 | `club_user` |

安全组/防火墙至少开放：

- `22/tcp`：SSH
- `80/tcp`：HTTP
- `443/tcp`：HTTPS

不要把 `8001` 暴露到公网。

## 2. 安装系统依赖

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y git curl nginx mysql-server python3 python3-venv python3-pip
```

安装 Node.js 20：

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node -v
npm -v
```

## 3. 配置 MySQL

建议先执行安全初始化：

```bash
sudo mysql_secure_installation
```

创建数据库与应用用户：

```bash
sudo mysql
```

```sql
CREATE DATABASE club_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'club_user'@'localhost' IDENTIFIED BY 'replace_with_strong_password';
GRANT ALL PRIVILEGES ON club_management.* TO 'club_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

验证登录：

```bash
mysql -u club_user -p club_management
```

## 4. 获取代码

```bash
sudo mkdir -p /var/www
sudo chown -R $USER:www-data /var/www
cd /var/www
git clone git@github.com:Warm-CN/all-in-one.git
cd /var/www/all-in-one
```

如果服务器没有配置 GitHub SSH Key，也可以用 HTTPS 仓库地址。

创建上传目录并授权：

```bash
mkdir -p uploads
sudo chown -R $USER:www-data /var/www/all-in-one
sudo chmod -R 750 /var/www/all-in-one
sudo chmod -R 770 /var/www/all-in-one/uploads
```

## 5. 后端环境

```bash
cd /var/www/all-in-one
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel
pip install -r requirements.txt
```

创建生产环境变量：

```bash
cp .env.example .env
nano .env
```

推荐配置：

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=club_user
DB_PASSWORD=replace_with_strong_password
DB_NAME=club_management
DB_ECHO=False

SECRET_KEY=replace_with_random_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

DEBUG=False
APP_NAME=社团统一管理系统
APP_VERSION=1.0.0

BACKEND_CORS_ORIGINS=https://club.example.com,http://club.example.com
```

生成 `SECRET_KEY`：

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

启动前自检：

```bash
python -c "from app.core.config import settings; print(settings.APP_NAME, settings.DB_NAME)"
```

首次部署空库时，应用启动会自动创建数据表。先用命令手动启动一次确认：

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

另开一个 SSH 窗口测试：

```bash
curl http://127.0.0.1:8001/health
```

看到 `{"status":"healthy",...}` 后按 `Ctrl+C` 停止临时进程。

创建管理员账号：

```bash
python scripts/init_admin.py
```

默认管理员为 `110 / 654321`，上线后立即登录修改密码。

生产环境不要运行 `scripts/rebuild_database.py`，它会删除全部表。

## 6. systemd 后端服务

创建服务文件：

```bash
sudo nano /etc/systemd/system/club-backend.service
```

写入：

```ini
[Unit]
Description=Club Management FastAPI Backend
After=network.target mysql.service

[Service]
Type=simple
User=your_ubuntu_user
Group=www-data
WorkingDirectory=/var/www/all-in-one
EnvironmentFile=/var/www/all-in-one/.env
Environment=PYTHONUNBUFFERED=1
ExecStart=/var/www/all-in-one/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

把 `your_ubuntu_user` 改为当前部署用户，可用 `whoami` 查看。

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable club-backend
sudo systemctl start club-backend
sudo systemctl status club-backend
```

查看日志：

```bash
sudo journalctl -u club-backend -n 100 --no-pager
sudo journalctl -u club-backend -f
```

## 7. 前端构建

服务器构建：

```bash
cd /var/www/all-in-one/frontend
printf "VITE_API_BASE_URL=\n" > .env.production
npm ci
npm run build
```

如果服务器内存较小，可以在本地构建后上传 `frontend/dist` 到服务器同一路径。无论在哪里构建，都要确保构建前存在：

```env
VITE_API_BASE_URL=
```

否则生产包可能会请求 `localhost:8001`。

授权 Nginx 读取静态文件：

```bash
sudo chown -R $USER:www-data /var/www/all-in-one/frontend/dist
sudo chmod -R 750 /var/www/all-in-one/frontend/dist
```

## 8. Nginx 配置

创建站点配置：

```bash
sudo nano /etc/nginx/sites-available/club-system
```

写入：

```nginx
server {
    listen 80;
    server_name club.example.com;

    client_max_body_size 20m;

    root /var/www/all-in-one/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads/ {
        proxy_pass http://127.0.0.1:8001/uploads/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://127.0.0.1:8001/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /redoc {
        proxy_pass http://127.0.0.1:8001/redoc;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8001/openapi.json;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8001/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

没有域名时，把 `server_name` 改为服务器公网 IP 或 `_`。

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/club-system /etc/nginx/sites-enabled/club-system
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

测试：

```bash
curl http://club.example.com/health
curl http://club.example.com/api/v1/auth/login
```

第二条即使返回 `405 Method Not Allowed` 也说明代理已经到达后端，因为登录接口要求 POST。

## 9. HTTPS

有域名后安装证书：

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d club.example.com
```

验证自动续期：

```bash
sudo certbot renew --dry-run
```

启用 HTTPS 后，把 `.env` 中的 `BACKEND_CORS_ORIGINS` 更新为 HTTPS 域名，并重启后端：

```bash
sudo systemctl restart club-backend
```

## 10. 日常升级

升级前先备份：

```bash
mkdir -p ~/club-backups
mysqldump -u club_user -p club_management > ~/club-backups/club_management_$(date +%F_%H%M%S).sql
tar -czf ~/club-backups/uploads_$(date +%F_%H%M%S).tar.gz -C /var/www/all-in-one uploads
cp /var/www/all-in-one/.env ~/club-backups/env_$(date +%F_%H%M%S).txt
chmod 600 ~/club-backups/env_*.txt
```

拉取并更新：

```bash
cd /var/www/all-in-one
git pull
source .venv/bin/activate
pip install -r requirements.txt
```

如果本次代码包含数据库结构变更，先阅读迁移脚本并在备份后执行相应迁移。当前项目的 Alembic 历史不是完整建库脚本，不建议在未确认的生产库上盲目执行。

重建前端：

```bash
cd /var/www/all-in-one/frontend
printf "VITE_API_BASE_URL=\n" > .env.production
npm ci
npm run build
```

重启服务：

```bash
sudo systemctl restart club-backend
sudo systemctl reload nginx
curl http://127.0.0.1:8001/health
```

## 11. 回滚

代码回滚：

```bash
cd /var/www/all-in-one
git log --oneline -5
git checkout <previous_commit>
source .venv/bin/activate
pip install -r requirements.txt
cd frontend
npm ci
npm run build
sudo systemctl restart club-backend
sudo systemctl reload nginx
```

数据库回滚只在明确需要时执行。先停止服务，再恢复备份：

```bash
sudo systemctl stop club-backend
mysql -u club_user -p club_management < ~/club-backups/club_management_YYYY-MM-DD_HHMMSS.sql
sudo systemctl start club-backend
```

## 12. 常见故障

### systemd 启动失败

```bash
sudo systemctl status club-backend
sudo journalctl -u club-backend -n 100 --no-pager
```

重点检查：

- `.env` 是否存在于 `/var/www/all-in-one/.env`。
- `DB_PASSWORD` 和 `SECRET_KEY` 是否为空。
- MySQL 用户和密码是否正确。
- `User=` 是否为真实 Linux 用户。
- `uploads/` 是否可写。

### Nginx 返回 502

```bash
curl http://127.0.0.1:8001/health
sudo tail -n 100 /var/log/nginx/error.log
```

如果本机 health 不通，先修后端。若本机通但 Nginx 502，检查 `proxy_pass` 是否为 `http://127.0.0.1:8001`，并确认服务没有监听到其他端口。

### 前端能打开但登录失败

在浏览器开发者工具 Network 查看请求地址：

- 正确：`https://club.example.com/api/v1/auth/login`
- 错误：`http://localhost:8001/api/v1/auth/login`

修复：

```bash
cd /var/www/all-in-one/frontend
printf "VITE_API_BASE_URL=\n" > .env.production
npm run build
sudo systemctl reload nginx
```

然后浏览器强制刷新。

### 访问子路由 404

确认 Nginx `location /` 中包含：

```nginx
try_files $uri $uri/ /index.html;
```

这是 Vue Router history 模式必须配置的 SPA 回退。

### 上传或导入文件失败

检查：

- Nginx `client_max_body_size 20m;`
- `uploads/` 目录权限：`ls -ld /var/www/all-in-one/uploads`
- 后端日志：`sudo journalctl -u club-backend -f`

### CORS 报错

同域部署通常不需要跨域。若前后端分域部署，后端 `.env` 的 `BACKEND_CORS_ORIGINS` 必须包含前端完整来源，例如：

```env
BACKEND_CORS_ORIGINS=https://club.example.com,https://www.club.example.com
```

修改后重启：

```bash
sudo systemctl restart club-backend
```

## 13. 安全建议

- 上线后立即修改默认管理员密码。
- `.env` 不要提交到 Git，也不要放进可公开下载目录。
- MySQL 用户只授予当前数据库权限。
- 后端只监听 `127.0.0.1`。
- 定期备份数据库和 `uploads/`。
- 启用 HTTPS 后优先使用 HTTPS 域名访问系统。
- 生产环境保持 `DEBUG=False`。
