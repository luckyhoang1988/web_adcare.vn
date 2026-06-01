# Xóa Django Cache

Xóa toàn bộ cache Django (menu, site config, context processor).

## Khi nào cần dùng

- Vừa sửa **MenuItem** trong admin nhưng navbar chưa cập nhật
- Vừa sửa **SiteConfig** (logo, phone, email) nhưng chưa thấy thay đổi
- Vừa thêm **AboutSection** có `auto_add_menu=True` nhưng menu chưa có
- Vừa chỉnh **context_processors.py** nhưng chưa có hiệu lực
- Sau khi sửa code context processor cần test ngay

## Lệnh

Chạy lệnh này trong thư mục gốc của project (nơi có `manage.py`):

```powershell
python manage.py shell -c "from django.core.cache import cache; cache.clear(); print('Cache đã xóa thành công.')"
```

## Xác nhận

Sau khi chạy, reload trang web để kiểm tra thay đổi đã có hiệu lực.

## Lưu ý

- Cache tự động xóa khi save **MenuItem** hoặc **AboutSection** (qua `post_save` signal trong models)
- Nếu dùng trên VPS, cần kích hoạt venv trước: `source venv/bin/activate`
- Cache TTL mặc định: 3600 giây (1 giờ) — nếu không muốn đợi, dùng lệnh trên
- Trên production, sau khi xóa cache trang web sẽ build lại cache ở request đầu tiên (chậm hơn 1 chút)
