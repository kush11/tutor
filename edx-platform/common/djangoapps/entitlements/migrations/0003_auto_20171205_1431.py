# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('entitlements', '0002_auto_20171102_0719'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseEntitlementPolicy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('expiration_period', models.DurationField(default=datetime.timedelta(450), help_text=b'Duration in days from when an entitlement is created until when it is expired.')),
                ('refund_period', models.DurationField(default=datetime.timedelta(60), help_text=b'Duration in days from when an entitlement is created until when it is no longer refundable')),
                ('regain_period', models.DurationField(default=datetime.timedelta(14), help_text=b'Duration in days from when an entitlement is redeemed for a course run until it is no longer able to be regained by a user.')),
                ('site', models.ForeignKey(to='sites.Site', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AlterField(
            model_name='courseentitlement',
            name='enrollment_course_run',
            field=models.ForeignKey(blank=True, to='student.CourseEnrollment', help_text=b'The current Course enrollment for this entitlement. If NULL the Learner has not enrolled.', null=True, on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='courseentitlement',
            name='expired_at',
            field=models.DateTimeField(help_text=b'The date that an entitlement expired, if NULL the entitlement has not expired.', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='courseentitlement',
            name='_policy',
            field=models.ForeignKey(blank=True, to='entitlements.CourseEntitlementPolicy', null=True, on_delete=models.CASCADE),
        ),
    ]
