from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from azbankgateways.urls import az_bank_gateways_urls

admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls', namespace='core')),
    path('bankgateways/', az_bank_gateways_urls()),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
