from django.db import models
from django_resized import ResizedImageField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit


class SiteConfig(models.Model):
    company_name = models.CharField('Tên công ty', max_length=200, default='ADCARE Việt Nam')
    company_name_en = models.CharField('Tên tiếng Anh', max_length=200, blank=True)
    slogan = models.CharField('Slogan', max_length=300, blank=True)
    logo = ResizedImageField('Logo', size=[300, 100], upload_to='site/', blank=True)
    favicon = models.ImageField('Favicon', upload_to='site/', blank=True)
    address = models.TextField('Địa chỉ', blank=True)
    phone = models.CharField('Điện thoại', max_length=20, blank=True)
    phone_2 = models.CharField('Điện thoại 2', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    email_2 = models.EmailField('Email 2', blank=True)
    facebook_url = models.URLField('Facebook', blank=True)
    youtube_url = models.URLField('YouTube', blank=True)
    zalo_url = models.URLField('Zalo', blank=True)
    linkedin_url = models.URLField('LinkedIn', blank=True)
    google_maps_embed = models.TextField('Google Maps (iframe)', blank=True)
    working_hours = models.TextField(
        'Giờ làm việc', blank=True,
        default='Thứ 2 - Thứ 7: 8:00 - 17:30\nChủ nhật: 8:00 - 12:00',
        help_text='Mỗi dòng một khung giờ. VD: Thứ 2 - Thứ 7: 8:00 - 17:30'
    )
    footer_description = models.TextField(
        'Mô tả footer', blank=True,
        help_text='Đoạn giới thiệu ngắn hiển thị ở footer. Để trống sẽ dùng slogan.'
    )
    meta_description = models.TextField('Meta Description', blank=True)
    meta_keywords = models.TextField('Meta Keywords', blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cấu hình Website'
        verbose_name_plural = 'Cấu hình Website'

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Slider(models.Model):
    title = models.CharField('Tiêu đề', max_length=200)
    subtitle = models.TextField('Mô tả', blank=True)
    image = ResizedImageField('Hình ảnh', size=[1920, 800], upload_to='sliders/', quality=85)
    image_mobile = ImageSpecField(source='image', processors=[ResizeToFit(576, 400)], format='JPEG', options={'quality': 80})
    button_text = models.CharField('Nút 1 - Text', max_length=50, default='Xem thêm')
    button_url = models.CharField('Nút 1 - URL', max_length=200, default='#')
    button2_text = models.CharField('Nút 2 - Text', max_length=50, blank=True)
    button2_url = models.CharField('Nút 2 - URL', max_length=200, blank=True)
    order = models.PositiveSmallIntegerField('Thứ tự', default=0)
    is_active = models.BooleanField('Hiển thị', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Slide Banner'
        verbose_name_plural = 'Slide Banners'

    def __str__(self):
        return self.title


class StatItem(models.Model):
    icon = models.CharField('Icon (FontAwesome)', max_length=60, default='fas fa-users',
                            help_text='VD: fas fa-users, fas fa-project-diagram')
    number = models.CharField('Số liệu', max_length=20, help_text='VD: 100+, 1000+')
    label = models.CharField('Nhãn', max_length=100)
    description = models.CharField('Mô tả phụ', max_length=200, blank=True)
    order = models.PositiveSmallIntegerField('Thứ tự', default=0)
    is_active = models.BooleanField('Hiển thị', default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Chỉ số thống kê'
        verbose_name_plural = 'Các chỉ số thống kê'

    def __str__(self):
        return f'{self.number} {self.label}'


class AboutSection(models.Model):
    title = models.CharField('Tiêu đề', max_length=200)
    subtitle = models.CharField('Tiêu đề phụ', max_length=300, blank=True)
    content = models.TextField('Nội dung')
    image = ResizedImageField('Hình ảnh', size=[700, 500], upload_to='about/', quality=85)
    image_mobile = ImageSpecField(source='image', processors=[ResizeToFit(480, 343)], format='JPEG', options={'quality': 80})
    image_alt = models.CharField('Alt text ảnh', max_length=200, blank=True)
    button_text = models.CharField('Nút - Text', max_length=50, default='Xem thêm')
    button_url = models.CharField('Nút - URL', max_length=200, default='/ve-chung-toi/')
    is_active = models.BooleanField('Hiển thị', default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Section Giới thiệu'
        verbose_name_plural = 'Section Giới thiệu'

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    ITEM_TYPES = [
        ('home', 'Trang chủ'),
        ('about', 'Về chúng tôi'),
        ('products', 'Sản phẩm (+ dropdown danh mục)'),
        ('services', 'Dịch vụ (+ dropdown danh mục)'),
        ('projects', 'Dự án'),
        ('news', 'Tin tức'),
        ('contact', 'Liên hệ'),
        ('custom', 'Link tùy chỉnh'),
    ]
    title = models.CharField('Tên hiển thị', max_length=100)
    item_type = models.CharField('Loại', max_length=20, choices=ITEM_TYPES, default='custom')
    url = models.CharField('URL', max_length=200, blank=True,
                           help_text='Chỉ dùng cho loại "Link tùy chỉnh". VD: /gioi-thieu/')
    order = models.PositiveSmallIntegerField('Thứ tự', default=0)
    is_active = models.BooleanField('Hiển thị', default=True)
    open_in_new_tab = models.BooleanField('Mở tab mới', default=False)

    class Meta:
        ordering = ['order']
        verbose_name = 'Menu item'
        verbose_name_plural = 'Menu chính'

    def __str__(self):
        return self.title


class AboutFeature(models.Model):
    about = models.ForeignKey(AboutSection, on_delete=models.CASCADE,
                              related_name='features', verbose_name='Section')
    icon = models.CharField('Icon (FontAwesome)', max_length=60, default='fas fa-check-circle',
                            help_text='VD: fas fa-check-circle, fas fa-shield-alt')
    text = models.CharField('Nội dung', max_length=200)
    order = models.PositiveSmallIntegerField('Thứ tự', default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Điểm nổi bật'
        verbose_name_plural = 'Điểm nổi bật'

    def __str__(self):
        return self.text
