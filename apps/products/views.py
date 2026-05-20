from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Product, ProductCategory


class ProductListView(ListView):
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = ProductCategory.objects.filter(is_active=True)
        ctx['page_title'] = 'Sản phẩm'
        return ctx


class ProductCategoryView(ListView):
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(ProductCategory, slug=self.kwargs['cat_slug'], is_active=True)
        return Product.objects.filter(category=self.category, is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = ProductCategory.objects.filter(is_active=True)
        ctx['current_category'] = self.category
        ctx['page_title'] = self.category.name
        return ctx


class ProductDetailView(DetailView):
    template_name = 'products/detail.html'
    context_object_name = 'product'

    def get_object(self):
        product = get_object_or_404(Product, slug=self.kwargs['slug'], is_active=True)
        product.view_count += 1
        product.save(update_fields=['view_count'])
        return product

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.get_object()
        ctx['related_products'] = Product.objects.filter(
            category=product.category, is_active=True
        ).exclude(pk=product.pk)[:4]
        return ctx
