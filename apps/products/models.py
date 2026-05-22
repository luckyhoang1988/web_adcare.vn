from django.db import models
from django.urls import reverse
from django_resized import ResizedImageField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit


class ProductCategory(models.Model):
    name = models.CharField('Tên danh mục', max_length=200)
    slug = models.SlugField('Slug', unique=True, allow_unicode=True)
    description = models.TextField('Mô tả', blank=True)
    image = ResizedImageField('Hình ảnh', size=[800, 600], upload_to='products/categories/', blank=True, quality=85)
    image_mobile = ImageSpecField(source='image', processors=[ResizeToFit(480, 360)], format='JPEG', options={'quality': 80})
    icon = models.CharField('Icon (FontAwesome)', max_length=100, blank=True,
                            help_text='VD: fas fa-camera, fas fa-shield-alt')
    order = models.PositiveSmallIntegerField('Thứ tự', default=0)
    is_active = models.BooleanField('Hiển thị', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Danh mục sản phẩm'
        verbose_name_plural = 'Danh mục sản phẩm'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_category', kwargs={'cat_slug': self.slug})


class Product(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL,
                                  null=True, related_name='products', verbose_name='Danh mục')
    name = models.CharField('Tên sản phẩm', max_length=300)
    slug = models.SlugField('Slug', unique=True, allow_unicode=True)
    short_desc = models.TextField('Mô tả ngắn', max_length=500, blank=True)
    description = models.TextField('Mô tả chi tiết', blank=True)
    image = ResizedImageField('Hình ảnh chính', size=[800, 600], upload_to='products/', quality=85)
    image_mobile = ImageSpecField(source='image', processors=[ResizeToFit(480, 360)], format='JPEG', options={'quality': 80})
    brand = models.CharField('Thương hiệu', max_length=100, blank=True)
    model_number = models.CharField('Model', max_length=100, blank=True)
    specifications = models.TextField('Thông số kỹ thuật', blank=True)
    is_featured = models.BooleanField('Nổi bật (hiện trang chủ)', default=False)
    is_active = models.BooleanField('Hiển thị', default=True)
    order = models.PositiveSmallIntegerField('Thứ tự', default=0)
    view_count = models.PositiveIntegerField('Lượt xem', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Sản phẩm'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if not self.category_id:
            return reverse('product_list')
        return reverse('product_detail', kwargs={
            'cat_slug': self.category.slug,
            'slug': self.slug
        })


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                 related_name='images', verbose_name='Sản phẩm')
    image = ResizedImageField('Hình ảnh', size=[800, 600], upload_to='products/gallery/', quality=85)
    image_mobile = ImageSpecField(source='image', processors=[ResizeToFit(480, 360)], format='JPEG', options={'quality': 80})
    alt = models.CharField('Alt text', max_length=200, blank=True)
    order = models.PositiveSmallIntegerField('Thứ tự', default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Ảnh sản phẩm'
        verbose_name_plural = 'Gallery sản phẩm'

    def __str__(self):
        return f'Ảnh {self.order} - {self.product.name}'
