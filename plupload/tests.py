from django.db import models
from django.conf import settings
from django.test import TestCase, RequestFactory
from django.http import Http404, HttpResponseBadRequest

import mock

from plupload.models import ResumableFile, ResumableFileStatus
from plupload.views import (
    upload_start, upload_error, get_upload_identifiers_or_404, upload_file
)
from plupload.forms import PlUploadFormField
from plupload.fields import ResumableFileField
from plupload.helpers import (
    path_for_namespace, namespace_exists, create_namespace, path_for_upload,
    upload_exists
)


class TestUploadViews(TestCase):
    """ Test the upload cases """

    def setUp(self):
        self.factory = RequestFactory()

        self.sample_file =  ResumableFile(
            pk=2,
            path=path_for_upload(
                "IssueSubmission",
                "2",
                "test.png"
            ),
            status=ResumableFileStatus.NEW
        ).save()

    def test_upload_file_raises_400_when_malformed(self):
        request = self.factory.post(
            'plupload/upload_start',
            {'model': 'IssueSubmission', 'pk': 2, 'filename': 'test.png'}
        )

        result = upload_file(request)

        self.assertEquals(
            result,
            HttpResponseBadRequest,
            "A request with no file should return an HttpBadRequest"
        )


    def test_get_upload_identifiers_or_404(self):
        request = self.factory.post(
            'plupload/upload_start',
            {'model': 'IssueSubmission', 'pk': 1, 'filename': 'test.png'}
        )

        name_pk_filename = get_upload_identifiers_or_404(request)

        # Assert that all the name, pk
        self.assertTrue(
            all(name_pk_filename)
        )

        request = self.factory.post(
            'plupload/upload_start',
        )

        self.assertRaises(
            Http404,
            get_upload_identifiers_or_404, request
        )

    def test_upload_start_new_files(self):
        """ Tests upload_start on new files """
        import os

        request = self.factory.post(
            'plupload/upload_start',
            {'model': 'IssueSubmission', 'pk': 1, 'filename': 'test.png'}
        )

        with mock.patch('os.makedirs', mock.MagicMock(spec=os.makedirs)):

            upload_start(request)

            resumable_file_count = ResumableFile.objects.filter(
                path=path_for_upload(
                    "IssueSubmission",
                    "1",
                    "test.png",
                ),
                status=ResumableFileStatus.NEW
            ).count()

            self.assertEquals(
                resumable_file_count,
                1,
                "A ResumableFile should have been created"
            )

    def test_upload_error(self):
        """ Test that posting to upload_error update the model """
        import os

        request = self.factory.post(
            'plupload/upload_start',
            {'model': 'IssueSubmission', 'pk': 1, 'filename': 'test.png'}
        )

        with mock.patch('os.makedirs', mock.MagicMock(spec=os.makedirs)):
            upload_start(request)

        request = self.factory.post(
            'plupload/upload_error',
            {'model': 'IssueSubmission', 'pk': 1, 'filename': 'test.png'}
        )

        response = upload_error(request)
        resumable_file_count = ResumableFile.objects.filter(
            path=path_for_upload(
                "IssueSubmission",
                "1",
                "test.png",
            ),
            status=ResumableFileStatus.ERROR
        ).count()

        self.assertEquals(
            resumable_file_count,
            1,
            "The ResumableFile should have failed"
        )


class TestResumableFileField(TestCase):

    def setUp(self):
        class MyTestModel(models.Model):
            my_field = ResumableFileField(upload_to='test_files')

        self.test_model_class = MyTestModel
        self.factory = RequestFactory()
        settings.UPLOAD_ROOT = '/tmp'

    def test_directory_creation_no_upload_root(self):
        """ Test that AttributeError is raised when no UPLOAD_ROOT """
        from django.conf import settings
        del(settings.UPLOAD_ROOT)
        self.assertRaises(
            AttributeError,
            self.test_model_class().save
        )

    def test_path_for_namespace(self):
        """ Test that the paths for the namespace are properly sets """
        self.assertEquals(
            path_for_namespace(
                'IssueSubmission',
                '1',
            ),
            '/tmp/IssueSubmission/1'
        )

    def test_path_for_upload(self):
        """ Test that the upload paths are set properly """
        self.assertEquals(
            path_for_upload(
                'IssueSubmission',
                '1',
                'david.png'
            ),
            '/tmp/IssueSubmission/1/david.png'
        )

    def test_upload_exists(self):
        """ Test that the uploads exist """

        with mock.patch('plupload.helpers.namespace_exists', lambda x, y: False):
            self.assertFalse(
                upload_exists('IssueSubmission', '1', 'test.png'),
                "The upload should not exists if the namespace does not exist"
            )

        with mock.patch('plupload.helpers.namespace_exists', lambda x, y: True):
            with mock.patch('os.path.exists', lambda x: True):
                self.assertTrue(
                    upload_exists('IssueSubmission', '1', 'test.png'),
                    "The upload should exist when the namespace and file exists"
                )

    def test_directory_creation(self):
        """ Test that the directory is created when the field is saved """
        # Mock makedirs, we do not want to actually create the directory
        import os
        os.makedirs = mock.Mock()

        my_test_model = self.test_model_class()

        # Do not save this model to the database
        my_test_model._do_update = mock.Mock()
        my_test_model._do_insert = mock.Mock()

        my_test_model.save()

        # since the database is mocked, we manually give the model a pk
        my_test_model.pk = 1

        # pre_save is not called on creation
        # so we need to update

        """ my_test_model.save()
        self.assertEquals(
            os.makedirs.call_count,
            1,
            "os.makedirs should have been called"
        )

        self.assertEquals(
            os.makedirs.call_args,
            mock.call(
                "{}/MyTestModel/my_field/1".format(
                    settings.UPLOAD_ROOT
                )
            )
        )"""


class TestPluploadWidgetOptions(TestCase):
    """ Make sure Plupload options are handled correctly

    PlUpload options are defined here:

      http://www.plupload.com/docs/Options
    """

    def test_all_params_are_passed_to_js_widget(self):
        """ Make sure that all the options given to the
        FormField are passed to the resulting javascript widget

        This does not test that the javascript widget is rendered
        correctly.
        """

        widget_options = {
            'browse_button': 'test_button',
            'url': 'upload_url',
            'filters': {
                'mime_types': [
                    {
                        'title': "Image files",
                        'extensions': "jpg,gif,png"},
                    {
                        'title': "Zip files",
                        'extensions': "zip"
                    }
                ],
                'max_file_size': 0,
                'prevent_duplicates': 'true',
            },
            'headers': {
                'my_header': 'my_value'
            },
            'multipart_params': {
                'one': 'two',
            },
            'max_retries': 0,
            'chunk_size': '1mb',
            'resize': {'width': '100px'},
            'drop_element': 'false',
            'multi_selection': 'false',
            'required_features': 'html5',
            'unique_names': 'false',
            'runtimes': 'html5',
            'file_data_name': "file",
            'container': 'container',
            'flash_swf_url': "js/Movie.swf",
            'silverlight_xap_url': 'js/Movie.xap',
        }

        form_field = PlUploadFormField(
            path='dummy_path',
            options=widget_options,
        )

        # Assert that all keys are passed to the widget
        for key in widget_options.keys():
            self.assertTrue(
                key in form_field.widget.widget_options.keys()
            )
