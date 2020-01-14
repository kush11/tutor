"""
One-off script to sync all user information to the
discussion service (later info will be synced automatically)
"""

import lms.lib.comment_client as cc
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Management command for adding all users to the discussion service.
    """
    help = 'Sync all user ids, usernames, and emails to the discussion service.'

    def handle(self, *args, **options):
        for user in User.objects.all().iterator():
            cc_user = cc.User.from_django_user(user)
            cc_user.save()
