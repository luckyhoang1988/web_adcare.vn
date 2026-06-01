from django.db import models
from django_resized import ResizedImageField


class Partner(models.Model):
    PARTNER_TYPE = [
        ('partner', 'Đối tác'),
        ('agent', 'Đại lý chính thức'),
        ('supplier', 'Nhà cung cấp'),
        ('customer', 'Khách hàng tiêu biểu'),
    ]
    name = models.CharField('Tên đối tác', max_length=200)
    logo = ResizedImageField('Logo', size=[300, 150], upload_to='partners/', quality=90)
    website = models.URLField('Website', blank=True)
    partner_type = models.CharField('Loại', max_length=20, choices=PARTNER_TYPE, default='partner')
    description = models.TextField('Mô tả', blank=True)
    order = models.PositiveSmallIntegerField('Thứ tự', default=0)
    is_active = models.BooleanField('Hiển thị', default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Đối tác'
        verbose_name_plural = 'Đối tác & Đại lý'

    def __str__(self):
        return self.name
