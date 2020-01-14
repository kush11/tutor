"""
Dump the course_ids available to the lms.

Output is UTF-8 encoded by default.
"""
from __future__ import unicode_literals

from textwrap import dedent

from six import text_type

from django.core.management.base import BaseCommand
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


class Command(BaseCommand):
    help = dedent(__doc__).strip()

    def add_arguments(self, parser):
        parser.add_argument('--modulestore',
                            default='default',
                            help='name of the modulestore to use')

    def handle(self, *args, **options):
        output = '\n'.join(text_type(course_overview.id) for course_overview in CourseOverview.get_all_courses()) + '\n'

        return output
