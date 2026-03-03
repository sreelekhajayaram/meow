from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('booking/', include('booking.urls')),
    path('feedback/', include('feedback.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin-panel/', include('adminpanel.urls')),
]

# Serve media files in both DEBUG and production
# In production with S3, MEDIA_URL will be the S3 bucket URL
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
