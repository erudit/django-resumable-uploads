import os

from django.conf import settings
from django.forms.fields import FilePathField

from resumable_uploads.widgets import PlUploadWidget


class PlUploadFormField(FilePathField):

    widget = PlUploadWidget

    def __init__(self, required=True, widget=widget, options=None, label=None,
                 initial=None, help_text=None, *args, **kwargs):

        if options is None:
            options = dict()

        options.setdefault('max_file_size', '100mb')
        options.setdefault('chunk_size', '1mb')
        options.setdefault('browse_button', 'pickfiles')
        options.setdefault('container', 'upload-container')
        # TODO: Customize runtimes
        options.setdefault('runtimes', 'html5,gears,silverlight')
        options.setdefault('max_retries', 5)

        widget = widget(
            widget_options=options
        )

        super().__init__(
            required=required,
            widget=widget,
            label=label,
            initial=initial,
            help_text=help_text,
            *args,
            **kwargs)

    def validate(self, value):
        return os.path.isfile(
            "{}/{}".format(
                settings.UPLOAD_ROOT,
                value
            )
        )
