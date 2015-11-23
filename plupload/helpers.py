import os

from django.conf import settings
from django.shortcuts import get_object_or_404

from plupload.models import ResumableFile


def get_resumable_file_by_identifiers_or_404(model, pk, filename):

    resumable_file = get_object_or_404(
        ResumableFile,
        path=path_for_upload(
            model, pk, filename
        )
    )

    return resumable_file


def path_for_namespace(model_name, model_pk):
    """ Return the absolute path of a namespace """

    if not hasattr(settings, 'UPLOAD_ROOT'):
        raise AttributeError(
            'You must define UPLOAD_ROOT in your settings'
        )

    upload_root = settings.UPLOAD_ROOT

    directory_name = "{}/{}/{}".format(
        upload_root,
        model_name,
        model_pk
    )

    return directory_name


def path_for_upload(model_name, model_pk, filename):
    return "{}/{}".format(
        path_for_namespace(
            model_name,
            model_pk
        ),
        filename
    )


def namespace_exists(model_name, model_pk):
    """ Test that a namespace exists """
    return os.path.exists(
        path_for_namespace(model_name, model_pk)
    )


def create_namespace(model_name, model_pk):
    if not namespace_exists(model_name, model_pk):
        os.makedirs(
            path_for_namespace(model_name, model_pk)
        )


def upload_exists(model_name, model_pk, filename):
    """ Test that a upload exists for this namespace

    A namespace is made of a model/pk combination"""

    if not namespace_exists(model_name, model_pk):
        return False

    return os.path.exists(
        path_for_upload(model_name, model_pk, filename)
    )
