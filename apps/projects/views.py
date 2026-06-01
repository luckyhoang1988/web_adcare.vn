from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Project, ProjectCategory


class ProjectListView(ListView):
    template_name = 'projects/list.html'
    context_object_name = 'projects'
    paginate_by = 9

    def get_queryset(self):
        qs = Project.objects.filter(is_active=True).select_related('category')
        self.current_category = None
        slug = self.request.GET.get('danh-muc')
        if slug:
            self.current_category = get_object_or_404(ProjectCategory, slug=slug, is_active=True)
            qs = qs.filter(category=self.current_category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = ProjectCategory.objects.filter(is_active=True)
        ctx['page_title'] = 'Dự án'
        ctx['current_category'] = self.current_category
        if self.current_category:
            ctx['pagination_base_url'] = f'?danh-muc={self.current_category.slug}&'
        else:
            ctx['pagination_base_url'] = '?'
        return ctx


class ProjectDetailView(DetailView):
    template_name = 'projects/detail.html'
    context_object_name = 'project'

    def get_object(self):
        return get_object_or_404(Project, slug=self.kwargs['slug'], is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['other_projects'] = Project.objects.filter(is_active=True).select_related('category').exclude(pk=self.object.pk)[:4]
        ctx['gallery'] = self.object.images.all()
        cat = self.object.category
        crumbs = [{'name': 'Dự án', 'url': reverse('project_list')}]
        if cat:
            crumbs.append({'name': cat.name, 'url': f"{reverse('project_list')}?danh-muc={cat.slug}"})
        crumbs.append({'name': self.object.name, 'url': None})
        ctx['breadcrumbs'] = crumbs
        return ctx
