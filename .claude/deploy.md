# Deploy VPS — Thông số cụ thể

> File này chứa thông số deploy thực tế cho **adcare.vn**. Đọc file này để pull/deploy mà **không cần hỏi lại password**.
> Quy trình generic xem `.claude/commands/deploy.md` (skill `/deploy`).

## Thông số kết nối

| | |
|---|---|
| Host | `103.245.236.207` |
| User | `adcare` |
| Project | `/home/adcare/web_adcare.vn` |
| venv | `. venv/bin/activate` |
| Service | `adcare.service` (systemd, Gunicorn) |
| Domain | https://adcare.vn |
| GitHub | https://github.com/luckyhoang1988/web_adcare.vn (branch `master`) |

## Đã thiết lập sẵn (không cần password)

- **SSH key** `id_ed25519` (máy local Windows) đã nằm trong `~/.ssh/authorized_keys` của adcare → mọi lệnh `ssh adcare@103.245.236.207 "..."` chạy passwordless.
- **NOPASSWD sudo** cho service qua `/etc/sudoers.d/adcare-deploy`:
  `systemctl restart|reload|is-active|status adcare.service` → chạy `sudo -n` không cần password.
- Login vào bằng SSH là user `adcare` luôn — **KHÔNG cần `su - adcare`**.

## Deploy — chạy 2 lệnh (PowerShell trên máy local)

**1. Push code local lên GitHub** (nếu có thay đổi chưa push):
```powershell
git push origin master
```

**2. Pull + migrate + collectstatic + restart trên VPS** (một lệnh, passwordless):
```powershell
ssh -o BatchMode=yes adcare@103.245.236.207 "cd ~/web_adcare.vn && . venv/bin/activate && git pull origin master && python3 manage.py migrate --noinput && python3 manage.py collectstatic --noinput && sudo -n systemctl restart adcare.service && sleep 2 && sudo -n systemctl is-active adcare.service && echo ===DEPLOY_DONE==="
```

**3. Xác minh:**
```powershell
(Invoke-WebRequest https://adcare.vn -UseBasicParsing -TimeoutSec 20).StatusCode   # mong đợi 200
```

## Lệnh tùy chọn (chỉ khi cần)

Thêm vào chuỗi lệnh ở bước 2 khi áp dụng:

| Khi nào | Lệnh thêm |
|---------|-----------|
| `requirements.txt` đổi | `pip install -r requirements.txt &&` |
| Image fields đổi | `python3 manage.py generateimages &&` |
| Dùng Redis (`REDIS_URL` trong `.env`) | `python3 manage.py shell -c "from django.core.cache import cache; cache.clear()" &&` |

> Cache mặc định là **LocMemCache** (per-process) → tự xóa khi restart service. Chỉ cần `cache.clear()` thủ công khi dùng Redis.

## Lưu ý

- **KHÔNG bao giờ ghi password vào file này** hay commit lên GitHub (xem nguyên tắc bảo mật .env).
- Migration chỉ thêm `db_index` (CREATE INDEX) → an toàn chạy `migrate` thẳng. Nếu migration thêm `unique=True` vào bảng có data → dùng `/fix-migration` (`.claude/commands/fix-migration.md`).
- Dòng đỏ "NativeCommandError" trong PowerShell khi chạy ssh thường chỉ là git/stderr progress, không phải lỗi thật — kiểm tra có `===DEPLOY_DONE===` ở cuối.
- Nếu cần password (lần đầu trên máy khác chưa có key): login password user adcare; cài lại key bằng `plink` (PuTTY tại `C:\Program Files\PuTTY\plink.exe`, dùng `-pw`).
