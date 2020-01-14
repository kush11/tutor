"""
Transfer Student Management Command
"""
from __future__ import print_function, unicode_literals

from textwrap import dedent

from six import text_type

from django.contrib.auth.models import User
from django.db import transaction
from opaque_keys.edx.keys import CourseKey
from shoppingcart.models import CertificateItem
from student.models import CourseEnrollment
from track.management.tracked_command import TrackedCommand


class TransferStudentError(Exception):
    """
    Generic Error when handling student transfers.
    """
    pass


class Command(TrackedCommand):
    """
    Transfer students enrolled in one course into one or more other courses.

    This will remove them from the first course.  Their enrollment mode (i.e.
    honor, verified, audit, etc.) will persist into the other course(s).
    """
    help = dedent(__doc__)

    def add_arguments(self, parser):
        parser.add_argument('-f', '--from',
                            metavar='SOURCE_COURSE',
                            dest='source_course',
                            required=True,
                            help='the course to transfer students from')
        parser.add_argument('-t', '--to',
                            nargs='+',
                            metavar='DEST_COURSE',
                            dest='dest_course_list',
                            required=True,
                            help='the new course(s) to enroll the student into')
        parser.add_argument('-c', '--transfer-certificates',
                            action='store_true',
                            help='try to transfer certificate items to the new course')

    @transaction.atomic
    def handle(self, *args, **options):
        source_key = CourseKey.from_string(options['source_course'])
        dest_keys = []
        for course_key in options['dest_course_list']:
            dest_keys.append(CourseKey.from_string(course_key))

        if options['transfer_certificates'] and len(dest_keys) > 1:
            raise TransferStudentError('Cannot transfer certificate items from one course to many.')

        source_students = User.objects.filter(
            courseenrollment__course_id=source_key
        )

        for user in source_students:
            with transaction.atomic():
                print('Moving {}.'.format(user.username))
                # Find the old enrollment.
                enrollment = CourseEnrollment.objects.get(
                    user=user,
                    course_id=source_key
                )

                # Move the Student between the classes.
                mode = enrollment.mode
                old_is_active = enrollment.is_active
                CourseEnrollment.unenroll(user, source_key, skip_refund=True)
                print('Unenrolled {} from {}'.format(user.username, text_type(source_key)))

                for dest_key in dest_keys:
                    if CourseEnrollment.is_enrolled(user, dest_key):
                        # Un Enroll from source course but don't mess
                        # with the enrollment in the destination course.
                        msg = 'Skipping {}, already enrolled in destination course {}'
                        print(msg.format(user.username, text_type(dest_key)))
                    else:
                        new_enrollment = CourseEnrollment.enroll(user, dest_key, mode=mode)

                        # Un-enroll from the new course if the user had un-enrolled
                        # form the old course.
                        if not old_is_active:
                            new_enrollment.update_enrollment(is_active=False, skip_refund=True)

                        if options['transfer_certificates']:
                            self._transfer_certificate_item(source_key, enrollment, user, dest_keys, new_enrollment)

    @staticmethod
    def _transfer_certificate_item(source_key, enrollment, user, dest_keys, new_enrollment):
        """
        Transfer the certificate item from one course to another.

        Do not use this generally, since certificate items are directly associated with a particular purchase.
        This should only be used when a single course to a new location. This cannot be used when transferring
        from one course to many.

        Args:
            source_key (str): The course key string representation for the original course.
            enrollment (CourseEnrollment): The original enrollment to move the certificate item from.
            user (User): The user to transfer the item for.
            dest_keys (list): A list of course key strings to transfer the item to.
            new_enrollment (CourseEnrollment): The new enrollment to associate the certificate item with.

        Returns:
            None

        """
        try:
            certificate_item = CertificateItem.objects.get(
                course_id=source_key,
                course_enrollment=enrollment
            )
        except CertificateItem.DoesNotExist:
            print('No certificate for {}'.format(user))
            return

        certificate_item.course_id = dest_keys[0]
        certificate_item.course_enrollment = new_enrollment
