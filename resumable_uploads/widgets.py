import json
from os import path

import simplejson

from django.forms.widgets import Input
from django.utils import six
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
            'js/moxie.js',
            'js/plupload.full.min.js',
            'js/plupload_widget.js',
        )
        css = {
            'all': ('css/plupload.css', )
        }

    def __init__(
            self, attrs=None, widget_options=None,
            template_name='plupload/plupload_widget.html'):
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

    def render(self, name, value, attrs=None):
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
            'files_json': mark_safe(simplejson.dumps(file_progress))
        }

        return mark_safe(
            template.render(
                options,
            )
        )
