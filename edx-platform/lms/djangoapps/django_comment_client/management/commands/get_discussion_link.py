from courseware.courses import get_course
from django.core.management.base import BaseCommand, CommandError
from opaque_keys.edx.keys import CourseKey


class Command(BaseCommand):
    help = 'Write a discussion link for a given course on standard output.'

    def add_arguments(self, parser):
        parser.add_argument('course_id',
                            help='course for which to write a discussion link')

    def handle(self, *args, **options):
        course_id = options['course_id']

        course_key = CourseKey.from_string(course_id)

        course = get_course(course_key)
        if not course:
            raise CommandError('Invalid course id: {}'.format(course_id))

        if course.discussion_link:
            self.stdout.write(course.discussion_link)
