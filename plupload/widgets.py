import json
from os import path

from django.forms.widgets import Input
from django.utils.safestring import mark_safe
from django.template.loader import get_template
from django.conf import settings
from django.template.context_processors import csrf
from django.forms.utils import flatatt
from django.core.urlresolvers import reverse

from plupload.models import ResumableFile


class PlUploadWidget(Input):

    needs_multipart_form = True
    input_type = 'text'

    def __init__(self, attrs=None, widget_options=None):
        self.widget_options = widget_options

        if widget_options is None:
            self.widget_options = {}

        return super().__init__(
            attrs=attrs
        )

    def set_model_reference(self, model_name, model_id):
        self.widget_options['model_name'] = model_name
        self.widget_options['model_id'] = model_id

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)

        template = get_template(
            "plupload_widget.html"
        )

        resumable_files = ResumableFile.objects.filter(
            pk__in=value
        )

        resumable_file_values = [
            {
                'status': rf.status,
                'filename': rf.get_filename(),
                'percent': rf.get_percent()
            }
            for rf in resumable_files
        ]

        upload_rel_path = path.relpath(
            settings.UPLOAD_ROOT,
            settings.MEDIA_ROOT
        )

        self.widget_options.update({
            'STATIC_URL': settings.STATIC_URL,
            'id': final_attrs['id'],
            'url': reverse('plupload:upload_file'),
            'path': upload_rel_path
        })

        options = {
            'STATIC_URL': settings.STATIC_URL,
            'id': final_attrs['id'],
            'csrf_token': csrf(name),
            'final_attrs': flatatt(final_attrs),
            'json_params': mark_safe(json.dumps(self.widget_options)),
            'files': resumable_file_values,
        }

        return mark_safe(
            template.render(
                options,
            )
        )
