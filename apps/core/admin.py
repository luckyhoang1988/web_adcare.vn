from django import forms
from django.contrib import admin
from django.core.cache import cache
from django.db.models import Count, Prefetch
from django.urls import reverse, NoReverseMatch
from django.utils.html import format_html, mark_safe
from ckeditor.widgets import CKEditorWidget
from .models import SiteConfig, Slider, StatItem, AboutSection, AboutFeature, MenuItem
from .admin_utils import DuplicateMixin, ClearMenuCacheMixin, make_duplicate_action

# Loại menu tự sinh dropdown danh mục/mục con — không cần thêm menu con thủ công.
AUTO_DROPDOWN_TYPES = {'products', 'services', 'about', 'projects', 'news'}

# Ánh xạ loại menu → tên URL để dựng link "Xem trên web".
ITEM_TYPE_URL_NAMES = {
    'home': 'home',
    'about': 'about',
    'products': 'product_list',
    'services': 'service_list',
    'projects': 'project_list',
    'news': 'news_list',
    'contact': 'contact',
}


class AboutSectionForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(), label='Nội dung')

    class Meta:
        model = AboutSection
        fields = '__all__'


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Thông tin công ty', {
            'fields': ('company_name', 'company_name_en', 'slogan', 'logo', 'favicon', 'pdf_profile')
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
    search_fields = ('title',)

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
    search_fields = ('label',)


class AboutFeatureInline(admin.TabularInline):
    model = AboutFeature
    extra = 3
    fields = ('icon', 'text', 'order')


@admin.register(AboutSection)
class AboutSectionAdmin(ClearMenuCacheMixin, admin.ModelAdmin):
    form = AboutSectionForm
    list_display = ('title', 'page_url_display', 'show_in_menu', 'menu_status', 'is_active', 'preview_link', 'updated_at')
    list_editable = ('show_in_menu', 'is_active')
    list_display_links = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [AboutFeatureInline]
    fieldsets = (
        ('Nội dung', {
            'fields': ('title', 'slug', 'subtitle', 'content', 'image', 'image_alt', 'pdf_file', 'button_text', 'button_url')
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
        if not obj.slug:
            return
        from django.core.cache import cache
        url = obj.get_absolute_url()
        if obj.auto_add_menu:
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
        else:
            # Tắt auto_add_menu → deactivate MenuItem đã tạo tự động
            MenuItem.objects.filter(url=url, item_type='custom').update(is_active=False)
        cache.delete('global_nav')

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
    extra = 1
    fields = ('title', 'url', 'icon', 'description', 'order', 'is_active', 'open_in_new_tab')
    verbose_name = 'Menu con'
    verbose_name_plural = 'Menu con (dropdown) — mỗi dòng là 1 mục trong dropdown'


def clear_menu_cache_action(modeladmin, request, queryset):
    cache.delete('global_nav')
    modeladmin.message_user(request, 'Đã làm mới menu — thay đổi đã hiển thị ngoài website.')
clear_menu_cache_action.short_description = '🔄 Làm mới menu ra website (xóa cache)'


@admin.register(MenuItem)
class MenuItemAdmin(ClearMenuCacheMixin, DuplicateMixin, admin.ModelAdmin):
    list_display = ('title_tree', 'type_badge', 'submenu_info', 'link_target',
                    'order', 'is_active', 'onsite_link', 'copy_link')
    list_editable = ('order', 'is_active')
    list_display_links = ('title_tree',)
    list_per_page = 25
    list_filter = ('is_active', 'item_type')
    search_fields = ('title', 'url')
    ordering = ('order',)
    inlines = [MenuSubItemInline]
    actions = [clear_menu_cache_action, make_duplicate_action('menu')]
    fieldsets = (
        ('1. Thông tin cơ bản', {
            'fields': ('title', 'item_type', 'url', 'icon'),
            'description': (
                'Chọn <b>Loại trang</b> để menu trỏ tới trang có sẵn (Trang chủ, Sản phẩm, Dịch vụ…). '
                'Các loại <b>Sản phẩm, Dịch vụ, Về chúng tôi, Dự án, Tin tức</b> sẽ <b>tự sinh dropdown danh mục</b> '
                '— không cần thêm menu con. Chọn <b>Link tùy chỉnh</b> rồi điền <b>URL</b> để trỏ tới địa chỉ bất kỳ.'
            )
        }),
        ('2. Hiển thị & thứ tự', {
            'fields': ('order', 'is_active', 'open_in_new_tab'),
            'description': 'Số <b>Thứ tự</b> nhỏ hiển thị trước. Bỏ tích <b>Hiển thị</b> để ẩn tạm khỏi navbar.'
        }),
        ('3. Dropdown tùy chỉnh (khi tự thêm menu con bên dưới)', {
            'fields': ('dropdown_style', 'description'),
            'classes': ('collapse',),
            'description': (
                'Chỉ dùng khi bạn tự thêm <b>Menu con</b> ở khung bên dưới (cho "Link tùy chỉnh"). '
                '<b>Danh sách</b>: cột dọc đơn giản · <b>Lưới</b>: 2 cột có icon · <b>Mega</b>: 2 cột có icon + mô tả.'
            )
        }),
    )

    def get_queryset(self, request):
        # Chỉ hiện menu cấp 1; kèm số lượng + danh sách menu con để tránh N+1.
        children_qs = MenuItem.objects.order_by('order')
        return (super().get_queryset(request)
                .filter(parent=None)
                .annotate(_submenu_count=Count('children'))
                .prefetch_related(Prefetch('children', queryset=children_qs)))

    @admin.display(description='Tên menu', ordering='title')
    def title_tree(self, obj):
        icon = format_html('<i class="{}" style="color:#7db833;margin-right:6px;"></i>', obj.icon) if obj.icon else ''
        return format_html('{}<b>{}</b>', icon, obj.title)

    @admin.display(description='Loại')
    def type_badge(self, obj):
        label = obj.get_item_type_display()
        if obj.item_type in AUTO_DROPDOWN_TYPES:
            color, note = '#17a2b8', ' ▾ tự sinh dropdown'
        elif obj.item_type == 'custom':
            color, note = '#6c757d', ''
        else:
            color, note = '#28a745', ''
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;">{}{}</span>',
            color, label, note,
        )

    @admin.display(description='Menu con')
    def submenu_info(self, obj):
        count = getattr(obj, '_submenu_count', 0)
        if not count:
            if obj.item_type in AUTO_DROPDOWN_TYPES:
                return mark_safe('<span style="color:#17a2b8;font-size:12px;">(tự động)</span>')
            return mark_safe('<span style="color:#ccc;">—</span>')
        names = ', '.join(c.title for c in obj.children.all()[:4])
        if count > 4:
            names += '…'
        return format_html(
            '<span style="font-size:12px;"><b>{}</b> mục: <span style="color:#666;">{}</span></span>',
            count, names,
        )

    @admin.display(description='Trỏ tới')
    def link_target(self, obj):
        url = self._resolve_url(obj)
        if url:
            return format_html('<code style="font-size:11px;color:#0a7;">{}</code>', url)
        return mark_safe('<span style="color:#dc3545;font-size:11px;">chưa có URL</span>')

    @admin.display(description='Web')
    def onsite_link(self, obj):
        url = self._resolve_url(obj)
        if not url:
            return mark_safe('<span style="color:#ccc;"><i class="fas fa-eye-slash"></i></span>')
        return format_html(
            '<a href="{}" target="_blank" title="Xem trên website" '
            'style="color:#28a745;font-size:15px;"><i class="fas fa-external-link-alt"></i></a>', url,
        )

    @staticmethod
    def _resolve_url(obj):
        if obj.item_type == 'custom':
            return obj.url or ''
        name = ITEM_TYPE_URL_NAMES.get(obj.item_type)
        if not name:
            return obj.url or ''
        try:
            return reverse(name)
        except NoReverseMatch:
            return obj.url or ''
