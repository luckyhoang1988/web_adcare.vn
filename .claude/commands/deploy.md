# Deploy lên GitHub và VPS

Thực hiện đầy đủ quy trình: commit code local → push GitHub → hướng dẫn deploy VPS.

## Bước 1: Kiểm tra thay đổi

Chạy `git status` và `git diff --stat` để xem files đã sửa.

## Bước 2: Commit và push

- Stage các file liên quan (không stage `.env`, `media/`, `db.sqlite3`, `staticfiles/`, `__pycache__/`, file ảnh rời)
- Viết commit message ngắn gọn mô tả thay đổi, thêm `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
- Push lên `origin master`

## Bước 3: Kiểm tra có migration mới không

So sánh `apps/*/migrations/` với commit trước. Nếu có file migration mới → cần chạy `migrate` trên VPS.

## Bước 4: In hướng dẫn VPS

In ra đúng lệnh cần chạy trên VPS (SSH vào với user `adcare`, project tại `/home/adcare/web_adcare.vn`):

```bash
su - adcare
cd web_adcare.vn
source venv/bin/activate
git pull origin master
pip install -r requirements.txt        # chỉ khi requirements.txt thay đổi
python3 manage.py migrate              # chỉ khi có migration mới
python3 manage.py collectstatic --noinput
sudo systemctl restart adcare.service
```

Nếu có migration thêm field `unique=True` vào bảng đã có data → cảnh báo người dùng về nguy cơ `IntegrityError` và hướng dẫn dùng quy trình fix-migration.

## Lưu ý

- **KHÔNG push** `.env`, `media/`, `db.sqlite3`, `staticfiles/`
- Luôn chạy `python manage.py check` trước khi commit nếu có thay đổi model/view
- Sau khi VPS restart, kiểm tra `https://adcare.vn` hoạt động bình thường
