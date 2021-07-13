from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    path("files/", views.files),
    path("files/<str:identifier>/", views.file_detail_view, name='file_detail'),
    path("files/download/<str:identifier>/", views.download_file_view),
    path("files/validatefile/<str:identifier>/", views.validate_file),
    path("files/share_file/<str:username>/<str:identifier>/", views.share_file),
    path("testie/", views.test_link)
]