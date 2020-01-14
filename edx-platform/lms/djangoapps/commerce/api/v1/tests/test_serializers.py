""" Commerce API v1 serializer tests. """
from django.test import TestCase

from ..serializers import serializers, validate_course_id


class CourseValidatorTests(TestCase):
    """ Tests for Course Validator method. """
    shard = 4

    def test_validate_course_id_with_non_existent_course(self):
        """ Verify a validator checking non-existent courses."""
        course_key = 'non/existing/keyone'

        error_msg = u"Course {} does not exist.".format(course_key)
        with self.assertRaisesRegexp(serializers.ValidationError, error_msg):
            validate_course_id(course_key)

    def test_validate_course_id_with_invalid_key(self):
        """ Verify a validator checking invalid course keys."""
        course_key = 'invalidkey'

        error_msg = u"{} is not a valid course key.".format(course_key)
        with self.assertRaisesRegexp(serializers.ValidationError, error_msg):
            validate_course_id(course_key)
