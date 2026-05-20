from django.db import models


class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'Mới'),
        ('read', 'Đã đọc'),
        ('replied', 'Đã phản hồi'),
        ('closed', 'Đã đóng'),
    ]
    full_name = models.CharField('Họ và tên', max_length=200)
    email = models.EmailField('Email')
    phone = models.CharField('Điện thoại', max_length=20, blank=True)
    company = models.CharField('Công ty', max_length=200, blank=True)
    subject = models.CharField('Chủ đề', max_length=300)
    message = models.TextField('Nội dung')
    status = models.CharField('Trạng thái', max_length=20, choices=STATUS_CHOICES, default='new')
    ip_address = models.GenericIPAddressField('IP', null=True, blank=True)
    created_at = models.DateTimeField('Thời gian gửi', auto_now_add=True)
    replied_at = models.DateTimeField('Thời gian phản hồi', null=True, blank=True)
    admin_notes = models.TextField('Ghi chú admin', blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Tin nhắn liên hệ'
        verbose_name_plural = 'Tin nhắn liên hệ'

    def __str__(self):
        return f'{self.full_name} - {self.subject}'
