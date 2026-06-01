# Kiểm tra sức khỏe project

Chạy các kiểm tra Django để phát hiện lỗi cấu hình, migration chưa chạy, và vấn đề khác.

## Bước 1: Django system check

```powershell
python manage.py check --deploy 2>&1 | head -50
```

Giải thích kết quả:
- `System check identified no issues` → OK
- `WARNINGS` → xem xét nhưng không chặn chạy
- `ERRORS` → phải fix trước khi deploy

## Bước 2: Kiểm tra migrations

```powershell
python manage.py showmigrations
```

Tìm dấu `[ ]` (chưa chạy) — nếu có cần chạy:
```powershell
python manage.py migrate
```

## Bước 3: Kiểm tra migrations chưa tạo

```powershell
python manage.py makemigrations --check --dry-run
```

Nếu có output → có model thay đổi chưa tạo migration. Cần:
```powershell
python manage.py makemigrations
python manage.py migrate
```

## Bước 4: Kiểm tra static files

```powershell
python manage.py collectstatic --dry-run --noinput 2>&1 | tail -5
```

## Bước 5: Kiểm tra server có start được không

```powershell
python manage.py check
```

## Tóm tắt kết quả

Báo cáo ngắn gọn:
- Django check: OK / có lỗi (liệt kê)
- Migrations pending: có / không
- Model changes chưa migrate: có / không
- Static files: OK / có vấn đề

## Lưu ý

Trên VPS dùng `python3` thay `python` và kích hoạt venv trước:
```bash
source venv/bin/activate
python3 manage.py check
```
