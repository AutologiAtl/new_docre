import statistics
from .views import Hello
from django.urls import path
from django.conf.urls.static import static
from Atl_Dockery import settings
# from .views import (Hello)

urlpatterns = [
    # path('', LoginView.as_view(), name='login'),
    path('', Hello, name='Hello'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Add the following lines to serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
