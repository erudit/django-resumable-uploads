[![Build Status](https://secure.travis-ci.org/erudit/django-resumable-uploads.svg?branch=master)](https://secure.travis-ci.org/erudit/django-resumable-uploads.svg?branch=master)
[![Coverage](https://codecov.io/github/erudit/django-resumable-uploads/coverage.svg?branch=master)](https://codecov.io/github/erudit/django-resumable-uploads/coverage.svg?branch=master)

# django-resumable-uploads

`django-resumable-uploads` is a multi-file resumable upload app. It uses [plupload](http://www.plupload.com/) and [jQuery](http://www.jquery.com/) in the backend.

## Requirements

- Django 1.6+

## Getting started

1. Add 'plupload' to your INSTALLED_APPS

2. Register urls in your root urlconf urls.py adding string to your urlpatterns like so :
    ```python
    # The url where the upload form is located:
    url(r'^$', 'plupload.views.upload'),
    ```
3. Specify the directory in which you would like to save the uploaded files. For example:
    ```python
    UPLOAD_ROOT = '/opt/project/media/uploads/
    ```

4. Link your model to the `ResumableFile` model:

    ```python
    class MyModel(models.Model):

        file_uploads = models.ManyToManyField(
            'plupload.ResumableFile'
        )
    ```

5. For any model form in which you would like to enable resumable uploads, use the `PlUploadFormField`. All the values in the `options` dictionary will be passed to the PlUpload widget constructor:

    ```python
    class FileUploadForm(models.ModelForm):

        class Meta:
            model = MyModel

        file_uploads = PlUploadFormField(
            path='uploads',
            label=_("Fichier"),
            options={
                "max_file_size": '15000mb',
                "drop_element": 'drop_element',
                "container": 'drop_element',
                "browse_button": 'pickfiles'
            }
        )
    ```

For the full list of options that can be passed to PlUpload, please refer to:

http://www.plupload.com/docs/Options

## Roadmap

* Make PlUploadFormField fully customizable

## Running the tests

* We use [`tox`](https://tox.readthedocs.org) as a test runner. To run the tests, install tox on your system or in a virtual environment and run it in the root of the project:

    ```bash
    $ tox
    ```
## Contributing

* All contributions are welcome. Please make sure the tests pass before submitting a pull request.

For any question, suggestion or additional help, feel free to contact `dcormier` on Freenode.
