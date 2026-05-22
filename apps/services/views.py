from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Service, ServiceCategory


class ServiceListView(ListView):
    template_name = 'services/list.html'
    context_object_name = 'services'
    paginate_by = 9

    def get_queryset(self):
        qs = Service.objects.filter(is_active=True).select_related('category')
        slug = self.request.GET.get('danh-muc')
        if slug:
            qs = qs.filter(category__slug=slug)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = ServiceCategory.objects.filter(is_active=True)
        ctx['page_title'] = 'Dịch vụ'
        slug = self.request.GET.get('danh-muc')
        if slug:
            ctx['current_category'] = get_object_or_404(ServiceCategory, slug=slug, is_active=True)
            ctx['pagination_base_url'] = f'?danh-muc={slug}&'
        else:
            ctx['current_category'] = None
            ctx['pagination_base_url'] = '?'
        return ctx


class ServiceDetailView(DetailView):
    template_name = 'services/detail.html'
    context_object_name = 'service'

    def get_object(self):
        return get_object_or_404(Service, slug=self.kwargs['slug'], is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['other_services'] = Service.objects.filter(is_active=True).select_related('category').exclude(
            pk=self.object.pk)[:4]
        return ctx
