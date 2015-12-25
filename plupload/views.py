import os
import datetime
import json

from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response

from plupload.helpers import (
    namespace_exists, create_namespace, path_for_upload,
    get_resumable_file_by_identifiers_or_404, get_or_create_resumable_file
)

from plupload.models import ResumableFile, ResumableFileStatus


def get_upload_identifiers_or_404(request):
    """ Test that the upload identifiers are present in POST

    Raise Http404 if model, pk or filename is missing.
    """
    request_keys = request.POST.keys()

    verified_keys = [
        key in request_keys
        for key in ('model', 'pk', 'name')
    ]

    if not all(verified_keys):
        raise Http404

    return (
        request.POST['model'],
        request.POST['pk'],
        request.POST['name']
    )


def set_file_info(request):

    model_name, model_pk, filename = get_upload_identifiers_or_404(request)

    if not namespace_exists(model_name, model_pk):
        create_namespace(model_name, model_pk)

    resumable_file = get_or_create_resumable_file(model_name, model_pk, filename)

    resumable_file.filesize = int(request.POST['filesize'])
    resumable_file.save()
    return HttpResponse()


def upload_file(request):

    model_name, model_pk, filename = get_upload_identifiers_or_404(request)

    if not namespace_exists(model_name, model_pk):
        create_namespace(model_name, model_pk)

    resumable_file = get_or_create_resumable_file(model_name, model_pk, filename)

    if request.method == 'POST' and request.FILES:
        # TODO: handle multiple files

        for _file in request.FILES:
            handle_uploaded_file(
                request.FILES[_file],
                request.POST.get('chunk', 0),
                resumable_file,
            )
        # response only to notify plUpload that the upload was successful
        return HttpResponse()
    else:
        return HttpResponseBadRequest


def handle_uploaded_file(f, chunk, resumable_file):
    """
    Here you can do whatever you like with your files, like resize them if they
    are images
    :param f: the file
    :param chunk: number of chunk to save
    """

    if int(chunk) > 0:
        # opens for append
        _file = open(resumable_file.path, 'ab')
    else:
        # erases content
        _file = open(resumable_file.path, 'wb')

    if f.multiple_chunks:
        for chunk in f.chunks():
            _file.write(chunk)
    else:
        _file.write(f.read())
    resumable_file.uploadsize = _file.tell()
    resumable_file.save()

def upload_error(request):
    identifiers = get_upload_identifiers_or_404(request)
    resumable_file = get_resumable_file_by_identifiers_or_404(*identifiers)
    resumable_file.status = ResumableFileStatus.ERROR
    resumable_file.save()
    return HttpResponse()
