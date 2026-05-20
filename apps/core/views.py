from django.views.generic import TemplateView
from apps.products.models import Product
from apps.services.models import Service
from apps.news.models import Article
from apps.partners.models import Partner
from .models import Slider, StatItem, AboutSection


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['sliders'] = Slider.objects.filter(is_active=True)
        ctx['stat_items'] = StatItem.objects.filter(is_active=True)
        ctx['about'] = AboutSection.objects.filter(is_active=True).first()
        ctx['featured_products'] = Product.objects.filter(is_featured=True, is_active=True)[:6]
        ctx['featured_services'] = Service.objects.filter(is_featured=True, is_active=True)[:6]
        ctx['partners'] = Partner.objects.filter(is_active=True)
        ctx['recent_news'] = Article.objects.filter(status='published')[:3]
        return ctx


class AboutView(TemplateView):
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['about'] = AboutSection.objects.filter(is_active=True).first()
        ctx['stat_items'] = StatItem.objects.filter(is_active=True)
        ctx['partners'] = Partner.objects.filter(is_active=True)
        return ctx
