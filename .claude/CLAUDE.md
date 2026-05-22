# CLAUDE.md

Hướng dẫn cho Claude Code khi làm việc với dự án này.

## Commands

```powershell
# Dev server
python manage.py runserver

# Migrations (bắt buộc sau khi sửa model)
python manage.py makemigrations
python manage.py migrate

# Production
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py generateimages   # generate mobile image cache (django-imagekit)
```

**Local:** `http://localhost:8000` · Admin: `http://localhost:8000/admin` — `admin` / `adcare@2024`

**Production:** `https://adcare.vn` · VPS user `adcare` · project `/home/adcare/web_adcare.vn`

### Deploy lên VPS

```bash
su - adcare                              # ← LUÔN chuyển sang user adcare trước
cd web_adcare.vn
git pull origin master
python3 manage.py migrate                # nếu có migration mới
python3 manage.py generateimages         # nếu có thay đổi image fields
sudo systemctl restart adcare.service
```

> **Lưu ý VPS:** Dùng `python3` (không phải `python`). Phải kích hoạt venv trước khi chạy lệnh Python: `source venv/bin/activate`

### Fix quyền media (403 Forbidden trên ảnh)

```bash
find media/ -type d -exec chmod 755 {} \;
find media/ -type f -exec chmod 644 {} \;
```

---

## Stack

**Django 5.2 LTS** · Jazzmin Admin · Bootstrap 5.3 · PostgreSQL (prod) / SQLite (dev)
- `django-resized` — resize ảnh khi upload
- `django-imagekit` — tạo mobile image variants tự động
- `django-ckeditor` — rich text editor trong admin
- `python-decouple` — đọc config từ `.env`
- `whitenoise` — serve static files

---

## Apps (`apps/`)

Đăng ký với prefix `apps.*` trong `INSTALLED_APPS`.

| App | Models chính |
|-----|-------------|
| `core` | `SiteConfig` · `Slider` · `StatItem` · `AboutSection` · `AboutFeature` · **`MenuItem`** |
| `products` | `ProductCategory` → `Product` → `ProductImage` |
| `services` | `ServiceCategory` → `Service` |
| `news` | `NewsCategory` → `Article` (status: draft/published) |
| `projects` | `ProjectCategory` → `Project` → `ProjectImage` |
| `partners` | `Partner` (logo carousel — không có urls.py riêng) |
| `contact` | `ContactMessage` + `ContactForm` |

---

## Models quan trọng

### SiteConfig — Singleton (pk=1)
Truy cập qua `SiteConfig.get()`. Inject vào mọi template qua context processor.

### MenuItem — Menu điều hướng động
Quản lý menu navbar từ Admin → **Menu chính**.

**Fields:** `title`, `item_type`, `url`, `parent` (FK self), `dropdown_style`, `icon`, `description`, `order`, `is_active`, `open_in_new_tab`

**`item_type`:** `home` · `about` · `products` · `services` · `projects` · `news` · `contact` · `custom`

**`dropdown_style`** (khi menu cha có menu con):
- `list` — danh sách dọc đơn giản
- `grid` — lưới 2 cột có icon
- `mega` — 2 cột với icon + mô tả

Menu con thêm qua inline trong admin. Menu `products`/`services` luôn dùng dropdown danh mục tự động (bỏ qua `dropdown_style`).

### AboutSection — nội dung soạn thảo bằng CKEditor
Field `content` dùng CKEditorWidget. Template render bằng `{{ about.content|safe }}` (không dùng `|linebreaks`).

---

## Context Processor (`apps/core/context_processors.py`)

Cache 3600s, inject vào **mọi template**:

| Biến | Dùng cho |
|------|----------|
| `{{ site_config }}` | Logo, phone, email, social links |
| `{{ nav_menu }}` | Danh sách MenuItem cấp 1 (có prefetch children) |
| `{{ nav_categories }}` | Dropdown sản phẩm — ProductCategory |
| `{{ nav_service_categories }}` | Dropdown dịch vụ — ServiceCategory |
| `{{ footer_services }}` | Dịch vụ hiển thị footer (6 item) |

**Xóa cache sau khi sửa menu/config:** `python manage.py shell -c "from django.core.cache import cache; cache.clear()"`

---

## Templates

`templates/` toàn cục — tất cả kế thừa `base.html`. Components dùng chung: `templates/components/` (navbar, footer, breadcrumb).

**Blocks quan trọng trong `base.html`:**

| Block | Mục đích |
|-------|----------|
| `{% block title %}` | `<title>` |
| `{% block meta_desc %}` | meta description |
| `{% block og_tags %}` | Open Graph — dùng `{{ block.super }}` để kế thừa |
| `{% block json_ld %}` | JSON-LD structured data |
| `{% block extra_css %}` / `{% block extra_js %}` | CSS/JS per-page |

**Page header:**
```html
<div class="page-header text-center">
  <div class="container"><h1>Tiêu đề</h1></div>
</div>
```
Không dùng inline style — `mobile.css` tự override responsive.

---

## Hình ảnh

### Upload & Resize
`ResizedImageField` (django-resized) tự resize khi upload. Kích thước per-field trong model.

### Mobile variants (django-imagekit)
Mỗi model có ảnh đều có `image_mobile = ImageSpecField(...)` tự tạo bản mobile nhỏ hơn.

Kích thước mobile:
| Model | Desktop | Mobile |
|-------|---------|--------|
| Slider | 1920×800 | 576×400 |
| Product/Service | 800×600 | 480×360 |
| Article | 1200×630 | 576×302 |
| Project | 900×600 | 480×320 |

**Template dùng `<picture>` element:**
```html
<picture>
  <source media="(max-width: 575px)" srcset="{{ obj.image_mobile.url }}">
  <img src="{{ obj.image.url }}" alt="...">
</picture>
```

**Sau khi deploy hoặc upload ảnh mới trên VPS:**
```bash
python3 manage.py generateimages
```

---

## Static Files

| File | Nội dung |
|------|----------|
| `main.css` | CSS variables, buttons, cards, utilities, dropdown-grid, dropdown-mega |
| `navbar.css` | Navbar, top-bar, dropdown |
| `hero.css` | Hero slider |
| `footer.css` | Footer 4 cột |
| `mobile.css` | **Tất cả responsive overrides** |

**CSS variables chính** (định nghĩa trong `main.css`):

| Variable | Giá trị | Dùng cho |
|----------|---------|----------|
| `--navy` | `#2e5c10` | Navbar, footer, page header |
| `--navy-dark` | `#1e3d0a` | Top bar, footer bottom |
| `--accent` | `#7db833` | Buttons, highlight |
| `--light` | `#f2f8ed` | Nền section xen kẽ |

Không hardcode màu hex trong templates — luôn dùng `var(--navy)`, `var(--accent)`, ...

---

## SEO

- **Google Search Console:** xác minh qua meta tag `base.html:11`
- **Sitemap:** `/sitemap.xml` — 5 content types
- **JSON-LD:** Organization schema trong `base.html`, detail pages override `{% block json_ld %}`
- **og:image:** detail pages override `{% block og_tags %}` với ảnh riêng

---

## .gitignore — KHÔNG commit

```
.env          ← credentials — tạo tay trên mỗi server
media/        ← user uploads
staticfiles/  ← generated by collectstatic
db.sqlite3    ← dev database
__pycache__/
```

---

## Lưu ý quan trọng

- **Migration:** luôn `makemigrations` + `migrate` sau khi sửa model
- **`is_active`:** hầu hết models có cờ này — query nên filter `is_active=True`
- **select_related:** dùng `select_related('category')` khi query FK — tránh N+1
- **prefetch_related:** dùng `prefetch_related('children')` cho MenuItem
- **Section spacing:** class `section-pad` (70px) / `section-pad-sm` (50px) — không inline padding
- **`get_absolute_url()`:** `Product` trả về `product_list` nếu không có category
- **Breadcrumb:** truyền `breadcrumbs` list vào context, mỗi phần tử có `name` và `url`
- **Thêm app mới:** đăng ký `apps.<tên>` trong `INSTALLED_APPS`, sửa `apps.py` cho đúng `name`
- **CKEditor content:** render bằng `|safe`, không dùng `|linebreaks`
- **Jazzmin logout:** render là `<form>` không phải `<a>` — style qua `#logout-form button.dropdown-item`
