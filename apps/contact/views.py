from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from .forms import ContactForm
from .models import ContactMessage


class ContactView(FormView):
    template_name = 'contact/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact_success')

    def form_valid(self, form):
        obj = form.save(commit=False)
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            obj.ip_address = x_forwarded_for.split(',')[0]
        else:
            obj.ip_address = self.request.META.get('REMOTE_ADDR')
        obj.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Liên hệ'
        return ctx


class ContactSuccessView(TemplateView):
    template_name = 'contact/success.html'
