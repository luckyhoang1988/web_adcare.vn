from django import forms
from django.contrib import admin
from django.utils.html import mark_safe
from ckeditor.widgets import CKEditorWidget
from .models import NewsCategory, Article
from apps.core.admin_utils import DuplicateMixin, make_duplicate_action


class ArticleAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(), label='Nội dung')

    class Meta:
        model = Article
        fields = '__all__'


@admin.register(NewsCategory)
class NewsCategoryAdmin(DuplicateMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active', 'copy_link')
    list_editable = ('order', 'is_active')
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    actions = [make_duplicate_action('danh mục')]


@admin.register(Article)
class ArticleAdmin(DuplicateMixin, admin.ModelAdmin):
    form = ArticleAdminForm
    list_display = ('title', 'category', 'author', 'status', 'is_featured', 'published_at', 'preview_image', 'copy_link')
    list_editable = ('status', 'is_featured')
    list_display_links = ('title',)
    list_filter = ('category', 'status', 'is_featured')
    list_select_related = ('category',)
    search_fields = ('title', 'summary', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    fieldsets = (
        ('Nội dung', {
            'fields': ('category', 'title', 'slug', 'summary', 'content', 'image', 'author')
        }),
        ('Xuất bản', {
            'fields': ('status', 'is_featured', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_desc'),
            'classes': ('collapse',)
        }),
    )
    actions = ['make_published', make_duplicate_action('bài viết')]

    def make_published(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='published', published_at=timezone.now())
    make_published.short_description = 'Đăng các bài đã chọn'

    def preview_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="50" style="border-radius:4px"/>')
        return '-'
    preview_image.short_description = 'Ảnh'
