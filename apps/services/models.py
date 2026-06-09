from django.db import models
from django.urls import reverse
from django_resized import ResizedImageField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from apps.core.models import unique_slugify


class ServiceCategory(models.Model):
    name = models.CharField('Tên danh mục', max_length=200)
    slug = models.SlugField('Slug', unique=True, blank=True)
    description = models.TextField('Mô tả', blank=True)
    icon = models.CharField('Icon (FontAwesome)', max_length=100, blank=True)
    image = ResizedImageField('Hình ảnh', size=[800, 600], upload_to='services/categories/', blank=True, quality=85)
    image_mobile = ImageSpecField(source='image', processors=[ResizeToFit(480, 360)], format='JPEG', options={'quality': 80})
    order = models.PositiveSmallIntegerField('Thứ tự', default=0)
    is_active = models.BooleanField('Hiển thị', default=True, db_index=True)
    show_in_menu = models.BooleanField('Hiển thị trong menu', default=True,
                                       help_text='Bật để danh mục này xuất hiện trong dropdown menu điều hướng.')

    class Meta:
        ordering = ['order']
        verbose_name = 'Danh mục dịch vụ'
        verbose_name_plural = 'Danh mục dịch vụ'

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name='services', verbose_name='Danh mục')
    name = models.CharField('Tên dịch vụ', max_length=300)
    slug = models.SlugField('Slug', unique=True, blank=True)
    short_desc = models.TextField('Mô tả ngắn', max_length=500, blank=True)
    description = models.TextField('Mô tả chi tiết', blank=True)
    image = ResizedImageField('Hình ảnh', size=[800, 600], upload_to='services/', quality=85)
    image_mobile = ImageSpecField(source='image', processors=[ResizeToFit(480, 360)], format='JPEG', options={'quality': 80})
    icon = models.CharField('Icon (FontAwesome)', max_length=100, blank=True)
    is_featured = models.BooleanField('Nổi bật (hiện trang chủ)', default=False)
    is_active = models.BooleanField('Hiển thị', default=True, db_index=True)
    order = models.PositiveSmallIntegerField('Thứ tự', default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Dịch vụ'
        verbose_name_plural = 'Dịch vụ'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('service_detail', kwargs={'slug': self.slug})
