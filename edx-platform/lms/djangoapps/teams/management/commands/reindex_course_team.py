"""
Management command to update course_teams' search index.
"""
from __future__ import print_function, unicode_literals

from textwrap import dedent

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError
from lms.djangoapps.teams.models import CourseTeam


class Command(BaseCommand):
    """
    Reindex course_teams (single, multiple or all available).
    """
    help = dedent(__doc__)

    def add_arguments(self, parser):
        # Mutually exclusive groups do not work here because nargs=* arguments
        # are "required", but required args are not allowed to be part of a
        # mutually exclusive group.
        parser.add_argument('--all',
                            action='store_true',
                            help='reindex all course teams (do not specify any course teams)')
        parser.add_argument('course_team_ids',
                            nargs='*',
                            metavar='course_team_id',
                            help='a specific course team to reindex')

    def _get_course_team(self, team_id):
        """
        Returns course_team object from team_id.
        """
        try:
            result = CourseTeam.objects.get(team_id=team_id)
        except ObjectDoesNotExist:
            raise CommandError('Argument {} is not a course_team team_id'.format(team_id))

        return result

    def handle(self, *args, **options):
        """
        By convention set by django developers, this method actually executes command's actions.
        So, there could be no better docstring than emphasize this once again.
        """
        # This is ugly, but there is a really strange circular dependency that doesn't
        # happen anywhere else that I can't figure out how to avoid it :(
        from ...search_indexes import CourseTeamIndexer

        if options['all']:
            if len(options['course_team_ids']) > 0:
                raise CommandError('Course teams cannot be specified when --all is also specified')
        else:
            if len(options['course_team_ids']) == 0:
                raise CommandError('At least one course_team_id or --all needs to be specified')

        if not settings.FEATURES.get('ENABLE_TEAMS', False):
            raise CommandError('ENABLE_TEAMS must be enabled to use course team indexing')

        if options['all']:
            course_teams = CourseTeam.objects.all()
        else:
            course_teams = map(self._get_course_team, options['course_team_ids'])

        for course_team in course_teams:
            print('Indexing {}'.format(course_team.team_id))
            CourseTeamIndexer.index(course_team)
