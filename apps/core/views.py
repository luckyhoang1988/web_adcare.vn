from django.views.generic import TemplateView, DetailView
from django.core.paginator import Paginator
from django.db.models import Q
from apps.products.models import Product
from apps.services.models import Service
from apps.solutions.models import Solution
from apps.news.models import Article
from apps.projects.models import Project
from apps.partners.models import Partner
from .models import Slider, StatItem, AboutSection


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['sliders'] = Slider.objects.filter(is_active=True)[:10]
        ctx['stat_items'] = StatItem.objects.filter(is_active=True)
        ctx['about'] = AboutSection.objects.filter(is_active=True).prefetch_related('features').first()
        ctx['featured_products'] = Product.objects.filter(is_active=True).select_related('category').order_by('-created_at')[:6]
        ctx['featured_services'] = Service.objects.filter(is_active=True).select_related('category').order_by('-created_at')[:6]
        ctx['featured_solutions'] = Solution.objects.filter(is_featured=True, is_active=True).select_related('category')
        ctx['featured_projects'] = Project.objects.filter(is_featured=True, is_active=True).select_related('category')[:6]
        ctx['partners'] = Partner.objects.filter(is_active=True)[:12]
        ctx['recent_news'] = Article.objects.filter(status='published').select_related('category').order_by('-published_at')[:3]
        return ctx


class AboutView(TemplateView):
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['about'] = AboutSection.objects.filter(is_active=True).first()
        ctx['stat_items'] = StatItem.objects.filter(is_active=True)
        ctx['partners'] = Partner.objects.filter(is_active=True)
        return ctx


class AboutDetailView(DetailView):
    model = AboutSection
    template_name = 'core/about_detail.html'
    context_object_name = 'about'
    queryset = AboutSection.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        about = self.object
        ctx['stat_items'] = StatItem.objects.filter(is_active=True)
        ctx['partners'] = Partner.objects.filter(is_active=True)
        ctx['breadcrumbs'] = [
            {'name': 'Giới thiệu', 'url': '/ve-chung-toi/'},
            {'name': about.title, 'url': None},
        ]
        return ctx


class SearchView(TemplateView):
    template_name = 'search/results.html'
    paginate_by = 9

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        ctx['query'] = query
        ctx['pagination_base_url'] = f'?q={query}&'

        results = []
        if query:
            def add(items, type_label, title_attr, desc_attr):
                for obj in items:
                    results.append({
                        'type': type_label,
                        'title': getattr(obj, title_attr),
                        'desc': getattr(obj, desc_attr, ''),
                        'url': obj.get_absolute_url(),
                        'image': obj.image,
                        'image_mobile': obj.image_mobile,
                    })

            add(Product.objects.filter(is_active=True)
                .filter(Q(name__icontains=query) | Q(short_desc__icontains=query) | Q(brand__icontains=query))
                .select_related('category'), 'Sản phẩm', 'name', 'short_desc')
            add(Service.objects.filter(is_active=True)
                .filter(Q(name__icontains=query) | Q(short_desc__icontains=query))
                .select_related('category'), 'Dịch vụ', 'name', 'short_desc')
            add(Project.objects.filter(is_active=True)
                .filter(Q(name__icontains=query) | Q(short_desc__icontains=query) | Q(client__icontains=query))
                .select_related('category'), 'Dự án', 'name', 'short_desc')
            add(Article.objects.filter(status='published')
                .filter(Q(title__icontains=query) | Q(summary__icontains=query))
                .select_related('category'), 'Tin tức', 'title', 'summary')

        paginator = Paginator(results, self.paginate_by)
        page_obj = paginator.get_page(self.request.GET.get('page'))
        ctx['page_obj'] = page_obj
        ctx['paginator'] = paginator
        ctx['is_paginated'] = page_obj.has_other_pages()
        ctx['results'] = page_obj.object_list
        ctx['total_count'] = paginator.count
        return ctx
