# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ResumableFile',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('path', models.CharField(max_length=200)),
                ('filesize', models.IntegerField()),
                ('uploadsize', models.IntegerField()),
                ('status', models.CharField(max_length=1)),
            ],
        ),
    ]
