import os

from django.db import models
import humanfriendly


class HasResumableFilesMixin():

    def get_files(self):
        pass


class ResumableFileStatus():

    NEW = 'n'
    ERROR = 'e'


class ResumableFile(models.Model):

    path = models.CharField(
        max_length=200
    )

    filesize = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True
    )
    """ File size in bytes """

    uploadsize = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True
    )
    """ Total uploaded in bytes """

    status = models.CharField(
        max_length=1
    )

    def get_filename(self):
        return self.path.replace(os.path.dirname(self.path) + "/", "")

    def get_filesize_display(self):
        if self.filesize:
            return humanfriendly.format_size(self.filesize)

    def get_percent(self):
        return int(self.uploadsize / self.filesize * 100) if\
            self.uploadsize and self.filesize else 0

    @property
    def is_complete(self):
        return int(self.get_percent()) == 100
