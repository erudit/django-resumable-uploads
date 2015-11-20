
import os
import django

TEST_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tests')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
UPLOAD_ROOT = '/tmp'
SECRET_KEY = 'fake key'
INSTALLED_APPS = [
    'plupload'
]
