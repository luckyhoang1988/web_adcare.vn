from django import forms
from django.contrib import admin
from django.utils.html import mark_safe
from ckeditor.widgets import CKEditorWidget
from .models import ProductCategory, Product, ProductImage


class ProductAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(), label='Mô tả chi tiết', required=False)

    class Meta:
        model = Product
        fields = '__all__'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2
    fields = ('image', 'alt', 'order')


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'category', 'brand', 'is_featured', 'is_active', 'order', 'preview_image')
    list_editable = ('is_featured', 'is_active', 'order')
    list_display_links = ('name',)
    list_filter = ('category', 'is_featured', 'is_active', 'brand')
    search_fields = ('name', 'brand', 'model_number', 'short_desc')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('category', 'name', 'slug', 'brand', 'model_number', 'image')
        }),
        ('Mô tả', {
            'fields': ('short_desc', 'description', 'specifications')
        }),
        ('Cài đặt', {
            'fields': ('is_featured', 'is_active', 'order')
        }),
    )

    def preview_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="50" style="border-radius:4px"/>')
        return '-'
    preview_image.short_description = 'Ảnh'
