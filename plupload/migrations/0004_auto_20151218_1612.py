# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


def is_test_db():
    return 'memorydb' in settings.DATABASES.get(
        'default', {}).get('NAME', '')


class Migration(migrations.Migration):

    dependencies = [
        ('plupload', '0003_auto_20151217_1519'),
    ]

    if is_test_db():
        operations = [
            migrations.CreateModel(
                name='MyTestModel',
                fields=[
                    ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)
                    ),
                    ('my_field', models.ManyToManyField(
                        to='plupload.ResumableFile'
                    ))
                ],
            )
        ]
