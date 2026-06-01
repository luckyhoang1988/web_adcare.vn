from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('tim-kiem/', views.SearchView.as_view(), name='search'),
    path('ve-chung-toi/', views.AboutView.as_view(), name='about'),
    path('gioi-thieu/<slug:slug>/', views.AboutDetailView.as_view(), name='about_detail'),
]
