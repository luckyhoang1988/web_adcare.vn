from django.contrib.admin.utils import unquote
from django.core.cache import cache
from django.db.models import FileField
from django.shortcuts import redirect, get_object_or_404
from django.urls import path, reverse
from django.utils.html import mark_safe


class ClearMenuCacheMixin:
    """Tự động xóa cache global_nav sau khi save hoặc delete — dùng cho CategoryAdmin."""

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete('global_nav')

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        cache.delete('global_nav')

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        cache.delete('global_nav')


class DuplicateMixin:
    """Thêm nút Sao chép vào danh sách: mở form Add mới pre-filled, chưa lưu."""

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        custom = [
            path('<path:object_id>/copy/', self.admin_site.admin_view(self._copy_view),
                 name='%s_%s_copy' % info),
        ]
        return custom + urls

    def _copy_view(self, request, object_id):
        obj = get_object_or_404(self.model, pk=unquote(object_id))
        add_url = reverse('admin:%s_%s_add' % (self.model._meta.app_label, self.model._meta.model_name))
        return redirect(f'{add_url}?copy_from={obj.pk}')

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        copy_from = request.GET.get('copy_from')
        if not copy_from:
            return initial
        try:
            obj = self.model.objects.get(pk=copy_from)
            for field in obj._meta.fields:
                if field.name in ('id', 'pk'):
                    continue
                if isinstance(field, FileField):
                    continue  # file/image không thể pre-fill
                initial[field.name] = getattr(obj, field.name)
            # Đổi slug để tránh trùng
            if hasattr(obj, 'slug') and obj.slug:
                initial['slug'] = f'{obj.slug}-copy'
            # Thêm "(Sao chép)" vào tên
            if hasattr(obj, 'name') and obj.name:
                initial['name'] = f'{obj.name} (Sao chép)'
            elif hasattr(obj, 'title') and obj.title:
                initial['title'] = f'{obj.title} (Sao chép)'
            # Ẩn khỏi website cho đến khi chỉnh xong
            if hasattr(obj, 'is_active'):
                initial['is_active'] = False
            if hasattr(obj, 'status'):
                initial['status'] = 'draft'
        except self.model.DoesNotExist:
            pass
        return initial

    def copy_link(self, obj):
        url = reverse('admin:%s_%s_copy' % (obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        return mark_safe(
            f'<a href="{url}" title="Sao chép" style="color:#17a2b8;font-size:15px;">'
            f'<i class="fas fa-copy"></i></a>'
        )
    copy_link.short_description = ''


def make_duplicate_action(label='bản ghi'):
    """Action nhân bản hàng loạt từ danh sách (lưu ngay, ẩn, slug+copy)."""
    def duplicate(modeladmin, request, queryset):
        for obj in queryset:
            obj.pk = None
            obj.id = None
            if hasattr(obj, 'slug') and obj.slug:
                Model = type(obj)
                base = obj.slug
                slug = f'{base}-copy'
                counter = 2
                while Model.objects.filter(slug=slug).exists():
                    slug = f'{base}-copy-{counter}'
                    counter += 1
                obj.slug = slug
            if hasattr(obj, 'is_active'):
                obj.is_active = False
            if hasattr(obj, 'status'):
                obj.status = 'draft'
            obj.save()
    duplicate.short_description = f'Sao chép {label} đã chọn'
    return duplicate
