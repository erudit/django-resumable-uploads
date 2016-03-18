from decimal import Decimal
import os

from django.http import JsonResponse, HttpResponse, Http404, HttpResponseBadRequest
from django.views.generic import DeleteView

from plupload.helpers import (
    namespace_exists, create_namespace,
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

    resumable_file.filesize = Decimal(request.POST.get('filesize'))
    resumable_file.save()
    return JsonResponse({
        'id': resumable_file.id,
    })


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
                int(request.POST.get('chunk', 0)),
                int(request.POST.get('chunks')),
                resumable_file,
            )
        # response only to notify plUpload that the upload was successful
        return JsonResponse({
            'id': resumable_file.id,
        })
    else:
        return HttpResponseBadRequest


def handle_uploaded_file(f, chunk, chunks_count, resumable_file):
    """
    Here you can do whatever you like with your files, like resize them if they
    are images
    :param f: the file
    :param chunk: number of chunk to save
    """
    chunk_filepath = lambda c: '{path}.chunk{chunk}'.format(
        path=resumable_file.path, chunk=c)
    chunk_file = open(chunk_filepath(chunk), 'wb')

    if f.multiple_chunks:
        for chk in f.chunks():
            chunk_file.write(chk)
    else:
        chunk_file.write(f.read())

    # resumable_file.uploadsize = _file.tell()
    resumable_file.uploadsize = chunk_file.tell() * (chunk + 1)
    resumable_file.save()
    chunk_file.close()

    if not (chunk == (chunks_count - 1)):
        return

    # Writes the final file
    final_file = open(resumable_file.path, 'wb')
    for ichunk in range(chunks_count):
        with open(chunk_filepath(ichunk), 'rb') as fchunk:
            final_file.write(fchunk.read())

    resumable_file.uploadsize = final_file.tell()
    resumable_file.save()
    final_file.close()

    # Deletes the temporary "chunk" files
    for ichunk in range(chunks_count):
        os.remove(chunk_filepath(ichunk))


def upload_error(request):
    identifiers = get_upload_identifiers_or_404(request)
    resumable_file = get_resumable_file_by_identifiers_or_404(*identifiers)
    resumable_file.status = ResumableFileStatus.ERROR
    resumable_file.save()
    return HttpResponse()


class ResumableFileDeleteView(DeleteView):
    model = ResumableFile

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'id': self.kwargs['pk']})
