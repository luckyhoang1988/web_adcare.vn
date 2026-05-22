from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_resized import ResizedImageField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from apps.core.models import vi_slugify


class NewsCategory(models.Model):
    name = models.CharField('Tên danh mục', max_length=200)
    slug = models.SlugField('Slug', unique=True, blank=True)
    description = models.TextField('Mô tả', blank=True)
    order = models.PositiveSmallIntegerField('Thứ tự', default=0)
    is_active = models.BooleanField('Hiển thị', default=True)
    show_in_menu = models.BooleanField('Hiển thị trong menu', default=True,
                                       help_text='Bật để danh mục này xuất hiện trong dropdown menu điều hướng.')

    class Meta:
        ordering = ['order']
        verbose_name = 'Danh mục tin tức'
        verbose_name_plural = 'Danh mục tin tức'

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base = vi_slugify(self.name)
            slug = base; i = 2
            while NewsCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{i}'; i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Bản nháp'),
        ('published', 'Đã đăng'),
    ]
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name='articles', verbose_name='Danh mục')
    title = models.CharField('Tiêu đề', max_length=300)
    slug = models.SlugField('Slug', unique=True, blank=True)
    summary = models.TextField('Tóm tắt', max_length=500, blank=True)
    content = models.TextField('Nội dung')
    image = ResizedImageField('Ảnh đại diện', size=[1200, 630], upload_to='news/', quality=85)
    image_mobile = ImageSpecField(source='image', processors=[ResizeToFit(576, 302)], format='JPEG', options={'quality': 80})
    author = models.CharField('Tác giả', max_length=100, default='ADCARE Việt Nam')
    status = models.CharField('Trạng thái', max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField('Nổi bật', default=False)
    view_count = models.PositiveIntegerField('Lượt xem', default=0)
    published_at = models.DateTimeField('Ngày đăng', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    meta_title = models.CharField('Meta Title', max_length=200, blank=True)
    meta_desc = models.TextField('Meta Description', max_length=300, blank=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'Bài viết'
        verbose_name_plural = 'Bài viết'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base = vi_slugify(self.title)
            slug = base; i = 2
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{i}'; i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news_detail', kwargs={'slug': self.slug})

    def publish(self):
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()
