from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Service, ServiceCategory
from apps.core.models import collect_descendant_ids


class ServiceListView(ListView):
    template_name = 'services/list.html'
    context_object_name = 'services'
    paginate_by = 9

    def get_queryset(self):
        qs = Service.objects.filter(is_active=True).select_related('category')
        self.current_category = None
        slug = self.request.GET.get('danh-muc')
        if slug:
            self.current_category = get_object_or_404(ServiceCategory, slug=slug, is_active=True)
            all_cats = list(ServiceCategory.objects.filter(is_active=True))
            ids = collect_descendant_ids(self.current_category, all_cats)
            qs = qs.filter(category_id__in=ids)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = ServiceCategory.objects.filter(is_active=True)
        ctx['page_title'] = 'Dịch vụ'
        ctx['current_category'] = self.current_category
        if self.current_category:
            ctx['pagination_base_url'] = f'?danh-muc={self.current_category.slug}&'
        else:
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
        cat = self.object.category
        crumbs = [{'name': 'Dịch vụ', 'url': reverse('service_list')}]
        if cat:
            for anc in cat.get_ancestors():
                crumbs.append({'name': anc.name, 'url': anc.get_absolute_url()})
            crumbs.append({'name': cat.name, 'url': cat.get_absolute_url()})
        crumbs.append({'name': self.object.name, 'url': None})
        ctx['breadcrumbs'] = crumbs
        return ctx
