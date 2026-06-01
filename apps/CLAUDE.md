# Rules cho `apps/` — Django Backend Code

## Models

### Bắt buộc cho mọi model nội dung
```python
is_active = models.BooleanField(default=True)
order = models.PositiveSmallIntegerField(default=0)
created_at = models.DateTimeField(auto_now_add=True)
```

### Slug — luôn dùng vi_slugify, không dùng slugify Django
```python
from apps.core.models import vi_slugify
# KHÔNG: from django.utils.text import slugify
# Lý do: slugify Django xóa dấu nhưng giữ ký tự lạ; vi_slugify cho kết quả ASCII sạch
```

### Image fields — luôn có cả desktop và mobile
Mọi model có `image` (ResizedImageField) phải có thêm `image_mobile` (ImageSpecField). Không được có image field đơn lẻ.

### QuerySet defaults
- Filter `is_active=True` trong mọi public view
- Dùng `select_related('category')` khi có FK để tránh N+1
- Dùng `prefetch_related('children')` cho MenuItem
- Không dùng `all()` không có filter trên public views

### Admin
- **LUÔN** kế thừa `DuplicateMixin` từ `apps/core/admin_utils.py`
- **Nếu model feed vào `global_nav`** (Category, Menu, SiteConfig, Service…) → kế thừa thêm `ClearMenuCacheMixin` (đặt trước `DuplicateMixin` trong MRO)
- `list_editable` phải bao gồm `is_active` và `order`
- `copy_link` trong `list_display` (từ DuplicateMixin)
- `prepopulated_fields = {'slug': ('name',)}` hoặc `('title',)`
- `list_per_page = 25` cho admin nội dung nhiều bản ghi

### Migrations
- Chạy ngay sau khi sửa model: `python manage.py makemigrations && python manage.py migrate`
- Thêm `unique=True` vào bảng có data → dùng quy trình trong CLAUDE.md gốc
- **Không** chỉnh sửa file migration đã commit

## Views

### ListView — pattern chuẩn
```python
paginate_by = 9  # LUÔN dùng 9
# Thêm pagination_base_url vào context (xem CLAUDE.md gốc)
# select_related category
# filter is_active=True
```

### Không làm trong views
- Không import trực tiếp model từ app khác (dùng context processor)
- Không hardcode strings tiếng Việt trong views (dùng verbose_name trong models)
- Không dùng `Model.objects.all()` không có filter trong public views

## App Registration
- INSTALLED_APPS: `'apps.<tên>'` (không bỏ prefix `apps.`)
- `apps.py` phải có `name = 'apps.<tên>'` (không phải chỉ `'<tên>'`)
- URL prefix trong `config/urls.py`: dùng tiếng Việt không dấu

## Context Processor
Khi cần inject data mới vào mọi template (menu, footer, v.v.):
- Sửa `apps/core/context_processors.py`
- Data gói trong 1 cache key `global_nav` (TTL **86400s = 24h**)
- **Nếu data mới đến từ model sửa được trong admin** → ModelAdmin tương ứng phải dùng `ClearMenuCacheMixin` để xóa `global_nav` (nếu không, thay đổi không hiện ra tới 24h)
- Xóa cache thủ công: `python manage.py shell -c "from django.core.cache import cache; cache.clear()"`
