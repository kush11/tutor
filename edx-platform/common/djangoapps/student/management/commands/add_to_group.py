from __future__ import print_function

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('name_or_email',
                            help='Username or email address of the user to add or remove')
        parser.add_argument('group_name',
                            help='Name of the group to change')
        parser.add_argument('--list',
                            action='store_true',
                            help='List available groups')
        parser.add_argument('--create',
                            action='store_true',
                            help='Create the group if it does not exist')
        parser.add_argument('--remove',
                            action='store_true',
                            help='Remove the user from the group instead of adding it')

    help = 'Add a user to a group'

    def print_groups(self):
        print('Groups available:')
        for group in Group.objects.all().distinct():
            print('   {}'.format(group.name))

    def handle(self, *args, **options):
        if options['list']:
            self.print_groups()
            return

        name_or_email = options['name_or_email']
        group_name = options['group_name']

        if '@' in name_or_email:
            user = User.objects.get(email=name_or_email)
        else:
            user = User.objects.get(username=name_or_email)

        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            if options['create']:
                group = Group(name=group_name)
                group.save()
            else:
                raise CommandError('Group {} does not exist'.format(group_name))

        if options['remove']:
            user.groups.remove(group)
        else:
            user.groups.add(group)

        print('Success!')
