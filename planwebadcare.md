# Kế hoạch Deploy Django lên VPS (Ubuntu 22.04)

## Context
Project `Web_adcare` là Django 5.2 với PostgreSQL, WhiteNoise, Jazzmin. Cần deploy lên VPS Ubuntu 22.04, truy cập qua IP (không domain, không SSL).
Stack production: **Nginx → Gunicorn → Django**.

> **Quy ước ký hiệu:**
> - 💻 **[PC LOCAL]** — thực hiện trên máy tính Windows của bạn
> - 🖥️ **[VPS]** — thực hiện trên VPS sau khi SSH vào server

---

## Bước 1 — 💻 [PC LOCAL] Chuẩn bị code

### 1.1 Thêm `gunicorn` vào requirements.txt
Mở file `requirements.txt`, thêm dòng cuối:
```
Django==5.2
Pillow>=11.0
django-jazzmin>=3.0
python-decouple>=3.8
whitenoise>=6.7
django-resized>=1.0.2
psycopg2-binary>=2.9
dj-database-url>=2.0
gunicorn>=21.2                  ← THÊM DÒNG NÀY
```

### 1.2 Tạo `.gitignore` tại thư mục gốc project (hiện chưa có)
```
.env
*.pyc
__pycache__/
db.sqlite3
staticfiles/
media/
*.log
.DS_Store
```

### 1.3 Tạo `.env.example` để làm mẫu cho VPS
```
DEBUG=False
SECRET_KEY=your-strong-secret-key-here
DATABASE_URL=postgresql://adcare_user:password@localhost:5432/adcare_db
ALLOWED_HOSTS=your-vps-ip
```

### 1.4 Commit & push lên GitHub
```bash
git add .
git commit -m "Add gunicorn, gitignore for VPS deployment"
git push origin master
```

---

## Bước 2 — 🖥️ [VPS] SSH vào server & cài phần mềm

SSH vào VPS từ máy local trước:
```bash
# Chạy trên PC LOCAL (PowerShell hoặc Terminal)
ssh root@<ip-vps-của-bạn>
```

Sau khi đã vào VPS, chạy các lệnh sau:

### 2.1 Cập nhật hệ thống & cài phần mềm cần thiết
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git nginx postgresql postgresql-contrib
```

### 2.2 Tạo user hệ thống riêng (không dùng root để chạy app)
```bash
sudo adduser adcare
sudo usermod -aG sudo adcare
su - adcare        # chuyển sang user adcare
```

---

## Bước 3 — 🖥️ [VPS] Tạo database PostgreSQL

```bash
sudo -u postgres psql
```
Trong psql:
```sql
CREATE DATABASE adcare_db;
CREATE USER adcare_user WITH PASSWORD 'strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE adcare_db TO adcare_user;
\q
```

---

## Bước 4 — 🖥️ [VPS] Clone code & cài đặt project

```bash
cd /home/adcare
git clone https://github.com/luckyhoang1988/web_adcare.vn.git
cd web_adcare.vn

# Tạo virtualenv
python3 -m venv venv
source venv/bin/activate

# Cài dependencies (bao gồm gunicorn đã thêm ở Bước 1)
pip install -r requirements.txt
```

### 4.1 Tạo file `.env` production (KHÔNG commit file này lên git)
```bash
nano /home/adcare/web_adcare.vn/.env
```
Nội dung file `.env`:
```
DEBUG=False
SECRET_KEY=<tạo key mới bằng lệnh bên dưới>
DATABASE_URL=postgresql://adcare_user:strong_password_here@localhost:5432/adcare_db
ALLOWED_HOSTS=<ip-vps-của-bạn>
```
Tạo SECRET_KEY mới:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4.2 Chạy migrations, collectstatic, tạo superuser
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

---

## Bước 5 — 🖥️ [VPS] Cấu hình Gunicorn chạy tự động (Systemd)

```bash
sudo nano /etc/systemd/system/adcare.service
```
Nội dung file:
```ini
[Unit]
Description=Gunicorn daemon for Adcare
After=network.target

[Service]
User=adcare
Group=www-data
WorkingDirectory=/home/adcare/web_adcare.vn
ExecStart=/home/adcare/web_adcare.vn/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/home/adcare/web_adcare.vn/adcare.sock \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Kích hoạt Gunicorn:
```bash
sudo systemctl daemon-reload
sudo systemctl enable adcare
sudo systemctl start adcare
sudo systemctl status adcare   # kiểm tra đang chạy, phải thấy "active (running)"
```

---

## Bước 6 — 🖥️ [VPS] Cấu hình Nginx làm reverse proxy

```bash
sudo nano /etc/nginx/sites-available/adcare
```
Nội dung file:
```nginx
server {
    listen 80;
    server_name <ip-vps-của-bạn>;

    client_max_body_size 10M;

    location /static/ {
        alias /home/adcare/web_adcare.vn/staticfiles/;
    }

    location /media/ {
        alias /home/adcare/web_adcare.vn/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/adcare/web_adcare.vn/adcare.sock;
    }
}
```

Kích hoạt Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/adcare /etc/nginx/sites-enabled/
sudo nginx -t                  # kiểm tra config hợp lệ — phải thấy "syntax is ok"
sudo systemctl restart nginx

# Cấp quyền để Nginx đọc được socket file của Gunicorn
sudo usermod -aG adcare www-data
```

---

## Bước 7 — 🖥️ [VPS] Mở firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

---

## Kiểm tra sau deploy — 💻 [PC LOCAL]

Mở trình duyệt trên máy local, truy cập:

| URL | Mong đợi |
|-----|----------|
| `http://<ip-vps>/` | Trang chủ hiển thị bình thường |
| `http://<ip-vps>/admin/` | Jazzmin admin login |
| `http://<ip-vps>/static/main.css` | CSS tải được (status 200) |
| `http://<ip-vps>/media/<tên-ảnh>` | Ảnh upload tải được |

**Nếu lỗi, xem log trên VPS:**
```bash
# 🖥️ [VPS]
sudo journalctl -u adcare -n 50       # Gunicorn logs
sudo tail -f /var/log/nginx/error.log  # Nginx error logs
```

---

## Tóm tắt files thay đổi/tạo mới

| Nơi thực hiện | File | Hành động |
|---------------|------|-----------|
| 💻 PC LOCAL | `requirements.txt` | Thêm `gunicorn>=21.2` |
| 💻 PC LOCAL | `.gitignore` | Tạo mới |
| 💻 PC LOCAL | `.env.example` | Tạo mới |
| 🖥️ VPS | `/etc/systemd/system/adcare.service` | Tạo mới |
| 🖥️ VPS | `/etc/nginx/sites-available/adcare` | Tạo mới |
| 🖥️ VPS | `/home/adcare/web_adcare.vn/.env` | Tạo mới (không commit lên git) |
