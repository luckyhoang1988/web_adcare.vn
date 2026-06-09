from django import forms
from django.contrib import admin
from django.utils.html import mark_safe
from ckeditor.widgets import CKEditorWidget
from .models import ServiceCategory, Service
from apps.core.models import collect_descendant_ids
from apps.core.admin_utils import ClearMenuCacheMixin, DuplicateMixin, make_duplicate_action


class ServiceAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(), label='Mô tả chi tiết', required=False)

    class Meta:
        model = Service
        fields = '__all__'


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(ClearMenuCacheMixin, DuplicateMixin, admin.ModelAdmin):
    list_display = ('tree_name', 'parent', 'slug', 'order', 'is_active', 'show_in_menu', 'copy_link')
    list_editable = ('order', 'is_active', 'show_in_menu')
    list_display_links = ('tree_name',)
    list_filter = ('parent', 'is_active', 'show_in_menu')
    search_fields = ('name',)
    actions = [make_duplicate_action('danh mục')]

    def tree_name(self, obj):
        depth = len(obj.get_ancestors())
        prefix = '— ' * depth
        return mark_safe(f'{prefix}{obj.name}')
    tree_name.short_description = 'Tên danh mục'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            obj_id = request.resolver_match.kwargs.get('object_id')
            if obj_id:
                obj = ServiceCategory.objects.filter(pk=obj_id).first()
                if obj:
                    all_cats = list(ServiceCategory.objects.all())
                    exclude_ids = collect_descendant_ids(obj, all_cats)
                    kwargs['queryset'] = ServiceCategory.objects.exclude(pk__in=exclude_ids)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Service)
class ServiceAdmin(ClearMenuCacheMixin, DuplicateMixin, admin.ModelAdmin):
    form = ServiceAdminForm
    list_display = ('name', 'category', 'is_featured', 'is_active', 'order', 'preview_image', 'copy_link')
    list_editable = ('is_featured', 'is_active', 'order')
    list_display_links = ('name',)
    list_filter = ('category', 'is_featured', 'is_active')
    list_select_related = ('category',)
    list_per_page = 25
    search_fields = ('name', 'short_desc', 'icon')
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('category', 'name', 'slug', 'icon', 'image')
        }),
        ('Mô tả', {
            'fields': ('short_desc', 'description')
        }),
        ('Cài đặt', {
            'fields': ('is_featured', 'is_active', 'order')
        }),
    )
    actions = [make_duplicate_action('dịch vụ')]

    def preview_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="50" style="border-radius:4px"/>')
        return '-'
    preview_image.short_description = 'Ảnh'
