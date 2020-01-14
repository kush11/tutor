# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0014_courseoverview_certificate_available_date'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entitlements', '0004_auto_20171206_1729'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseEntitlementSupportDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('reason', models.CharField(max_length=15, choices=[(b'LEAVE', 'Learner requested leave session for expired entitlement'), (b'CHANGE', 'Learner requested session change for expired entitlement'), (b'LEARNER_NEW', 'Learner requested new entitlement'), (b'COURSE_TEAM_NEW', 'Course team requested entitlement for learnerg'), (b'OTHER', 'Other')])),
                ('comments', models.TextField(null=True)),
                ('entitlement', models.ForeignKey(to='entitlements.CourseEntitlement', on_delete=models.CASCADE)),
                ('support_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('unenrolled_run', models.ForeignKey(db_constraint=False, blank=True, to='course_overviews.CourseOverview', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
