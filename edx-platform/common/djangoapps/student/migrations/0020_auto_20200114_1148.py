# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2020-01-14 11:48
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('student', '0019_auto_20181221_0540'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRegistration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(db_index=True, max_length=255)),
                ('middleName', models.CharField(blank=True, max_length=255)),
                ('lastName', models.CharField(blank=True, max_length=255)),
                ('gender', models.CharField(max_length=10)),
                ('dateOfBirth', models.DateField()),
                ('contactNumber', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(9999999999)])),
                ('emailId', models.EmailField(max_length=254)),
                ('identyType', models.CharField(max_length=255)),
                ('identyNo', models.CharField(max_length=255)),
                ('percentage10', models.CharField(max_length=5)),
                ('percentage12', models.CharField(max_length=5)),
                ('qualification', models.CharField(max_length=100)),
                ('stream', models.CharField(max_length=100)),
                ('collageName', models.CharField(max_length=100)),
                ('yearOfPassing', models.IntegerField()),
                ('gradPercentage', models.CharField(max_length=100)),
                ('postGradPercentage', models.CharField(max_length=100)),
                ('drive', models.CharField(max_length=50)),
                ('informationSource', models.CharField(max_length=50)),
                ('backlogs', models.CharField(max_length=10)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='userregistration', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'auth_userregistration',
                'permissions': (('can_deactivate_users', 'Can deactivate, but NOT delete users'),),
            },
        ),
        migrations.AddField(
            model_name='userprofile',
            name='allow_assessment',
            field=models.BooleanField(default=0),
        ),
    ]
