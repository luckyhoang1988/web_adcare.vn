from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Project, ProjectCategory


class ProjectListView(ListView):
    template_name = 'projects/list.html'
    context_object_name = 'projects'
    paginate_by = 9

    def get_queryset(self):
        qs = Project.objects.filter(is_active=True).select_related('category')
        slug = self.request.GET.get('danh-muc')
        if slug:
            qs = qs.filter(category__slug=slug)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = ProjectCategory.objects.filter(is_active=True)
        ctx['page_title'] = 'Dự án'
        slug = self.request.GET.get('danh-muc')
        if slug:
            ctx['current_category'] = get_object_or_404(ProjectCategory, slug=slug, is_active=True)
        else:
            ctx['current_category'] = None
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
        return ctx
