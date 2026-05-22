from django.core.cache import cache
from .models import SiteConfig, MenuItem
from apps.products.models import ProductCategory
from apps.services.models import ServiceCategory, Service


def site_config(request):
    data = cache.get('global_nav')
    if data is None:
        data = {
            'site_config': SiteConfig.get(),
            'nav_menu': list(MenuItem.objects.filter(is_active=True).order_by('order')),
            'nav_categories': list(ProductCategory.objects.filter(is_active=True).order_by('order')),
            'nav_service_categories': list(ServiceCategory.objects.filter(is_active=True).order_by('order')),
            'footer_services': list(Service.objects.filter(is_active=True).order_by('order')[:6]),
        }
        cache.set('global_nav', data, 3600)
    return data
