from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('<slug:cat_slug>/', views.ProductCategoryView.as_view(), name='product_category'),
    path('<slug:cat_slug>/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
]
