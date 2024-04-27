from django.urls import path
# from .views import FileUploadView, homeView, index, upload_success

from django.conf.urls.static import static
from .views import FileUploadView
from Atl_Dockery import settings


urlpatterns = [
    path('trucking/', FileUploadView.as_view(), name='fileupload'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)