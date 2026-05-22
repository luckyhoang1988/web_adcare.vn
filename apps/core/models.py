from django.db import models
from django.utils.text import slugify
from django_resized import ResizedImageField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit

_VI_CHARS = {
    'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a', 'å': 'a',
    'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
    'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
    'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o', 'ø': 'o',
    'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
    'ý': 'y', 'ÿ': 'y', 'ç': 'c', 'ñ': 'n',
    # Tiếng Việt
    'đ': 'd', 'Đ': 'd',
    'ă': 'a', 'ắ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
    'Ă': 'a', 'Ắ': 'a', 'Ằ': 'a', 'Ẳ': 'a', 'Ẵ': 'a', 'Ặ': 'a',
    'ấ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
    'Â': 'a', 'Ấ': 'a', 'Ầ': 'a', 'Ẩ': 'a', 'Ẫ': 'a', 'Ậ': 'a',
    'ế': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
    'Ê': 'e', 'Ế': 'e', 'Ề': 'e', 'Ể': 'e', 'Ễ': 'e', 'Ệ': 'e',
    'ố': 'o', 'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
    'Ô': 'o', 'Ố': 'o', 'Ồ': 'o', 'Ổ': 'o', 'Ỗ': 'o', 'Ộ': 'o',
    'ơ': 'o', 'ớ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
    'Ơ': 'o', 'Ớ': 'o', 'Ờ': 'o', 'Ở': 'o', 'Ỡ': 'o', 'Ợ': 'o',
    'ư': 'u', 'ứ': 'u', 'ừ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
    'Ư': 'u', 'Ứ': 'u', 'Ừ': 'u', 'Ử': 'u', 'Ữ': 'u', 'Ự': 'u',
    'ỉ': 'i', 'ị': 'i', 'Ỉ': 'i', 'Ị': 'i',
    'ũ': 'u', 'ủ': 'u', 'ụ': 'u', 'Ũ': 'u', 'Ủ': 'u', 'Ụ': 'u',
    'ĩ': 'i', 'Ĩ': 'i',
    'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    'Ỳ': 'y', 'Ỷ': 'y', 'Ỹ': 'y', 'Ỵ': 'y',
}


def vi_slugify(text):
    text = ''.join(_VI_CHARS.get(c, c) for c in text)
    return slugify(text)


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
    slug = models.SlugField(
        'Slug (URL)', max_length=200, unique=True, blank=True,
        help_text='Tự động tạo từ tiêu đề. URL trang: /gioi-thieu/&lt;slug&gt;/'
    )
    subtitle = models.CharField('Tiêu đề phụ', max_length=300, blank=True)
    content = models.TextField('Nội dung')
    image = ResizedImageField('Hình ảnh', size=[700, 500], upload_to='about/', quality=85)
    image_mobile = ImageSpecField(source='image', processors=[ResizeToFit(480, 343)], format='JPEG', options={'quality': 80})
    image_alt = models.CharField('Alt text ảnh', max_length=200, blank=True)
    button_text = models.CharField('Nút - Text', max_length=50, default='Xem thêm')
    button_url = models.CharField('Nút - URL', max_length=200, default='/ve-chung-toi/')
    meta_title = models.CharField('Meta Title', max_length=200, blank=True,
                                  help_text='Tiêu đề SEO. Để trống sẽ dùng tiêu đề chính.')
    meta_desc = models.TextField('Meta Description', max_length=300, blank=True)
    is_active = models.BooleanField('Hiển thị', default=True)
    show_in_menu = models.BooleanField(
        'Hiển thị trong menu dropdown', default=False,
        help_text='Bật để section này tự xuất hiện trong dropdown của menu "Về chúng tôi" mà không cần tạo MenuItem.'
    )
    auto_add_menu = models.BooleanField(
        'Tự động thêm vào menu', default=False,
        help_text='Khi bật, section này sẽ tự động tạo một mục trong menu điều hướng.'
    )
    menu_parent = models.ForeignKey(
        'MenuItem', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='+', verbose_name='Hiển thị là menu con của',
        limit_choices_to={'parent': None},
        help_text='Chọn menu cha để hiển thị dưới dạng menu con. Để trống = thêm vào menu cấp 1 (menu chính).'
    )
    menu_order = models.PositiveSmallIntegerField('Thứ tự trong menu', default=99)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Section Giới thiệu'
        verbose_name_plural = 'Section Giới thiệu'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base = vi_slugify(self.title)
            slug = base
            counter = 2
            while AboutSection.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        if self.slug:
            return reverse('about_detail', kwargs={'slug': self.slug})
        return reverse('about')


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
    DROPDOWN_STYLES = [
        ('list', 'Danh sách đơn giản'),
        ('grid', 'Lưới 2 cột (có icon)'),
        ('mega', 'Mega menu (có mô tả)'),
    ]
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,
                               related_name='children', verbose_name='Menu cha',
                               help_text='Để trống = menu cấp 1. Chọn menu cha = menu con (dropdown).')
    title = models.CharField('Tên hiển thị', max_length=100)
    item_type = models.CharField('Loại trang', max_length=20, choices=ITEM_TYPES, default='custom')
    url = models.CharField('URL', max_length=200, blank=True,
                           help_text='Bắt buộc với loại "Link tùy chỉnh". VD: /gioi-thieu/')
    icon = models.CharField('Icon (FontAwesome)', max_length=60, blank=True,
                            help_text='VD: fas fa-camera. Dùng cho kiểu dropdown Lưới/Mega.')
    description = models.CharField('Mô tả ngắn', max_length=200, blank=True,
                                   help_text='Dùng cho kiểu dropdown Mega menu.')
    dropdown_style = models.CharField('Kiểu dropdown', max_length=10, choices=DROPDOWN_STYLES,
                                      default='list',
                                      help_text='Chỉ áp dụng khi menu cấp 1 có menu con.')
    order = models.PositiveSmallIntegerField('Thứ tự', default=0)
    is_active = models.BooleanField('Hiển thị', default=True)
    open_in_new_tab = models.BooleanField('Mở tab mới', default=False)

    class Meta:
        ordering = ['order']
        verbose_name = 'Menu item'
        verbose_name_plural = 'Menu chính'

    def __str__(self):
        if self.parent:
            return f'↳ {self.title}'
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
