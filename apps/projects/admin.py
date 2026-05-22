from django.contrib import admin
from django.utils.html import mark_safe
from .models import ProjectCategory, Project, ProjectImage
from apps.core.admin_utils import ClearMenuCacheMixin, DuplicateMixin, make_duplicate_action


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(ClearMenuCacheMixin, DuplicateMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active', 'show_in_menu', 'copy_link')
    list_editable = ('order', 'is_active', 'show_in_menu')
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    actions = [make_duplicate_action('danh mục')]


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 3
    fields = ('image', 'alt', 'order')


@admin.register(Project)
class ProjectAdmin(DuplicateMixin, admin.ModelAdmin):
    list_display = ('name', 'category', 'client', 'year', 'is_featured', 'is_active', 'order', 'preview_image', 'copy_link')
    list_editable = ('is_featured', 'is_active', 'order')
    list_display_links = ('name',)
    list_filter = ('category', 'is_featured', 'is_active', 'year')
    list_select_related = ('category',)
    search_fields = ('name', 'client', 'location', 'short_desc')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProjectImageInline]
    actions = [make_duplicate_action('dự án')]

    def preview_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="50" style="border-radius:4px"/>')
        return '-'
    preview_image.short_description = 'Ảnh'
