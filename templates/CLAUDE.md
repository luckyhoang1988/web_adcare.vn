# Rules cho `templates/` — Django Templates

## Cấu trúc bắt buộc

Mọi template phải:
1. `{% extends 'base.html' %}`
2. Định nghĩa `{% block title %}` và `{% block meta_desc %}`
3. Không duplicate navbar/footer (đã có trong base.html qua blocks)

## Blocks quan trọng

| Block | Bắt buộc? | Ghi chú |
|-------|-----------|---------|
| `title` | Bắt buộc | Không thêm " - ADCARE" (base.html đã làm) |
| `meta_desc` | Bắt buộc | 150-160 ký tự |
| `og_tags` | Detail pages | Dùng `{{ block.super }}` để giữ defaults |
| `json_ld` | Detail pages | Schema.org markup |
| `content` | Bắt buộc | Nội dung chính của trang |
| `extra_css` | Khi cần | CSS riêng cho trang |
| `extra_js` | Khi cần | JS riêng cho trang |

## Images — LUÔN dùng `<picture>` element

```html
<!-- ĐÚNG -->
<picture>
  <source media="(max-width: 575px)" srcset="{{ obj.image_mobile.url }}">
  <img src="{{ obj.image.url }}" alt="{{ obj.name }}" loading="lazy">
</picture>

<!-- SAI — không có mobile variant -->
<img src="{{ obj.image.url }}" alt="{{ obj.name }}">
```

## CKEditor — LUÔN dùng `|safe`

```html
{{ article.content|safe }}    <!-- ĐÚNG -->
{{ article.content|linebreaks }} <!-- SAI -->
{{ article.content }}            <!-- SAI — hiện HTML tags -->
```

## CSS

### Không hardcode màu, kích thước
```html
<!-- SAI -->
<section style="padding: 70px 0; background: #f2f8ed;">
<h2 style="color: #2e5c10;">

<!-- ĐÚNG -->
<section class="section-pad bg-light">
<h2 style="color: var(--navy);">  <!-- nếu bắt buộc dùng inline -->
```

### Classes chuẩn
- `section-pad` — 70px vertical padding
- `section-pad-sm` — 50px
- `page-header` — header section tối màu
- `bg-light` — nền xanh nhạt (var --light)
- `btn-accent` / `btn-navy` — buttons

## Components

### Page header + breadcrumb
```html
<div class="page-header text-center">
  <div class="container">
    <h1>Tên trang</h1>
    {% include 'components/breadcrumb.html' with breadcrumbs=breadcrumbs %}
  </div>
</div>
```
View phải truyền `breadcrumbs` list: `[{'name': '...', 'url': '...'}, ...]` (url rỗng = trang hiện tại)

### Pagination
```html
{% include 'components/pagination.html' %}
```
View **bắt buộc** có `pagination_base_url` trong context.

## Context variables luôn có sẵn

- `{{ site_config }}` — logo, phone, email, social links
- `{{ nav_menu }}` — MenuItem cấp 1
- `{{ nav_categories }}` — ProductCategory
- `{{ nav_service_categories }}` — ServiceCategory
- `{{ footer_services }}` — 6 services cho footer

## Không làm

- Không load Bootstrap, jQuery, FontAwesome lại (đã có trong base.html)
- Không `{% load static %}` nếu không dùng `{% static %}`
- Không `<br>` hay `<p>` tag bao quanh `|safe` content
- Không inline style thay cho CSS class (ngoại lệ: CSS variables inline)
- Không duplicate nội dung từ `navbar.html` hay `footer.html`
