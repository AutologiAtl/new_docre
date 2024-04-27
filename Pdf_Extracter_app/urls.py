import statistics
from django.urls import path
from django.conf.urls.static import static
from .views import logout_view,dashboard_view
from Atl_Dockery import settings
from .views import (AjaxSaveView, ExcelDownloadView, FileUploadView, FileListView, LoginView, 
                    MscExcelView, view_files_view,downloadfile)

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    # path('logout/', LogoutView.as_view(), name='logout'),
    path('upload/', FileUploadView.as_view(), name='file_upload'),
    path('list/', FileListView.as_view(), name='file_list'),
    # path('view/', ViewFilesView.as_view(), name='view_files'),
    path('update_data/', AjaxSaveView.as_view(), name='update_data'),
    path('download_excel/', ExcelDownloadView.as_view(), name='excel_download'),
    path('MscExcelView/', MscExcelView.as_view(), name='MscExcelView'),
    path('view_files/', view_files_view, name='view_files'),
    path('download/<str:filename>/', downloadfile, name='download_file'),
    path('dashboard/', dashboard_view, name='dashboard'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Add the following lines to serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

