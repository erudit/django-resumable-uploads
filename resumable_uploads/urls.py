from django.conf.urls import url

from . import views


urlpatterns = [
    # the url where the upload petition is processed
    url(r'^resumable_uploads/resumable-file/(?P<pk>[\d-]+)/delete/$',
        views.ResumableFileDeleteView.as_view(), name='resumable_file_delete'),

    # the url where the upload petition is processed
    url(r'^resumable_uploads/set_file_info', views.set_file_info, name='set_file_info'),

    # the url where the upload petition is processed
    url(r'^resumable_uploads/', views.upload_file, name='upload_file'),
]
