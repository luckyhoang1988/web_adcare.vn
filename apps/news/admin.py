from django import forms
from django.contrib import admin
from django.utils import timezone
from django.utils.html import mark_safe
from ckeditor.widgets import CKEditorWidget
from .models import NewsCategory, Article, RssSource
from .services import fetch_source
from apps.core.admin_utils import ClearMenuCacheMixin, DuplicateMixin, make_duplicate_action


class ArticleAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(), label='Nội dung')

    class Meta:
        model = Article
        fields = '__all__'


@admin.register(NewsCategory)
class NewsCategoryAdmin(ClearMenuCacheMixin, DuplicateMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active', 'show_in_menu', 'copy_link')
    list_editable = ('order', 'is_active', 'show_in_menu')
    list_display_links = ('name',)
    search_fields = ('name',)
    actions = [make_duplicate_action('danh mục')]


@admin.register(Article)
class ArticleAdmin(DuplicateMixin, admin.ModelAdmin):
    form = ArticleAdminForm
    list_display = ('title', 'category', 'author', 'status', 'is_featured', 'published_at', 'preview_image', 'copy_link')
    list_editable = ('status', 'is_featured')
    list_display_links = ('title',)
    list_filter = ('category', 'status', 'is_featured', 'source')
    list_select_related = ('category',)
    list_per_page = 25
    search_fields = ('title', 'summary', 'content')
    date_hierarchy = 'published_at'
    readonly_fields = ('source_guid',)
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
        ('Nguồn nhập', {
            'fields': ('source', 'source_url', 'source_guid'),
            'classes': ('collapse',)
        }),
    )
    actions = ['make_published', make_duplicate_action('bài viết')]

    def make_published(self, request, queryset):
        queryset.update(status='published', published_at=timezone.now())
    make_published.short_description = 'Đăng các bài đã chọn'

    def preview_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="50" style="border-radius:4px"/>')
        return '-'
    preview_image.short_description = 'Ảnh'


@admin.register(RssSource)
class RssSourceAdmin(DuplicateMixin, admin.ModelAdmin):
    list_display = ('name', 'category', 'use_ai', 'is_active', 'order', 'max_items',
                    'last_fetched_at', 'article_count', 'copy_link')
    list_editable = ('is_active', 'order')
    list_display_links = ('name',)
    list_filter = ('is_active', 'use_ai', 'category')
    search_fields = ('name', 'feed_url')
    readonly_fields = ('last_fetched_at',)
    list_per_page = 25
    actions = ['fetch_now', make_duplicate_action('nguồn RSS')]

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Số bài'

    def fetch_now(self, request, queryset):
        total = {'created': 0, 'skipped': 0, 'errors': 0}
        for source in queryset:
            stats = fetch_source(source)
            for k in total:
                total[k] += stats[k]
        msg = (f"Đã lấy bài: tạo {total['created']} · "
               f"trùng {total['skipped']} · lỗi {total['errors']}.")
        if total['errors']:
            self.message_user(request, msg, level='warning')
        else:
            self.message_user(request, msg)
    fetch_now.short_description = '🔄 Lấy bài ngay từ nguồn đã chọn'
