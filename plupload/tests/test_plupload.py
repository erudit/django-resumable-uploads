from django.db import models
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.test import TestCase, RequestFactory
from django.http import Http404, HttpResponseBadRequest

import mock

from plupload.factories import ResumableFileFactory
from plupload.models import ResumableFile, ResumableFileStatus
from plupload.views import (
    upload_error, get_upload_identifiers_or_404, upload_file
)
from plupload.forms import PlUploadFormField

from plupload.helpers import (
    path_for_namespace, namespace_exists, create_namespace, path_for_upload,
    upload_exists
)


class MyTestModelManager(models.Manager):

    def get(self, **kwargs):
        fake_model = MyTestModel(
            **kwargs
        )

        fake_model.resumable_file = mock.MagicMock(
            spec=models.ManyToManyField
        )

        return fake_model


class MyTestModel(models.Model):

    objects = MyTestModelManager()

    def save(self):
        return True

class TestModel(TestCase):

    def test_can_sanitize_filename(self):
        resumable_file = ResumableFileFactory(path="test file ,.png")
        self.assertEqual(
            resumable_file.get_filename(sanitize=True),
            "test_file__.png"
        )


class TestUploadViews(TestCase):
    """ Test the upload cases """

    def setUp(self):

        # self.sample_model.save()

        self.factory = RequestFactory()

        self.sample_file = ResumableFileFactory(
            pk=2,
            path=path_for_upload(
                "IssueSubmission",
                "2",
                "test.png"
            ),
            status=ResumableFileStatus.NEW
        ).save()

    @mock.patch('django.apps.apps.get_model', lambda x, y: mock.MagicMock(spec=MyTestModel))
    def test_upload_file_raises_400_when_malformed(self):
        request = self.factory.post(
            '/plupload/',
            {'model': 'test.IssueSubmission', 'pk': 1, 'name': 'test.png'}
        )

        result = upload_file(request)

        self.assertEquals(
            result,
            HttpResponseBadRequest,
            "A request with no file should return an HttpBadRequest"
        )


    @mock.patch('plupload.models.ResumableFile.save', lambda self: True)
    @mock.patch('django.apps.apps.get_model', lambda x, y: MyTestModel)
    @mock.patch('plupload.views.os.remove', lambda self: True)
    def test_append_file(self):
        """ Test that chunks are appended to the file """

        request = self.factory.post(
            '/plupload/',
            {
                'model': 'test.IssueSubmission',
                'pk': 1,
                'name': 'test.png',
                "chunk": 0,
                "chunks": 1,
            }
        )

        request.FILES['file'] = mock.MagicMock(spec=UploadedFile)

        with mock.patch("builtins.open", mock.MagicMock()) as mock_file:
            upload_file(request)

        mock_file.assert_called_with(
            path_for_upload('test.IssueSubmission', '1', 'test.png.chunk0'),
            'rb'
        )
        mock_file.assert_any_call(
            path_for_upload('test.IssueSubmission', '1', 'test.png'),
            'wb'
        )

    @mock.patch('plupload.models.ResumableFile.save', lambda self: True)
    @mock.patch('django.apps.apps.get_model', lambda x, y: MyTestModel)
    @mock.patch('plupload.views.os.remove', lambda self: True)
    def test_create_file(self):
        """ Test that files are created when no chunk is sent """
        request = self.factory.post(
            '/plupload/',
            {
                'model': 'test.IssueSubmission',
                'pk': 1,
                'name': 'test.png',
                "chunk": 0,
                "chunks": 1,
            }
        )

        request.FILES['file'] = mock.MagicMock(spec=UploadedFile)

        with mock.patch("builtins.open", mock.MagicMock()) as mock_file:
            upload_file(request)

        mock_file.assert_called_with(
            path_for_upload('test.IssueSubmission', '1', 'test.png.chunk0'),
            'rb'
        )
        mock_file.assert_any_call(
            path_for_upload('test.IssueSubmission', '1', 'test.png'),
            'wb'
        )

    def test_get_upload_identifiers_or_404(self):
        request = self.factory.post(
            '/plupload/',
            {'model': 'test.IssueSubmission', 'pk': 1, 'name': 'test.png'}
        )

        name_pk_filename = get_upload_identifiers_or_404(request)

        # Assert that all the name, pk
        self.assertTrue(
            all(name_pk_filename)
        )

        request = self.factory.post(
            '/plupload/',
        )

        self.assertRaises(
            Http404,
            get_upload_identifiers_or_404, request
        )

    @mock.patch('django.apps.apps.get_model', lambda x, y: MyTestModel)
    def test_upload_start_new_files(self):
        """ Tests upload_start on new files """
        import os

        request = self.factory.post(
            '/plupload/',
            {'model': 'test.IssueSubmission', 'pk': 2, 'name': 'test.png'}
        )

        with mock.patch('os.makedirs', mock.MagicMock(spec=os.makedirs)):

            upload_file(request)

            resumable_file_count = ResumableFile.objects.filter(
                path=path_for_upload(
                    "test.IssueSubmission",
                    "2",
                    "test.png",
                ),
                status=ResumableFileStatus.NEW
            ).count()

            self.assertEquals(
                resumable_file_count,
                1,
                "A ResumableFile should have been created"
            )

    @mock.patch('django.apps.apps.get_model', lambda x, y: MyTestModel)
    def test_upload_error(self):
        """ Test that posting to upload_error update the model """
        import os

        request = self.factory.post(
            '/plupload/',
            {'model': 'test.IssueSubmission', 'pk': 1, 'name': 'test.png'}
        )

        with mock.patch('os.makedirs', mock.MagicMock(spec=os.makedirs)):
            upload_file(request)

        request = self.factory.post(
            'plupload/upload_error',
            {'model': 'test.IssueSubmission', 'pk': 1, 'name': 'test.png'}
        )

        response = upload_error(request)
        resumable_file_count = ResumableFile.objects.filter(
            path=path_for_upload(
                "test.IssueSubmission",
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


class TestHelpers(TestCase):

    def setUp(self):

        self.test_model_class = mock.MagicMock(spec=models.Model)
        self.factory = RequestFactory()
        settings.UPLOAD_ROOT = '/tmp'

    def test_directory_creation_no_upload_root(self):
        """ Test that AttributeError is raised when no UPLOAD_ROOT """
        from django.conf import settings
        del(settings.UPLOAD_ROOT)
        self.assertRaises(
            AttributeError,
            path_for_namespace,
            'test.IssueSubmission',
            '1',
        )

    def test_path_for_namespace(self):
        """ Test that the paths for the namespace are properly sets """
        self.assertEquals(
            path_for_namespace(
                'test.IssueSubmission',
                '1',
            ),
            '/tmp/test.IssueSubmission/1'
        )

    def test_path_for_upload(self):
        """ Test that the upload paths are set properly """
        self.assertEquals(
            path_for_upload(
                'test.IssueSubmission',
                '1',
                'david.png'
            ),
            '/tmp/test.IssueSubmission/1/david.png'
        )

    def test_upload_exists(self):
        """ Test that the uploads exist """

        with mock.patch('plupload.helpers.namespace_exists', lambda x, y: False):
            self.assertFalse(
                upload_exists('test.IssueSubmission', '1', 'test.png'),
                "The upload should not exists if the namespace does not exist"
            )

        with mock.patch('plupload.helpers.namespace_exists', lambda x, y: True):
            with mock.patch('os.path.exists', lambda x: True):
                self.assertTrue(
                    upload_exists('test.IssueSubmission', '1', 'test.png'),
                    "The upload should exist when the namespace and file exists"
                )


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
