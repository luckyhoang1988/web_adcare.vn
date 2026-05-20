from .models import SiteConfig
from apps.products.models import ProductCategory
from apps.services.models import ServiceCategory, Service


def site_config(request):
    return {
        'site_config': SiteConfig.get(),
        'nav_categories': ProductCategory.objects.filter(is_active=True).order_by('order'),
        'nav_service_categories': ServiceCategory.objects.filter(is_active=True).order_by('order'),
        'footer_services': Service.objects.filter(is_active=True).order_by('order')[:6],
    }
