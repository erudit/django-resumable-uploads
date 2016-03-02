import os

from django.db.models import ManyToManyField
from django.apps import apps

from django.conf import settings
from django.shortcuts import get_object_or_404

from plupload.models import ResumableFile, ResumableFileStatus


def get_or_create_resumable_file(model, pk, filename):
    try:
        resumable_file = ResumableFile.objects.get(
            path=path_for_upload(model, pk, filename)
        )

        return resumable_file
    except ResumableFile.DoesNotExist:
        resumable_file = create_resumable_file(model, pk, filename)
        return resumable_file


def create_resumable_file(model, pk, filename):
    """ Initialise a ResumableFile

    Initialise the file, set its status to NEW, and link it
    to it's models m2m field. """
    resumable_file = ResumableFile(
        path=path_for_upload(model, pk, filename)
    )

    resumable_file.status = ResumableFileStatus.NEW
    resumable_file.save()
    add_to_model_m2m(resumable_file, model, pk)
    return resumable_file


def add_to_model_m2m(resumable_file, model, pk):
    """ Add the ResumableFile to the model's m2m """

    # Retrieve the Django model.
    Model = apps.get_model(*model.split('.', 1))

    # Retrieve the object

    object = Model.objects.get(pk=pk)

    for field in object._meta.get_fields():
        if isinstance(field, ManyToManyField):
            # check if the m2m accepts resumable files
            bound_field = getattr(object, field.name)
            if bound_field.model == ResumableFile:
                bound_field.add(resumable_file)
                object.save()


def get_resumable_file_by_identifiers_or_404(model, pk, filename):
    # TODO: Link to model should be tested explicitely.

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
