"""
Tests for django admin commands in the verify_student module

"""
import logging
import os
import tempfile

from django.core.management import call_command, CommandError
from django.test import TestCase
from lms.djangoapps.verify_student.models import ManualVerification
from lms.djangoapps.verify_student.utils import earliest_allowed_verification_date
from student.tests.factories import UserFactory
from testfixtures import LogCapture

LOGGER_NAME = 'lms.djangoapps.verify_student.management.commands.manual_verifications'


class TestVerifyStudentCommand(TestCase):
    """
    Tests for django admin commands in the verify_student module
    """
    tmp_file_path = os.path.join(tempfile.gettempdir(), 'tmp-emails.txt')

    def setUp(self):
        super(TestVerifyStudentCommand, self).setUp()
        self.user1 = UserFactory.create()
        self.user2 = UserFactory.create()
        self.user3 = UserFactory.create()
        self.invalid_email = unicode('unknown@unknown.com')

        self.create_email_ids_file(
            self.tmp_file_path,
            [self.user1.email, self.user2.email, self.user3.email, self.invalid_email]
        )

    @staticmethod
    def create_email_ids_file(file_path, email_ids):
        """
        Write the email_ids list to the temp file.
        """
        with open(file_path, 'w') as temp_file:
            temp_file.write(str("\n".join(email_ids)))

    def test_manual_verifications(self):
        """
        Tests that the manual_verifications management command executes successfully
        """
        self.assertEquals(ManualVerification.objects.filter(status='approved').count(), 0)

        call_command('manual_verifications', '--email-ids-file', self.tmp_file_path)

        self.assertEquals(ManualVerification.objects.filter(status='approved').count(), 3)

    def test_manual_verifications_created_date(self):
        """
        Tests that the manual_verifications management command does not create a new verification
        if a previous non-expired verification exists
        """
        call_command('manual_verifications', '--email-ids-file', self.tmp_file_path)

        verification1 = ManualVerification.objects.filter(
            user=self.user1,
            status='approved',
            created_at__gte=earliest_allowed_verification_date()
        )

        call_command('manual_verifications', '--email-ids-file', self.tmp_file_path)

        verification2 = ManualVerification.objects.filter(
            user=self.user1,
            status='approved',
            created_at__gte=earliest_allowed_verification_date()
        )

        self.assertQuerysetEqual(verification1, [repr(r) for r in verification2])

    def test_user_doesnot_exist_log(self):
        """
        Tests that the manual_verifications management command logs an error when an invalid email is
        provided as input
        """
        expected_log = (
            (LOGGER_NAME,
             'INFO',
             u'Creating manual verification for 4 emails.'
             ),
            (LOGGER_NAME,
             'ERROR',
             u'Tried to verify email unknown@unknown.com, but user not found'
             ),
            (LOGGER_NAME,
             'ERROR',
             u'Completed manual verification. 1 of 4 failed.'
             ),
            (LOGGER_NAME,
             'ERROR',
             "Failed emails:['unknown@unknown.com']"
             )
        )
        with LogCapture(LOGGER_NAME, level=logging.INFO) as logger:
            call_command('manual_verifications', '--email-ids-file', self.tmp_file_path)

            logger.check(
                *expected_log
            )

    def test_invalid_file_path(self):
        """
        Verify command raises the CommandError for invalid file path.
        """
        with self.assertRaises(CommandError):
            call_command('manual_verifications', '--email-ids-file', u'invalid/email_id/file/path')
