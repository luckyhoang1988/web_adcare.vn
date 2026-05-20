from django.contrib import admin
from django.utils.html import mark_safe
from .models import SiteConfig, Slider, StatItem, AboutSection, AboutFeature


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
    list_display = ('title', 'is_active', 'updated_at')
    list_editable = ('is_active',)
    inlines = [AboutFeatureInline]
