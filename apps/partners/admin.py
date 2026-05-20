from django.contrib import admin
from django.utils.html import mark_safe
from .models import Partner


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'partner_type', 'website', 'order', 'is_active', 'preview_logo')
    list_editable = ('order', 'is_active')
    list_display_links = ('name',)
    list_filter = ('partner_type', 'is_active')
    search_fields = ('name',)

    def preview_logo(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" height="40" style="object-fit:contain"/>')
        return '-'
    preview_logo.short_description = 'Logo'
