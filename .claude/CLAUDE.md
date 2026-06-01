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

# Xóa cache (sau khi sửa menu/config)
python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

**Local:** `http://localhost:8000` · Admin: `http://localhost:8000/admin` — `admin` / `adcare@2024`

**Production:** `https://adcare.vn` · VPS user `adcare` · project `/home/adcare/web_adcare.vn`

### Deploy lên VPS

```bash
su - adcare                              # ← LUÔN chuyển sang user adcare trước
cd web_adcare.vn
source venv/bin/activate                 # ← BẮT BUỘC trước mọi lệnh python3
git pull origin master
pip install -r requirements.txt          # nếu có package mới
python3 manage.py migrate                # nếu có migration mới
python3 manage.py collectstatic --noinput
python3 manage.py generateimages         # nếu có thay đổi image fields
sudo systemctl restart adcare.service
```

> **Lưu ý VPS:** Dùng `python3` (không phải `python`). Phải kích hoạt venv trước: `source venv/bin/activate`

### Fix lỗi migration khi có data cũ trong DB (PostgreSQL)

Nếu migration thêm field `unique=True` vào bảng đã có data → lỗi `IntegrityError` hoặc `ProgrammingError`:

```bash
# Bước 1: Thêm cột thủ công (bỏ qua unique tạm thời)
python3 manage.py dbshell
```
```sql
ALTER TABLE <tên_bảng> ADD COLUMN IF NOT EXISTS <tên_cột> varchar(200) NOT NULL DEFAULT '';
\q
```
```bash
# Bước 2: Điền data cho cột mới
python3 manage.py shell -c "
from apps.<app>.models import <Model>, vi_slugify
for obj in <Model>.objects.all():
    base = vi_slugify(obj.title)
    slug = base; i = 2
    while <Model>.objects.filter(slug=slug).exclude(pk=obj.pk).exists():
        slug = f'{base}-{i}'; i += 1
    <Model>.objects.filter(pk=obj.pk).update(slug=slug)
print('Done')
"

# Bước 3: Thêm unique constraint
python3 manage.py dbshell
```
```sql
ALTER TABLE <tên_bảng> ADD CONSTRAINT <tên_constraint> UNIQUE (<tên_cột>);
\q
```
```bash
# Bước 4: Fake migration rồi chạy các migration còn lại
python3 manage.py migrate <app> <số_migration> --fake
python3 manage.py migrate
```

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

### AboutSection — Trang giới thiệu động
Mỗi section là một trang riêng với URL `/gioi-thieu/<slug>/`.

**Fields quan trọng:**
- `slug` — tự động tạo từ `title` qua `vi_slugify()` nếu để trống
- `auto_add_menu` — bật để tự tạo MenuItem trỏ đến trang này khi lưu
- `menu_parent` — chọn MenuItem cha (để trống = menu cấp 1)
- `menu_order` — thứ tự trong menu
- `meta_title`, `meta_desc` — SEO per-page
- `get_absolute_url()` — trả về `/gioi-thieu/<slug>/`
- `content` — CKEditor, render bằng `{{ about.content|safe }}` (không dùng `|linebreaks`)

**Template:** `templates/core/about_detail.html` · **View:** `AboutDetailView` tại `apps/core/views.py`

**`vi_slugify(text)`** — hàm trong `apps/core/models.py`, chuyển tiếng Việt có dấu thành slug ASCII. Không cần thư viện ngoài.

---

## Admin — Mixins & quản lý Menu

File: `apps/core/admin_utils.py` cung cấp 2 mixin: **`DuplicateMixin`** (sao chép) và **`ClearMenuCacheMixin`** (tự xóa `global_nav` khi save/delete — xem bảng Cache invalidation ở mục Context Processor).

**`DuplicateMixin`** — mixin cho ModelAdmin, thêm:
- Icon copy (🔵) mỗi row trong list → click mở form Add pre-filled (chưa lưu)
- Slug tự thêm `-copy`, name/title thêm `(Sao chép)`, `is_active=False`, `status='draft'`
- File/image fields bị bỏ qua (không thể pre-fill HTML form)

**`make_duplicate_action(label)`** — factory tạo bulk action "Sao chép ... đã chọn" (lưu ngay)

**Áp dụng cho:** `MenuItem` · `ProductCategory` · `Product` · `ServiceCategory` · `Service` · `NewsCategory` · `Article` · `ProjectCategory` · `Project`

```python
from apps.core.admin_utils import DuplicateMixin, make_duplicate_action

class MyAdmin(DuplicateMixin, admin.ModelAdmin):
    list_display = ('name', ..., 'copy_link')
    actions = [make_duplicate_action('tên loại')]
```

> **MRO khi kết hợp:** `class MyAdmin(ClearMenuCacheMixin, DuplicateMixin, admin.ModelAdmin)` — đặt `ClearMenuCacheMixin` trước.

### Quản lý Menu — `MenuItemAdmin` (apps/core/admin.py)

Trang **Menu chính** đã được tối ưu để thiết kế navbar trực quan:
- `title_tree` (icon + tên), `type_badge` (đánh dấu loại tự-sinh-dropdown), `submenu_info` (số + tên menu con), `link_target` (URL đích resolve), `onsite_link` (🔗 xem trên web)
- `list_editable = ('order', 'is_active')`, `search_fields`, `list_filter`, `list_per_page = 25`
- Action **"🔄 Làm mới menu ra website"** (`clear_menu_cache_action`) ép xóa cache khi cần
- `ClearMenuCacheMixin` → thêm/sửa/xóa menu (kể cả inline menu con + sửa nhanh list_editable) đều xóa cache ngay → hiện ra trang chủ sau khi F5

> **Lưu ý `JAZZMIN_SETTINGS['search_model']`:** dùng định dạng `app_label.model` (vd `products.product`), **KHÔNG** `apps.products.product` (3 phần → Jazzmin crash 500 mọi trang admin).

---

## Context Processor (`apps/core/context_processors.py`)

Toàn bộ data dưới đây gói trong **1 cache key `global_nav` (TTL 86400s = 24h)**, inject vào **mọi template**:

| Biến | Dùng cho |
|------|----------|
| `{{ site_config }}` | Logo, phone, email, social links (snapshot của `SiteConfig.get()`) |
| `{{ nav_menu }}` | Danh sách MenuItem cấp 1 (có prefetch children) |
| `{{ nav_categories }}` | Dropdown sản phẩm — ProductCategory (`show_in_menu=True`) |
| `{{ nav_service_categories }}` | Dropdown dịch vụ — ServiceCategory |
| `{{ nav_project_categories }}` | Dropdown dự án — ProjectCategory |
| `{{ nav_news_categories }}` | Dropdown tin tức — NewsCategory |
| `{{ nav_about_sections }}` | Dropdown "Về chúng tôi" — AboutSection (`show_in_menu=True`) |
| `{{ footer_services }}` | Dịch vụ hiển thị footer (6 item) |

> `SiteConfig.get()` còn cache riêng key `site_config_singleton` (24h), tự xóa trong `SiteConfig.save()`.

**Xóa cache thủ công:** `python manage.py shell -c "from django.core.cache import cache; cache.clear()"`

### Cache invalidation — admin nào tự xóa `global_nav`

Vì `global_nav` chứa snapshot menu/footer/site_config, **mọi admin chỉnh sửa data nằm trong cache PHẢI xóa cache** qua `ClearMenuCacheMixin` (save/delete/bulk delete) — nếu không, thay đổi sẽ không hiện ra website tới 24h.

| Admin | Ảnh hưởng | Xóa cache? |
|-------|-----------|:---------:|
| `SiteConfigAdmin` | site_config (mọi trang: logo/SĐT/footer) | ✅ ClearMenuCacheMixin |
| `MenuItemAdmin` | nav_menu (navbar) | ✅ ClearMenuCacheMixin |
| `ServiceAdmin` | footer_services | ✅ ClearMenuCacheMixin |
| `*CategoryAdmin` (4 app) | nav_*_categories | ✅ ClearMenuCacheMixin |
| `AboutSectionAdmin` | nav_about_sections | ✅ ClearMenuCacheMixin |

Model **query trực tiếp** (không cache → hiện ngay, không cần mixin): `Slider`, `StatItem`, `Product`, `Service` (list/detail/home), `Article`, `Project`, `Partner`, `AboutFeature`.

---

## Templates

`templates/` toàn cục — tất cả kế thừa `base.html`.

**Components dùng chung** (`templates/components/`):

| File | Mô tả |
|------|-------|
| `navbar.html` | Navbar + top bar + mega/grid dropdown |
| `footer.html` | Footer 4 cột |
| `breadcrumb.html` | Breadcrumb — truyền `breadcrumbs` list (mỗi phần tử có `name`, `url`; `url=None` = trang hiện tại). Tự thêm icon home đầu dòng. Render rỗng nếu `breadcrumbs` trống. |
| `pagination.html` | Phân trang — dùng `{% include 'components/pagination.html' %}` |

> **Breadcrumb trên detail pages:** mọi `*DetailView` (Product/Service/Project/Article/About) build `ctx['breadcrumbs']` (Home › List › Category › Item) — khớp với `BreadcrumbList` JSON-LD. Template detail include `{% include 'components/breadcrumb.html' with breadcrumbs=breadcrumbs %}` ngay sau `page-header`.

**Blocks quan trọng trong `base.html`:**

| Block | Mục đích |
|-------|----------|
| `{% block title %}` | `<title>` |
| `{% block meta_desc %}` | meta description |
| `{% block og_tags %}` | Open Graph — dùng `{{ block.super }}` để kế thừa |
| `{% block json_ld %}` | JSON-LD structured data |
| `{% block extra_meta %}` | Meta thêm trong `<head>` (vd `<meta name="robots" content="noindex">`) |
| `{% block extra_css %}` / `{% block extra_js %}` | CSS/JS per-page |

> **Versioning CSS:** link trong `base.html` dùng query `?v=N` (vd `navbar.css?v=6`) — tăng N khi sửa file CSS để bust cache trình duyệt.

**Page header:**
```html
<div class="page-header text-center">
  <div class="container"><h1>Tiêu đề</h1></div>
</div>
```
Không dùng inline style — `mobile.css` tự override responsive.

---

## Phân trang (Pagination)

Tất cả list views dùng `paginate_by = 9` và component `templates/components/pagination.html`.

**Pattern chuẩn cho list view có filter `?danh-muc=`:**
```python
def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    slug = self.request.GET.get('danh-muc')
    if slug:
        ctx['current_category'] = get_object_or_404(MyCategory, slug=slug)
        ctx['pagination_base_url'] = f'?danh-muc={slug}&'
    else:
        ctx['current_category'] = None
        ctx['pagination_base_url'] = '?'
    return ctx
```

**Pattern cho view không dùng query param (URL path):**
```python
ctx['pagination_base_url'] = '?'
```

**Trong template:**
```html
{% include 'components/pagination.html' %}
```

> `pagination_base_url` đảm bảo link trang giữ nguyên filter — ví dụ `?danh-muc=camera&page=2`.

---

## Tìm kiếm toàn site

- **URL:** `/tim-kiem/?q=<từ khóa>` · **View:** `SearchView` (TemplateView) tại `apps/core/views.py`
- Gộp kết quả 4 loại: `Product` · `Service` · `Project` · `Article` (filter `is_active`/`published`, `select_related('category')`)
- View build sẵn list dict `{type, title, desc, url, image, image_mobile}` rồi `Paginator(paginate_by=9)` — **không** dùng `default` filter trên model khác field trong template
- `pagination_base_url = f'?q={query}&'` để giữ từ khóa khi sang trang
- **Template:** `templates/search/results.html` — có `{% block extra_meta %}<meta name="robots" content="noindex,follow">{% endblock %}`
- Ô search nằm trong `templates/components/navbar.html` (form GET → `/tim-kiem/`), style ở `navbar.css`

## Form liên hệ — chống spam + email

`apps/contact/` · **View:** `ContactView` (FormView) · **Form:** `ContactForm` (ModelForm)

- **Honeypot:** field ẩn `website` — bot điền vào → `clean_website()` raise ValidationError. Template render trong div ẩn (`position:absolute;left:-9999px`).
- **Rate-limit:** `ContactView.form_valid` chặn cùng IP gửi lại trong `CONTACT_RATE_LIMIT_SECONDS` (60s) qua `cache`. Bị chặn → `form.add_error(None, ...)`, template hiện `non_field_errors` (alert).
- **Email thông báo:** sau khi lưu, `_notify_admin()` gọi `send_mail(..., fail_silently=True)` tới `settings.CONTACT_NOTIFY_EMAIL` (để trống = bỏ qua).
- Lưu `ip_address` (HTTP_X_FORWARDED_FOR → REMOTE_ADDR).

**Config EMAIL trong `.env`** (xem `.env.example`):
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend   # bỏ trống = console (dev)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=...      EMAIL_HOST_PASSWORD=...   # Gmail dùng App Password
DEFAULT_FROM_EMAIL=ADCARE Website <no-reply@adcare.vn>
CONTACT_NOTIFY_EMAIL=admin@adcare.vn                        # nơi nhận thông báo liên hệ
```

## Trang chủ (`HomeView` · `templates/core/home.html`)

Thứ tự section: **Hero slider → Stats → Giới thiệu → CTA giữa → Sản phẩm nổi bật → Dịch vụ → Dự án tiêu biểu → Tin tức → Đối tác → CTA cuối**.

Context `HomeView` (query trực tiếp, không cache): `sliders[:10]`, `stat_items`, `about` (prefetch `features`), `featured_products[:6]`, `featured_services[:6]`, `featured_projects[:6]` (`is_featured=True`), `partners[:12]`, `recent_news[:3]`. Mỗi section bọc `{% if %}` nên tự ẩn khi rỗng.

---

## Hình ảnh

### Upload & Resize
`ResizedImageField` (django-resized) tự resize khi upload. Kích thước per-field trong model.

### Mobile variants (django-imagekit)
Mỗi model có ảnh đều có `image_mobile = ImageSpecField(...)` tự tạo bản mobile nhỏ hơn.

| Model | Desktop | Mobile |
|-------|---------|--------|
| Slider | 1920×800 | 576×400 |
| Product/Service | 800×600 | 480×360 |
| Article | 1200×630 | 576×302 |
| Project | 900×600 | 480×320 |
| AboutSection | 700×500 | 480×343 |

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

- **Google Search Console:** xác minh qua meta tag trong `base.html` (`<head>`)
- **Sitemap:** `/sitemap.xml` — 5 nhóm (static + products + services + articles + projects), khai báo ở `config/urls.py`
- **robots.txt:** `/robots.txt` — chặn `/admin/`, trỏ sitemap
- **JSON-LD:** Organization schema trong `base.html`; detail pages override `{% block json_ld %}` (Product/Service/CreativeWork/NewsArticle + `BreadcrumbList`)
- **og:image:** detail pages override `{% block og_tags %}` với ảnh riêng
- **noindex:** trang tìm kiếm `/tim-kiem/` dùng `extra_meta` → `robots noindex,follow`

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
- **Migration unique field trên DB có data:** xem phần "Fix lỗi migration" ở trên — không chạy migrate thẳng
- **Phân trang:** `paginate_by = 9` cho mọi list view; luôn thêm `pagination_base_url` vào context
- **`is_active`:** hầu hết models có cờ này — query nên filter `is_active=True`
- **select_related:** dùng `select_related('category')` khi query FK — tránh N+1
- **prefetch_related:** dùng `prefetch_related('children')` cho MenuItem
- **Section spacing:** class `section-pad` (70px) / `section-pad-sm` (50px) — không inline padding
- **`get_absolute_url()`:** `Product` trả về `product_list` nếu không có category
- **Thêm app mới:** đăng ký `apps.<tên>` trong `INSTALLED_APPS`, sửa `apps.py` cho đúng `name`
- **CKEditor content:** render bằng `|safe`, không dùng `|linebreaks`
- **Jazzmin logout:** render là `<form>` không phải `<a>` — style qua `#logout-form button.dropdown-item`
- **Cache `global_nav`:** mọi admin sửa data feed vào navbar/footer/site_config PHẢI dùng `ClearMenuCacheMixin` (xem bảng "Cache invalidation"). Sai → thay đổi không hiện ra web tới 24h. Xóa tay: `cache.clear()`
- **Jazzmin search_model:** định dạng `app_label.model` (vd `products.product`) — sai (3 phần) làm crash 500 toàn admin
- **Breadcrumb detail:** DetailView build `ctx['breadcrumbs']`; detail template include `components/breadcrumb.html`
- **Email liên hệ:** cần khai báo `EMAIL_*` + `CONTACT_NOTIFY_EMAIL` trong `.env` (xem `.env.example`); `send_mail` đã `fail_silently`
- **vi_slugify:** không dùng `allow_unicode=True` — slug phải là ASCII. Dùng `vi_slugify()` từ `apps.core.models`
