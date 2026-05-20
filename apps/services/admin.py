from django.contrib import admin
from django.utils.html import mark_safe
from .models import ServiceCategory, Service


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_featured', 'is_active', 'order', 'preview_image')
    list_editable = ('is_featured', 'is_active', 'order')
    list_display_links = ('name',)
    list_filter = ('category', 'is_featured', 'is_active')
    search_fields = ('name', 'short_desc')
    prepopulated_fields = {'slug': ('name',)}

    def preview_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="50" style="border-radius:4px"/>')
        return '-'
    preview_image.short_description = 'Ảnh'
