# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plupload', '0002_auto_20151217_1414'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resumablefile',
            name='filesize',
            field=models.DecimalField(max_digits=20, decimal_places=0, null=True),
        ),
        migrations.AlterField(
            model_name='resumablefile',
            name='uploadsize',
            field=models.DecimalField(max_digits=20, decimal_places=0, null=True),
        ),
    ]
