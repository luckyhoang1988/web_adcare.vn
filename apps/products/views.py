from django.db.models import F
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Product, ProductCategory, build_category_tree, collect_descendant_ids


def _category_context():
    """Trả về (cây danh mục gốc cho sidebar, list phẳng cho chips mobile)."""
    flat = list(ProductCategory.objects.filter(is_active=True).order_by('order'))
    roots = build_category_tree(flat)   # gắn .children_list lên từng node trong flat
    return roots, flat


class ProductListView(ListView):
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'], ctx['categories_flat'] = _category_context()
        ctx['page_title'] = 'Sản phẩm'
        ctx['pagination_base_url'] = '?'
        ctx['open_category_ids'] = set()
        return ctx


class ProductCategoryView(ListView):
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(ProductCategory, slug=self.kwargs['cat_slug'], is_active=True)
        all_cats = list(ProductCategory.objects.filter(is_active=True))
        ids = collect_descendant_ids(self.category, all_cats)
        return Product.objects.filter(category_id__in=ids, is_active=True).select_related('category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'], ctx['categories_flat'] = _category_context()
        ctx['current_category'] = self.category
        ctx['page_title'] = self.category.name
        ctx['pagination_base_url'] = '?'
        ancestors = self.category.get_ancestors()
        ctx['open_category_ids'] = {c.pk for c in ancestors} | {self.category.pk}
        crumbs = [{'name': 'Sản phẩm', 'url': reverse('product_list')}]
        for anc in ancestors:
            crumbs.append({'name': anc.name, 'url': anc.get_absolute_url()})
        crumbs.append({'name': self.category.name, 'url': None})
        ctx['breadcrumbs'] = crumbs
        return ctx


class ProductDetailView(DetailView):
    template_name = 'products/detail.html'
    context_object_name = 'product'

    def get_object(self):
        product = get_object_or_404(Product, slug=self.kwargs['slug'], is_active=True)
        Product.objects.filter(pk=product.pk).update(view_count=F('view_count') + 1)
        return product

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['related_products'] = Product.objects.filter(
            category=self.object.category, is_active=True
        ).select_related('category').exclude(pk=self.object.pk)[:4]
        cat = self.object.category
        crumbs = [{'name': 'Sản phẩm', 'url': reverse('product_list')}]
        if cat:
            for anc in cat.get_ancestors():
                crumbs.append({'name': anc.name, 'url': anc.get_absolute_url()})
            crumbs.append({'name': cat.name, 'url': cat.get_absolute_url()})
        crumbs.append({'name': self.object.name, 'url': None})
        ctx['breadcrumbs'] = crumbs
        return ctx
