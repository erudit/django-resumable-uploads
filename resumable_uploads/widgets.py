import json
from os import path

import simplejson
import six

from django.forms.widgets import Input
from django.forms.widgets import get_default_renderer
from django.utils.safestring import mark_safe
from django.template.loader import get_template
from django.conf import settings
from django.template.context_processors import csrf
from django.forms.utils import flatatt
from django.urls import reverse

from resumable_uploads.models import ResumableFile


class PlUploadWidget(Input):

    needs_multipart_form = True
    input_type = 'text'

    class Media:
        js = (
            'js/plupload/moxie.js',
            'js/plupload/plupload.full.min.js',
            'js/resumable_uploads.js',
        )
        css = {
            'all': (
                'css/fontawesome.css',
                'css/resumable_uploads.css',
            ),
        }

    def __init__(
            self, attrs=None, widget_options=None,
            template_name='resumable_uploads/resumable_uploads_widget.html'):
        self.widget_options = widget_options
        self.template_name = template_name

        if widget_options is None:
            self.widget_options = {}

        return super().__init__(
            attrs=attrs
        )

    def set_model_reference(self, model_name, model_id):
        self.widget_options['model_name'] = model_name
        self.widget_options['model_id'] = model_id

    def render(self, name, value, attrs=None, renderer=None):
        if renderer is None:
            renderer = get_default_renderer()
        final_attrs = self.build_attrs(
            attrs, extra_attrs={'type': self.input_type, 'name': name})

        template = get_template(self.template_name)

        fids = []
        if value and isinstance(value, six.string_types):
            fids = value.split(',')
        elif value and isinstance(value, list):
            fids = value
        else:
            fids = []
        resumable_files = ResumableFile.objects.filter(pk__in=fids) if fids else []

        final_attrs['value'] = ','.join(map(six.text_type, fids))

        resumable_file_values = [
            {
                'id': rf.id,
                'status': rf.status,
                'filename': rf.get_filename(),
                'filesize': rf.get_filesize_display(),
                'percent': rf.get_percent(),
                'offset': rf.uploadsize,
                'is_complete': rf.is_complete,
                'type': rf.get_filename().rsplit('.', 1).pop().lower(),
            }
            for rf in resumable_files
        ]

        file_progress = {
            rf.get_filename(): rf.uploadsize
            for rf in resumable_files
        }

        self.widget_options.update({
            'STATIC_URL': settings.STATIC_URL,
            'id': final_attrs['id'],
            'url': reverse('resumable_uploads:upload_file'),
        })

        options = {
            'STATIC_URL': settings.STATIC_URL,
            'id': final_attrs['id'],
            'csrf_token': csrf(name),
            'final_attrs': flatatt(final_attrs),
            'json_params': mark_safe(json.dumps(self.widget_options)),
            'files': resumable_file_values,
            'files_json': mark_safe(simplejson.dumps(file_progress)),
            'auto_upload': self.widget_options.get('auto_upload', False),
            'max_file_count': self.widget_options.get('max_file_count', 1),
        }

        return mark_safe(
            template.render(
                options,
            )
        )
