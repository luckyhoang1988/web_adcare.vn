from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from .forms import ContactForm

# Khoảng cách tối thiểu giữa 2 lần gửi từ cùng một IP (giây)
CONTACT_RATE_LIMIT_SECONDS = 60


class ContactView(FormView):
    template_name = 'contact/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact_success')

    def _get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return self.request.META.get('REMOTE_ADDR')

    def form_valid(self, form):
        ip = self._get_client_ip()

        # Rate limit theo IP: chặn gửi liên tiếp trong khoảng quy định.
        rate_key = f'contact_ip_{ip}'
        if ip and cache.get(rate_key):
            form.add_error(None, 'Bạn vừa gửi liên hệ. Vui lòng thử lại sau ít phút.')
            return self.form_invalid(form)

        obj = form.save(commit=False)
        obj.ip_address = ip
        obj.save()

        if ip:
            cache.set(rate_key, True, CONTACT_RATE_LIMIT_SECONDS)

        self._notify_admin(obj)
        return super().form_valid(form)

    def _notify_admin(self, obj):
        recipient = getattr(settings, 'CONTACT_NOTIFY_EMAIL', None)
        if not recipient:
            return
        subject = f'[Liên hệ website] {obj.subject}'
        body = (
            f'Họ tên: {obj.full_name}\n'
            f'Email: {obj.email}\n'
            f'Điện thoại: {obj.phone}\n'
            f'Công ty: {obj.company}\n'
            f'Chủ đề: {obj.subject}\n\n'
            f'Nội dung:\n{obj.message}\n\n'
            f'IP: {obj.ip_address}'
        )
        send_mail(
            subject, body,
            getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            [recipient],
            fail_silently=True,
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Liên hệ'
        return ctx


class ContactSuccessView(TemplateView):
    template_name = 'contact/success.html'
