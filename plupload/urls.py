from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    # the url where the upload petition is processed
    url(r'^plupload/set_file_info', 'plupload.views.set_file_info',
        name='set_file_info'),

    # the url where the upload petition is processed
    url(r'^plupload/', 'plupload.views.upload_file',
        name='upload_file'),
)
