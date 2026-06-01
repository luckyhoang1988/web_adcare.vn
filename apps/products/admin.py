from django import forms
from django.contrib import admin
from django.utils.html import mark_safe
from ckeditor.widgets import CKEditorWidget
from .models import ProductCategory, Product, ProductImage
from apps.core.admin_utils import ClearMenuCacheMixin, DuplicateMixin, make_duplicate_action


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
class ProductCategoryAdmin(ClearMenuCacheMixin, DuplicateMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active', 'show_in_menu', 'copy_link')
    list_editable = ('order', 'is_active', 'show_in_menu')
    list_display_links = ('name',)
    search_fields = ('name',)
    actions = [make_duplicate_action('danh mục')]


@admin.register(Product)
class ProductAdmin(DuplicateMixin, admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'category', 'brand', 'is_featured', 'is_active', 'order', 'preview_image', 'copy_link')
    list_editable = ('is_featured', 'is_active', 'order')
    list_display_links = ('name',)
    list_filter = ('category', 'is_featured', 'is_active', 'brand')
    list_select_related = ('category',)
    search_fields = ('name', 'brand', 'model_number', 'short_desc')
    inlines = [ProductImageInline]
    actions = [make_duplicate_action('sản phẩm')]
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
