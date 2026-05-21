from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.products.models import Product
from apps.services.models import Service
from apps.news.models import Article
from apps.projects.models import Project


class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = 'monthly'

    def items(self):
        return ['home', 'about', 'product_list', 'service_list', 'news_list', 'project_list', 'contact']

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Product.objects.filter(is_active=True).select_related('category')

    def lastmod(self, obj):
        return obj.updated_at


class ServiceSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Service.objects.filter(is_active=True)


class ArticleSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Article.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at


class ProjectSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Project.objects.filter(is_active=True)
