""" Tests for API endpoints. """
from __future__ import unicode_literals

import datetime
import freezegun
import json

from django.conf import settings
from django.urls import reverse
from django.test import TestCase
from django.test.utils import override_settings

from lms.djangoapps.verify_student.models import SoftwareSecurePhotoVerification
from student.tests.factories import UserFactory

FROZEN_TIME = '2015-01-01'
VERIFY_STUDENT = {'DAYS_GOOD_FOR': 365}


@override_settings(VERIFY_STUDENT=VERIFY_STUDENT)
class PhotoVerificationStatusViewTests(TestCase):
    """ Tests for the PhotoVerificationStatusView endpoint. """
    CREATED_AT = datetime.datetime.strptime(FROZEN_TIME, '%Y-%m-%d')
    PASSWORD = 'test'

    def setUp(self):
        freezer = freezegun.freeze_time(FROZEN_TIME)
        freezer.start()
        self.addCleanup(freezer.stop)

        super(PhotoVerificationStatusViewTests, self).setUp()
        self.user = UserFactory(password=self.PASSWORD)
        self.staff = UserFactory(is_staff=True, password=self.PASSWORD)
        self.verification = SoftwareSecurePhotoVerification.objects.create(user=self.user, status='submitted')
        self.path = reverse('verification_status', kwargs={'username': self.user.username})
        self.client.login(username=self.staff.username, password=self.PASSWORD)

    def assert_path_not_found(self, path):
        """ Assert the path returns HTTP 404. """
        response = self.client.get(path)
        self.assertEqual(response.status_code, 404)

    def assert_verification_returned(self, verified=False):
        """ Assert the path returns HTTP 200 and returns appropriately-serialized data. """
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        expected_expires = self.CREATED_AT + datetime.timedelta(settings.VERIFY_STUDENT['DAYS_GOOD_FOR'])

        expected = {
            'status': self.verification.status,
            'expiration_datetime': '{}Z'.format(expected_expires.isoformat()),
            'is_verified': verified
        }
        self.assertEqual(json.loads(response.content), expected)

    def test_non_existent_user(self):
        """ The endpoint should return HTTP 404 if the user does not exist. """
        path = reverse('verification_status', kwargs={'username': 'abc123'})
        self.assert_path_not_found(path)

    def test_no_verifications(self):
        """ The endpoint should return HTTP 404 if the user has no verifications. """
        user = UserFactory()
        path = reverse('verification_status', kwargs={'username': user.username})
        self.assert_path_not_found(path)

    def test_authentication_required(self):
        """ The endpoint should return HTTP 403 if the user is not authenticated. """
        self.client.logout()
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_staff_user(self):
        """ The endpoint should be accessible to staff users. """
        self.client.logout()
        self.client.login(username=self.staff.username, password=self.PASSWORD)
        self.assert_verification_returned()

    def test_owner(self):
        """ The endpoint should be accessible to the user who submitted the verification request. """
        self.client.logout()
        self.client.login(username=self.user.username, password=self.PASSWORD)
        self.assert_verification_returned()

    def test_non_owner_or_staff_user(self):
        """ The endpoint should NOT be accessible if the request is not made by the submitter or staff user. """
        user = UserFactory()
        self.client.login(username=user.username, password=self.PASSWORD)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 403)

    def test_approved_verification(self):
        """ The endpoint should return that the user is verified if the user's verification is accepted. """
        self.verification.status = 'approved'
        self.verification.save()
        self.client.logout()
        self.client.login(username=self.user.username, password=self.PASSWORD)
        self.assert_verification_returned(verified=True)
