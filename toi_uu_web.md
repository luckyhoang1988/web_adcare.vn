# Kế hoạch Tối ưu Web_adcare

## Context
Project là Django 5.2 website CMS cho ADCARE (camera an ninh). Sau khi deploy lên VPS, cần tối ưu về performance, SEO, và bảo mật. Không có REST API — đây là traditional Django website. Kế hoạch chia 3 giai đoạn theo mức độ ưu tiên.

---

## GIAI ĐOẠN 1 — Performance (Tác động lớn nhất)

### 1.1 Fix N+1 query trong HomeView
**File:** `apps/core/views.py`
- Thêm `.select_related('category')` cho `featured_products` và `recent_news`
- Thêm `.order_by('-published_at')` cho `recent_news` để lấy bài mới nhất

### 1.2 Fix race condition view_count
**File:** `apps/products/views.py`, `apps/news/views.py`
- Thay `product.view_count += 1; product.save()` bằng:
  `Product.objects.filter(pk=obj.pk).update(view_count=F('view_count') + 1)`
- Áp dụng cho cả Article

### 1.3 Cache context processor
**File:** `apps/core/context_processors.py`, `config/settings.py`
- Thêm `CACHES` vào settings dùng LocMemCache (không cần Redis)
- Wrap toàn bộ context processor với `cache.get/set` key `'global_nav'`, TTL 1 giờ

### 1.4 Fix N+1 trong Admin
**Files:** `apps/products/admin.py`, `apps/services/admin.py`, `apps/news/admin.py`, `apps/projects/admin.py`
- Thêm `list_select_related = ('category',)` vào 4 ModelAdmin

### 1.5 Thêm pagination cho ServiceListView
**File:** `apps/services/views.py`
- Thêm `paginate_by = 12`
- Cập nhật template `services/list.html` thêm pagination block

---

## GIAI ĐOẠN 2 — SEO

### 2.1 Open Graph + canonical tags
**File:** `templates/base.html`
- Thêm block `{% block og_tags %}` với default từ SiteConfig
- Các page template override block này với data riêng (title, description, image)
- Thêm `<link rel="canonical">` với `{{ request.build_absolute_uri }}`

### 2.2 Sitemap
**File:** `apps/core/sitemaps.py` (tạo mới), `config/urls.py`, `config/settings.py`
- Tạo sitemap cho: Product, Service, Article, Project, trang tĩnh
- Thêm `django.contrib.sitemaps` vào INSTALLED_APPS
- URL: `/sitemap.xml`

### 2.3 Robots.txt
**File:** `templates/robots.txt` (tạo mới), `config/urls.py`
- Disallow `/admin/`, Allow tất cả còn lại
- Thêm `Sitemap: https://adcare.vn/sitemap.xml`

---

## GIAI ĐOẠN 3 — Bảo mật & Chất lượng

### 3.1 Security headers cho production
**File:** `config/settings.py`
- Thêm (chỉ khi `DEBUG=False`):
  ```python
  SECURE_SSL_REDIRECT = True
  SESSION_COOKIE_SECURE = True
  CSRF_COOKIE_SECURE = True
  SECURE_HSTS_SECONDS = 31536000
  SECURE_HSTS_INCLUDE_SUBDOMAINS = True
  X_FRAME_OPTIONS = 'DENY'
  ```
- Đổi `DEBUG default=True` → `default=False`

### 3.2 Lazy loading ảnh
**Files:** Tất cả templates có `<img>` tag
- Thêm `loading="lazy"` vào tất cả ảnh ngoại trừ ảnh hero/above-the-fold

### 3.3 Logging
**File:** `config/settings.py`
- Thêm `LOGGING` config ghi lỗi ra `logs/django.log`
- Tạo thư mục `logs/` với `.gitkeep`

---

## Files cần sửa

| File | Thay đổi |
|------|----------|
| `config/settings.py` | CACHES, LOGGING, SECURITY, INSTALLED_APPS (sitemaps) |
| `config/urls.py` | Thêm sitemap URL, robots.txt URL |
| `apps/core/views.py` | select_related, order_by |
| `apps/core/context_processors.py` | Cache wrapping |
| `apps/core/sitemaps.py` | Tạo mới |
| `apps/products/views.py` | F() expression cho view_count |
| `apps/products/admin.py` | list_select_related |
| `apps/news/views.py` | F() expression cho view_count |
| `apps/news/admin.py` | list_select_related |
| `apps/services/views.py` | paginate_by |
| `apps/services/admin.py` | list_select_related |
| `apps/projects/admin.py` | list_select_related |
| `templates/base.html` | OG tags, canonical |
| `templates/robots.txt` | Tạo mới |
| Tất cả templates có img | loading="lazy" |

---

## Kiểm tra sau khi xong

1. Chạy `python manage.py runserver`, mở trang chủ → inspect Network tab → đếm số DB queries giảm
2. Truy cập `/sitemap.xml` → thấy danh sách URLs
3. Truy cập `/robots.txt` → thấy nội dung đúng
4. Dùng Facebook Sharing Debugger với `https://adcare.vn` → thấy OG image/title
5. Commit, push, `git pull` trên VPS + `sudo systemctl restart adcare`
