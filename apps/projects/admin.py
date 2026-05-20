from django.contrib import admin
from django.utils.html import mark_safe
from .models import ProjectCategory, Project, ProjectImage


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 3
    fields = ('image', 'alt', 'order')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'client', 'year', 'is_featured', 'is_active', 'order', 'preview_image')
    list_editable = ('is_featured', 'is_active', 'order')
    list_display_links = ('name',)
    list_filter = ('category', 'is_featured', 'is_active', 'year')
    search_fields = ('name', 'client', 'location', 'short_desc')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProjectImageInline]

    def preview_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="50" style="border-radius:4px"/>')
        return '-'
    preview_image.short_description = 'Ảnh'
