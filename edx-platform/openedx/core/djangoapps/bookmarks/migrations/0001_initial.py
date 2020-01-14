# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import model_utils.fields
import jsonfield.fields
import django.utils.timezone
from django.conf import settings
from opaque_keys.edx.django.models import CourseKeyField, UsageKeyField


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('course_key', CourseKeyField(max_length=255, db_index=True)),
                ('usage_key', UsageKeyField(max_length=255, db_index=True)),
                ('_path', jsonfield.fields.JSONField(help_text=b'Path in course tree to the block', db_column=b'path')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='XBlockCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('course_key', CourseKeyField(max_length=255, db_index=True)),
                ('usage_key', UsageKeyField(unique=True, max_length=255, db_index=True)),
                ('display_name', models.CharField(default=b'', max_length=255)),
                ('_paths', jsonfield.fields.JSONField(default=[], help_text=b'All paths in course tree to the corresponding block.', db_column=b'paths')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='bookmark',
            name='xblock_cache',
            field=models.ForeignKey(to='bookmarks.XBlockCache', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='bookmark',
            unique_together=set([('user', 'usage_key')]),
        ),
    ]
