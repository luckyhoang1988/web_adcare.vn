from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('san-pham/', include('apps.products.urls')),
    path('dich-vu/', include('apps.services.urls')),
    path('tin-tuc/', include('apps.news.urls')),
    path('lien-he/', include('apps.contact.urls')),
    path('du-an/', include('apps.projects.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
