# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```powershell
# Chạy development server
python manage.py runserver

# Tạo và áp dụng migrations sau khi thay đổi models
python manage.py makemigrations
python manage.py migrate

# Thu thập static files (production)
python manage.py collectstatic --noinput

# Tạo superuser
python manage.py createsuperuser

# Chạy shell Django
python manage.py shell
```

**Truy cập:**
- Trang chủ: `http://localhost:8000`
- Admin (Jazzmin): `http://localhost:8000/admin` — `admin` / `adcare@2024`

## Cấu trúc & Kiến trúc

**Stack:** Django 5.2 LTS · Jazzmin Admin · Bootstrap 5.3 · Swiper.js · SQLite · `django-resized` · `whitenoise`

**Cấu hình** đọc từ `.env` qua `python-decouple` (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`).

### Apps (`apps/`)

Tất cả apps đặt trong `apps/` và đăng ký với prefix `apps.*` (ví dụ `apps.core`).

| App | Mục đích |
|-----|----------|
| `core` | Homepage, SiteConfig (singleton pk=1), Slider, StatItem, AboutSection, **AboutFeature** |
| `products` | ProductCategory → Product → ProductImage (ForeignKey chain) |
| `services` | ServiceCategory → Service |
| `news` | NewsCategory → Article (có `status` draft/published) |
| `partners` | Partner (logo carousel) |
| `contact` | ContactMessage + ContactForm |

### SiteConfig — Singleton pattern

`SiteConfig` chỉ tồn tại **1 bản ghi duy nhất** (pk=1). Truy cập qua `SiteConfig.get()`. Dữ liệu này inject vào **mọi template** qua context processor `apps.core.context_processors.site_config`.

### Context Processor — biến global trong mọi template

`apps/core/context_processors.py` inject 2 biến vào tất cả templates:

| Biến | Nguồn | Dùng cho |
|------|-------|----------|
| `{{ site_config }}` | `SiteConfig.get()` | Logo, phone, email, social links |
| `{{ nav_categories }}` | `ProductCategory.objects.filter(is_active=True)` | Dropdown sản phẩm trên navbar |

### AboutFeature — điểm nổi bật trong section Giới thiệu

`AboutFeature` là model FK → `AboutSection` (related_name=`features`), có fields: `icon` (FontAwesome), `text`, `order`.  
Truy cập trong template: `{{ about.features.all }}`.  
Chỉnh sửa qua Admin → Section Giới thiệu → inline "Điểm nổi bật".

### Hiển thị trên Homepage

`HomeView` tổng hợp dữ liệu từ nhiều apps:
- Sản phẩm nổi bật: `Product.is_featured=True`
- Dịch vụ nổi bật: `Service.is_featured=True`
- Tin tức: `Article.status='published'`

Để một sản phẩm/dịch vụ xuất hiện trên trang chủ, phải bật cờ `is_featured` trong Admin.

### Templates

`templates/` là thư mục toàn cục (không nằm trong app). Tất cả templates kế thừa từ `templates/base.html`. Components dùng chung ở `templates/components/` (navbar, footer, breadcrumb).

**Page header** (banner xanh đầu mỗi trang): dùng class `.page-header` — đã được định nghĩa responsive trong `mobile.css`. Không dùng inline style cứng cho phần này.

```html
<div class="page-header text-center">
  <div class="container">
    <h1>Tiêu đề trang</h1>
    <p>Mô tả ngắn</p>
  </div>
</div>
```

### Static files

CSS tách theo module, load theo thứ tự trong `base.html`:

| File | Nội dung |
|------|----------|
| `main.css` | CSS variables, buttons, cards, breadcrumb, pagination, utilities |
| `navbar.css` | Navbar, top-bar, dropdown (hover desktop / click mobile) |
| `hero.css` | Hero slider Bootstrap Carousel |
| `footer.css` | Footer 4 cột |
| `mobile.css` | **Tất cả responsive overrides** — page-header, section-pad, stats, cards, mobile category chips |

CSS variables chính định nghĩa trong `main.css`:

| Variable | Giá trị | Dùng cho |
|----------|---------|----------|
| `--navy` | `#2e5c10` | Nền navbar, footer, page header |
| `--navy-dark` | `#1e3d0a` | Top bar, dropdown, footer bottom |
| `--accent` | `#7db833` | **Xanh chuối** — buttons, underline, highlight |
| `--accent-hover` | `#659a28` | Hover state của accent |
| `--light` | `#f2f8ed` | Nền section xen kẽ |

Không hardcode màu hex trong templates — luôn dùng CSS variables (`var(--navy)`, `var(--accent)`, ...).

### Navbar — active link & dropdown

- **Active link:** dùng `{% with path=request.path %}` so sánh URL để thêm class `active` vào `<li>`. CSS `.nav-item.active .nav-link::after` hiện gạch xanh.
- **Dropdown sản phẩm:** mở khi hover trên desktop (`@media (min-width: 992px)`), mở khi tap trên mobile (Bootstrap JS + `.show` class). Danh mục lấy từ biến `{{ nav_categories }}` inject bởi context processor.

### Mobile Responsive

`mobile.css` xử lý toàn bộ responsive. Breakpoints chính:

| Breakpoint | Padding section | Ghi chú |
|------------|----------------|---------|
| ≤ 991px (tablet) | 50px | page-header 36px |
| ≤ 575px (phone) | 36px `!important` | page-header 26px, stat-number 26px |
| ≤ 380px (phone nhỏ) | — | font giảm thêm |

**Products list mobile:** sidebar ẩn (`d-none d-lg-block`), thay bằng horizontal scrollable category chips (class `.mobile-cat-scroll` + `.mobile-cat-chip`). Cards dùng `col-6 col-lg-4` (2 cột trên phone).

### Image uploads

`django-resized` (`ResizedImageField`) tự động resize ảnh khi upload. Kích thước định nghĩa per-field trong từng model. File upload lưu vào `media/`.

### URL structure

```
/                    → core:home
/ve-chung-toi/       → core:about
/san-pham/           → products (list / category / detail)
/dich-vu/            → services (list / detail)
/tin-tuc/            → news (list / detail)
/lien-he/            → contact (form / success)
/admin/              → Jazzmin Admin
```

### Jazzmin Admin — tuỳ chỉnh giao diện

Tất cả custom CSS/JS cho admin nằm trong `templates/admin/base_site.html` (override Jazzmin), dùng `{% block extrastyle %}` và `{% block extrahead %}`.

**Cấu hình quan trọng trong `config/settings.py`:**
- `JAZZMIN_SETTINGS` — tiêu đề, logo, menu links, icons
- `JAZZMIN_UI_TWEAKS` — theme, màu sidebar/navbar class
- `topmenu_links` và `usermenu_links` — chỉ giữ link "Trang chủ website", **không** thêm logout vào đây (Jazzmin đã có logout mặc định)

**Lưu ý kỹ thuật Jazzmin:**
- Logout được render là `<form id="logout-form" method="post"><button class="dropdown-item">` — **không phải** `<a href>`. Muốn style phải target `#logout-form button.dropdown-item`.
- Navbar top bar dùng id `#jazzy-navbar`, user dropdown dùng id `#jazzy-usermenu`.
- Navbar có class `bg-body` hardcode → muốn đổi màu nền phải dùng CSS override `#jazzy-navbar { background-color: ... !important }`.
- Username người dùng hiển thị trên navbar button bằng JS inject trong `{% block extrahead %}` (dùng `{{ request.user }}`).

**Màu admin đồng bộ với public site:**
- Navbar admin: `#2e5c10` (navy), viền dưới `#1e3d0a`
- User button pill: `#7db833` (accent), hover `#659a28`
- Logout button: `#e74c3c` (đỏ), hover `#c0392b`

## Lưu ý quan trọng

- **Thêm app mới:** đăng ký tên dạng `apps.<tên>` trong `INSTALLED_APPS`, cập nhật `apps.py` cho đúng `name = 'apps.<tên>'`.
- **Migration:** luôn chạy `makemigrations` + `migrate` sau khi sửa model.
- **`is_active`:** hầu hết models có cờ này — query mặc định nên filter `is_active=True`.
- **`partners` app:** không có `urls.py` riêng, dữ liệu chỉ hiển thị qua homepage.
- **Breadcrumb:** truyền `breadcrumbs` list vào context, mỗi phần tử có `name` và `url`.
- **Section spacing:** dùng class `section-pad` (70px desktop) hoặc `section-pad-sm` (50px desktop) — **không** dùng inline `padding` cứng, mobile.css sẽ override tự động.
- **Page header:** luôn dùng class `.page-header`, không inline style — để mobile.css responsive hoạt động đúng.
- **Contact form card:** dùng class `.contact-form-card` thay vì inline `padding:36px`.
