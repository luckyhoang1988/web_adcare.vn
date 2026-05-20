from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Article, NewsCategory


class ArticleListView(ListView):
    template_name = 'news/list.html'
    context_object_name = 'articles'
    paginate_by = 9

    def get_queryset(self):
        qs = Article.objects.filter(status='published').select_related('category')
        cat_slug = self.request.GET.get('danh-muc')
        if cat_slug:
            self.current_category = get_object_or_404(NewsCategory, slug=cat_slug)
            qs = qs.filter(category=self.current_category)
        else:
            self.current_category = None
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = NewsCategory.objects.filter(is_active=True)
        ctx['current_category'] = getattr(self, 'current_category', None)
        ctx['page_title'] = 'Tin tức'
        return ctx


class ArticleDetailView(DetailView):
    template_name = 'news/detail.html'
    context_object_name = 'article'

    def get_object(self):
        article = get_object_or_404(Article, slug=self.kwargs['slug'], status='published')
        article.view_count += 1
        article.save(update_fields=['view_count'])
        return article

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['related_articles'] = Article.objects.filter(
            status='published', category=self.object.category
        ).exclude(pk=self.object.pk)[:3]
        return ctx
