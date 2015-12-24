from django.db import models


class MyTestModel(models.Model):
    my_field = models.ManyToManyField(
        'plupload.ResumableFile'
    )
