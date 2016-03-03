from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns(
    '',

    # the url where the upload petition is processed
    url(r'^plupload/resumable-file/(?P<pk>[\d-]+)/delete/$', views.ResumableFileDeleteView.as_view(),
        name='resumable_file_delete'),

    # the url where the upload petition is processed
    url(r'^plupload/set_file_info', 'plupload.views.set_file_info',
        name='set_file_info'),

    # the url where the upload petition is processed
    url(r'^plupload/', 'plupload.views.upload_file',
        name='upload_file'),
)
