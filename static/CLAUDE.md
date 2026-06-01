# Rules cho `static/` — CSS, JavaScript

## CSS

### File ownership — không nhầm file
| File | Nội dung |
|------|----------|
| `main.css` | CSS variables, buttons, cards, utilities, dropdown styles |
| `navbar.css` | Navbar, top bar, dropdown menu |
| `hero.css` | Hero slider |
| `footer.css` | Footer |
| `mobile.css` | **TẤT CẢ** responsive overrides (max-width breakpoints) |

**Quy tắc:** responsive code chỉ được viết trong `mobile.css`. Không viết `@media` query trong các file khác.

### CSS Variables (định nghĩa trong `main.css`)

```css
/* Màu chính */
--navy: #2e5c10;       /* Navbar, footer, page header */
--navy-dark: #1e3d0a;  /* Top bar, footer bottom */
--accent: #7db833;     /* Buttons, highlight, hover states */
--light: #f2f8ed;      /* Section backgrounds xen kẽ */

/* Typography */
--font-main: 'Be Vietnam Pro', sans-serif;
```

**Không hardcode** các màu này. Dùng `var(--navy)` thay `#2e5c10`.

### Breakpoints (trong `mobile.css`)
```css
/* Mobile */
@media (max-width: 575px) { ... }
/* Tablet */
@media (max-width: 767px) { ... }
/* Small desktop */
@media (max-width: 991px) { ... }
/* Desktop */
@media (max-width: 1199px) { ... }
```

### Classes chuẩn — không tạo duplicate
Trước khi thêm class mới, kiểm tra đã có trong `main.css`:
- `.section-pad` / `.section-pad-sm` — spacing sections
- `.page-header` — header section
- `.btn-accent` / `.btn-navy` — buttons
- `.product-card` / `.service-card` / `.news-card` / `.project-card` — content cards

## JavaScript

### Không dùng jQuery
Project đã load jQuery (qua Bootstrap). Khi cần DOM manipulation:
```javascript
// Dùng jQuery (đã có sẵn)
$('.selector').on('click', function() { ... });

// Hoặc vanilla JS
document.querySelector('.selector').addEventListener('click', () => { ... });
```

### File placement
- Code dùng chung → `main.js`
- Counter animation → `counter.js` (không sửa nếu không cần)
- Code cho admin → `admin/custom_admin.js`
- Code riêng cho 1 trang → `{% block extra_js %}` trong template, không tạo file mới

## Không làm

- Không `!important` trừ khi override Bootstrap và không có cách khác
- Không duplicate selector giữa các file CSS
- Không viết `@media` query ngoài `mobile.css`
- Không hardcode hex colors — dùng CSS variables
- Không thêm thư viện JS mới mà không hỏi (ảnh hưởng performance)
- Không minify thủ công — production dùng whitenoise tự động
