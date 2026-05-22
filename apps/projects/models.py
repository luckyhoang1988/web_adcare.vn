from django.db import models
from django.urls import reverse
from django_resized import ResizedImageField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit


class ProjectCategory(models.Model):
    name = models.CharField('Tên danh mục', max_length=200)
    slug = models.SlugField('Slug', unique=True, allow_unicode=True)
    icon = models.CharField('Icon (FontAwesome)', max_length=100, blank=True)
    order = models.PositiveSmallIntegerField('Thứ tự', default=0)
    is_active = models.BooleanField('Hiển thị', default=True)
    show_in_menu = models.BooleanField('Hiển thị trong menu', default=True,
                                       help_text='Bật để danh mục này xuất hiện trong dropdown menu điều hướng.')

    class Meta:
        ordering = ['order']
        verbose_name = 'Danh mục dự án'
        verbose_name_plural = 'Danh mục dự án'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project_list') + f'?danh-muc={self.slug}'


class Project(models.Model):
    category = models.ForeignKey(
        ProjectCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='projects', verbose_name='Danh mục'
    )
    name = models.CharField('Tên dự án', max_length=300)
    slug = models.SlugField('Slug', unique=True, allow_unicode=True)
    short_desc = models.TextField('Mô tả ngắn', max_length=500, blank=True)
    description = models.TextField('Mô tả chi tiết', blank=True)
    image = ResizedImageField('Ảnh đại diện', size=[900, 600], upload_to='projects/', quality=85)
    image_mobile = ImageSpecField(source='image', processors=[ResizeToFit(480, 320)], format='JPEG', options={'quality': 80})
    client = models.CharField('Khách hàng', max_length=200, blank=True)
    location = models.CharField('Địa điểm', max_length=300, blank=True)
    year = models.PositiveSmallIntegerField('Năm thực hiện', null=True, blank=True)
    is_featured = models.BooleanField('Nổi bật (hiện trang chủ)', default=False)
    is_active = models.BooleanField('Hiển thị', default=True)
    order = models.PositiveSmallIntegerField('Thứ tự', default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Dự án'
        verbose_name_plural = 'Dự án'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'slug': self.slug})


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        related_name='images', verbose_name='Dự án'
    )
    image = ResizedImageField('Hình ảnh', size=[1200, 800], upload_to='projects/gallery/', quality=85)
    image_mobile = ImageSpecField(source='image', processors=[ResizeToFit(576, 384)], format='JPEG', options={'quality': 80})
    alt = models.CharField('Alt text', max_length=200, blank=True)
    order = models.PositiveSmallIntegerField('Thứ tự', default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Hình ảnh dự án'
        verbose_name_plural = 'Hình ảnh dự án'

    def __str__(self):
        return f'{self.project.name} - ảnh {self.order}'
