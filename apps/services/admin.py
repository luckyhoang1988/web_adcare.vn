from django import forms
from django.contrib import admin
from django.utils.html import mark_safe
from ckeditor.widgets import CKEditorWidget
from .models import ServiceCategory, Service


class ServiceAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(), label='Mô tả chi tiết', required=False)

    class Meta:
        model = Service
        fields = '__all__'


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm
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
