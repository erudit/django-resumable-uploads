# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resumable_uploads', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resumablefile',
            name='filesize',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='resumablefile',
            name='uploadsize',
            field=models.IntegerField(null=True),
        ),
    ]
