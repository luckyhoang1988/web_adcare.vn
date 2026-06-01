# Scaffold ứng dụng Django mới

Tạo đầy đủ cấu trúc Django app mới theo conventions của Web_adcare.

**Cách dùng:** `/new-app <tên_app> [url_prefix]`
Ví dụ: `/new-app faq cau-hoi` hoặc `/new-app testimonials`

## Bước 1: Đọc tên app từ arguments

`$ARGUMENTS` chứa `<tên_app>` (bắt buộc) và `[url_prefix]` (tùy chọn, mặc định = tên_app).

## Bước 2: Tạo cấu trúc thư mục

Tạo các file sau (thay `<app_name>` bằng tên thực):

```
apps/<app_name>/
├── __init__.py
├── apps.py
├── models.py
├── views.py
├── urls.py
├── admin.py
└── migrations/
    └── __init__.py
```

Cũng tạo thư mục template:
```
templates/<app_name>/
├── list.html
└── detail.html
```

## Bước 3: Nội dung các file

### `apps/<app_name>/apps.py`
```python
from django.apps import AppConfig

class <AppName>Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.<app_name>'
    verbose_name = '<Tên hiển thị>'
```

### `apps/<app_name>/models.py`
Tạo pattern Category → Item chuẩn:
```python
from django.db import models
from django.urls import reverse
from django_resized import ResizedImageField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from apps.core.models import vi_slugify


class <AppName>Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='Tên danh mục')
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name='Mô tả')
    icon = models.CharField(max_length=100, blank=True, verbose_name='Icon (FontAwesome)')
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Thứ tự')
    is_active = models.BooleanField(default=True, verbose_name='Hiển thị')
    show_in_menu = models.BooleanField(default=True, verbose_name='Hiện trong menu')

    class Meta:
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = vi_slugify(self.name)
            slug = base; i = 2
            while <AppName>Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{i}'; i += 1
            self.slug = slug
        super().save(*args, **kwargs)


class <AppName>Item(models.Model):
    category = models.ForeignKey(
        <AppName>Category, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='items',
        verbose_name='Danh mục'
    )
    name = models.CharField(max_length=300, verbose_name='Tên')
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    short_desc = models.TextField(blank=True, verbose_name='Mô tả ngắn')
    description = models.TextField(blank=True, verbose_name='Nội dung chi tiết')
    image = ResizedImageField(
        size=[800, 600], quality=85,
        upload_to='<app_name>/',
        force_format='WEBP',
        blank=True, null=True,
        verbose_name='Ảnh'
    )
    image_mobile = ImageSpecField(
        source='image',
        processors=[ResizeToFill(480, 360)],
        format='WEBP',
        options={'quality': 80}
    )
    is_featured = models.BooleanField(default=False, verbose_name='Nổi bật')
    is_active = models.BooleanField(default=True, verbose_name='Hiển thị')
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Thứ tự')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = vi_slugify(self.name)
            slug = base; i = 2
            while <AppName>Item.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{i}'; i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('<app_name>:detail', kwargs={'slug': self.slug})
```

### `apps/<app_name>/admin.py`
```python
from django.contrib import admin
from .models import <AppName>Category, <AppName>Item
from apps.core.admin_utils import DuplicateMixin, make_duplicate_action


@admin.register(<AppName>Category)
class <AppName>CategoryAdmin(DuplicateMixin, admin.ModelAdmin):
    list_display = ('name', 'is_active', 'order', 'copy_link')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    actions = [make_duplicate_action('danh mục')]


@admin.register(<AppName>Item)
class <AppName>ItemAdmin(DuplicateMixin, admin.ModelAdmin):
    list_display = ('name', 'category', 'is_featured', 'is_active', 'order', 'copy_link')
    list_editable = ('is_featured', 'is_active', 'order')
    list_filter = ('is_active', 'is_featured', 'category')
    search_fields = ('name', 'short_desc')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    actions = [make_duplicate_action('item')]
```

### `apps/<app_name>/views.py`
```python
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import <AppName>Category, <AppName>Item


class <AppName>ListView(ListView):
    model = <AppName>Item
    template_name = '<app_name>/list.html'
    context_object_name = 'items'
    paginate_by = 9

    def get_queryset(self):
        qs = (<AppName>Item.objects
              .filter(is_active=True)
              .select_related('category')
              .order_by('order', '-created_at'))
        slug = self.request.GET.get('danh-muc')
        if slug:
            qs = qs.filter(category__slug=slug)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        slug = self.request.GET.get('danh-muc')
        if slug:
            ctx['current_category'] = get_object_or_404(<AppName>Category, slug=slug)
            ctx['pagination_base_url'] = f'?danh-muc={slug}&'
        else:
            ctx['current_category'] = None
            ctx['pagination_base_url'] = '?'
        ctx['categories'] = <AppName>Category.objects.filter(is_active=True).order_by('order')
        return ctx


class <AppName>DetailView(DetailView):
    model = <AppName>Item
    template_name = '<app_name>/detail.html'
    context_object_name = 'item'

    def get_queryset(self):
        return <AppName>Item.objects.filter(is_active=True).select_related('category')
```

### `apps/<app_name>/urls.py`
```python
from django.urls import path
from . import views

app_name = '<app_name>'
urlpatterns = [
    path('', views.<AppName>ListView.as_view(), name='list'),
    path('<slug:slug>/', views.<AppName>DetailView.as_view(), name='detail'),
]
```

## Bước 4: Hướng dẫn thủ công (không thể tự động hóa)

Sau khi tạo xong files, nhắc người dùng làm thủ công:

1. **`config/settings.py`** — thêm vào `INSTALLED_APPS`:
   ```python
   'apps.<app_name>',
   ```

2. **`config/urls.py`** — thêm URL pattern:
   ```python
   path('<url_prefix>/', include('apps.<app_name>.urls')),
   ```

3. **`apps/core/context_processors.py`** — nếu cần inject vào mọi template (dropdown menu, footer, etc.)

4. **Chạy migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Tạo templates** `templates/<app_name>/list.html` và `detail.html` — dùng `/template-agent` hoặc copy từ app tương tự.

## Lưu ý

- Thay tất cả `<app_name>` bằng tên app thực (snake_case)
- Thay tất cả `<AppName>` bằng PascalCase
- Tên model phải phản ánh đúng domain (FAQ, Testimonial, Gallery, ...)
- Không tạo app nếu chức năng đã có trong app khác
