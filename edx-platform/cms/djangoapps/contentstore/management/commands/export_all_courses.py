"""
Script for exporting all courseware from Mongo to a directory and listing the courses which failed to export
"""
from __future__ import print_function
from six import text_type

from django.core.management.base import BaseCommand

from xmodule.contentstore.django import contentstore
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.xml_exporter import export_course_to_xml


class Command(BaseCommand):
    """
    Export all courses from mongo to the specified data directory and list the courses which failed to export
    """
    help = 'Export all courses from mongo to the specified data directory and list the courses which failed to export'

    def add_arguments(self, parser):
        parser.add_argument('output_path')

    def handle(self, *args, **options):
        """
        Execute the command
        """
        courses, failed_export_courses = export_courses_to_output_path(options['output_path'])

        print("=" * 80)
        print("=" * 30 + "> Export summary")
        print("Total number of courses to export: {0}".format(len(courses)))
        print("Total number of courses which failed to export: {0}".format(len(failed_export_courses)))
        print("List of export failed courses ids:")
        print("\n".join(failed_export_courses))
        print("=" * 80)


def export_courses_to_output_path(output_path):
    """
    Export all courses to target directory and return the list of courses which failed to export
    """
    content_store = contentstore()
    module_store = modulestore()
    root_dir = output_path
    courses = module_store.get_courses()

    course_ids = [x.id for x in courses]
    failed_export_courses = []

    for course_id in course_ids:
        print("-" * 80)
        print("Exporting course id = {0} to {1}".format(course_id, output_path))
        try:
            course_dir = text_type(course_id).replace('/', '...')
            export_course_to_xml(module_store, content_store, course_id, root_dir, course_dir)
        except Exception as err:  # pylint: disable=broad-except
            failed_export_courses.append(text_type(course_id))
            print("=" * 30 + "> Oops, failed to export {0}".format(course_id))
            print("Error:")
            print(err)

    return courses, failed_export_courses
