from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'subject', 'status', 'created_at')
    list_editable = ('status',)
    list_display_links = ('full_name',)
    list_filter = ('status',)
    date_hierarchy = 'created_at'
    search_fields = ('full_name', 'email', 'phone', 'subject', 'message', 'company')
    readonly_fields = ('full_name', 'email', 'phone', 'company', 'subject',
                       'message', 'ip_address', 'created_at')
    fieldsets = (
        ('Thông tin người gửi', {
            'fields': ('full_name', 'email', 'phone', 'company')
        }),
        ('Nội dung', {
            'fields': ('subject', 'message')
        }),
        ('Xử lý', {
            'fields': ('status', 'replied_at', 'admin_notes')
        }),
        ('Hệ thống', {
            'fields': ('ip_address', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return False
