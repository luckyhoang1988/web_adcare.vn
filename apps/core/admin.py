from django import forms
from django.contrib import admin
from django.utils.html import mark_safe
from ckeditor.widgets import CKEditorWidget
from .models import SiteConfig, Slider, StatItem, AboutSection, AboutFeature, MenuItem
from .admin_utils import DuplicateMixin, make_duplicate_action


class AboutSectionForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(), label='Nội dung')

    class Meta:
        model = AboutSection
        fields = '__all__'


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Thông tin công ty', {
            'fields': ('company_name', 'company_name_en', 'slogan', 'logo', 'favicon')
        }),
        ('Liên hệ', {
            'fields': ('address', 'phone', 'phone_2', 'email', 'email_2')
        }),
        ('Mạng xã hội', {
            'fields': ('facebook_url', 'youtube_url', 'zalo_url', 'linkedin_url')
        }),
        ('Footer', {
            'fields': ('footer_description', 'working_hours'),
            'description': 'Nội dung hiển thị ở chân trang website'
        }),
        ('Bản đồ & SEO', {
            'fields': ('google_maps_embed', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'preview_image')
    list_editable = ('order', 'is_active')
    list_display_links = ('title',)

    def preview_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="50" style="border-radius:4px"/>')
        return '-'
    preview_image.short_description = 'Xem trước'


@admin.register(StatItem)
class StatItemAdmin(admin.ModelAdmin):
    list_display = ('label', 'number', 'icon', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_display_links = ('label',)


class AboutFeatureInline(admin.TabularInline):
    model = AboutFeature
    extra = 3
    fields = ('icon', 'text', 'order')


@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    form = AboutSectionForm
    list_display = ('title', 'page_url_display', 'show_in_menu', 'menu_status', 'is_active', 'preview_link', 'updated_at')
    list_editable = ('show_in_menu', 'is_active')
    list_display_links = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [AboutFeatureInline]
    fieldsets = (
        ('Nội dung', {
            'fields': ('title', 'slug', 'subtitle', 'content', 'image', 'image_alt', 'button_text', 'button_url')
        }),
        ('Vị trí hiển thị trên Menu', {
            'fields': ('show_in_menu', 'auto_add_menu', 'menu_parent', 'menu_order'),
            'description': (
                'Bật "Tự động thêm vào menu" → khi lưu sẽ tạo mục menu trỏ đến trang này. '
                'Chọn "Menu cha" nếu muốn hiển thị là menu con (dropdown). '
                'Để trống = thêm vào menu cấp 1.'
            )
        }),
        ('Cài đặt', {
            'fields': ('is_active',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_desc'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not obj.slug or not obj.auto_add_menu:
            return
        from django.core.cache import cache
        url = obj.get_absolute_url()
        item, created = MenuItem.objects.get_or_create(
            url=url,
            defaults={
                'title': obj.title,
                'item_type': 'custom',
                'parent': obj.menu_parent,
                'order': obj.menu_order,
                'is_active': obj.is_active,
            }
        )
        if not created:
            item.title = obj.title
            item.parent = obj.menu_parent
            item.order = obj.menu_order
            item.is_active = obj.is_active
            item.save()
        cache.clear()

    def page_url_display(self, obj):
        if not obj.slug:
            return mark_safe('<span style="color:#aaa;font-style:italic;">Chưa có slug</span>')
        try:
            url = obj.get_absolute_url()
            return mark_safe(
                f'<a href="{url}" target="_blank" style="font-size:11px;color:#17a2b8;">'
                f'/gioi-thieu/{obj.slug}/</a>'
            )
        except Exception:
            return mark_safe(f'<code style="font-size:11px;color:#dc3545;">{obj.slug} (lỗi URL)</code>')
    page_url_display.short_description = 'URL trang'

    def menu_status(self, obj):
        if obj.auto_add_menu:
            parent = obj.menu_parent.title if obj.menu_parent else 'Menu chính'
            return mark_safe(
                f'<span style="color:#28a745;font-size:12px;">'
                f'<i class="fas fa-check-circle"></i> {parent}</span>'
            )
        return mark_safe('<span style="color:#aaa;font-size:12px;">—</span>')
    menu_status.short_description = 'Vị trí menu'

    def preview_link(self, obj):
        if not obj.slug:
            return mark_safe('<span style="color:#ccc;" title="Cần điền slug trước"><i class="fas fa-eye-slash"></i></span>')
        try:
            url = obj.get_absolute_url()
            return mark_safe(
                f'<a href="{url}" target="_blank" title="Xem trang trước" '
                f'style="color:#28a745;font-size:16px;"><i class="fas fa-eye"></i></a>'
            )
        except Exception:
            return '-'
    preview_link.short_description = 'Preview'


class MenuSubItemInline(admin.TabularInline):
    model = MenuItem
    fk_name = 'parent'
    extra = 2
    fields = ('title', 'url', 'icon', 'description', 'order', 'is_active', 'open_in_new_tab')
    verbose_name = 'Menu con'
    verbose_name_plural = 'Danh sách menu con (dropdown)'


@admin.register(MenuItem)
class MenuItemAdmin(DuplicateMixin, admin.ModelAdmin):
    list_display = ('display_title', 'item_type', 'dropdown_style', 'url', 'order', 'is_active', 'copy_link')
    list_editable = ('order', 'is_active')
    list_display_links = ('display_title',)
    ordering = ('order',)
    inlines = [MenuSubItemInline]
    actions = [make_duplicate_action('menu')]
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('title', 'item_type', 'url', 'order', 'is_active', 'open_in_new_tab')
        }),
        ('Kiểu dropdown (khi có menu con)', {
            'fields': ('dropdown_style', 'icon', 'description'),
            'description': 'Cấu hình giao diện dropdown. Thêm menu con bên dưới.'
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parent=None)

    def display_title(self, obj):
        return obj.title
    display_title.short_description = 'Tên menu'
