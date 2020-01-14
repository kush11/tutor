"""Test of models for embargo app"""
import json
from django.test import TestCase
from django.db.utils import IntegrityError
from opaque_keys.edx.locator import CourseLocator
from ..models import (
    EmbargoedCourse, EmbargoedState, IPFilter, RestrictedCourse,
    Country, CountryAccessRule, CourseAccessRuleHistory
)

from openedx.core.djangolib.testing.utils import CacheIsolationTestCase


class EmbargoModelsTest(CacheIsolationTestCase):
    """Test each of the 3 models in embargo.models"""

    ENABLED_CACHES = ['default']

    def test_course_embargo(self):
        course_id = CourseLocator('abc', '123', 'doremi')
        # Test that course is not authorized by default
        self.assertFalse(EmbargoedCourse.is_embargoed(course_id))

        # Authorize
        cauth = EmbargoedCourse(course_id=course_id, embargoed=True)
        cauth.save()

        # Now, course should be embargoed
        self.assertTrue(EmbargoedCourse.is_embargoed(course_id))
        self.assertEquals(
            unicode(cauth),
            u"Course '{course_id}' is Embargoed".format(course_id=course_id)
        )

        # Unauthorize by explicitly setting email_enabled to False
        cauth.embargoed = False
        cauth.save()
        # Test that course is now unauthorized
        self.assertFalse(EmbargoedCourse.is_embargoed(course_id))
        self.assertEquals(
            unicode(cauth),
            u"Course '{course_id}' is Not Embargoed".format(course_id=course_id)
        )

    def test_state_embargo(self):
        # Azerbaijan and France should not be blocked
        good_states = ['AZ', 'FR']
        # Gah block USA and Antartica
        blocked_states = ['US', 'AQ']
        currently_blocked = EmbargoedState.current().embargoed_countries_list

        for state in blocked_states + good_states:
            self.assertNotIn(state, currently_blocked)

        # Block
        cauth = EmbargoedState(embargoed_countries='US, AQ')
        cauth.save()
        currently_blocked = EmbargoedState.current().embargoed_countries_list

        for state in good_states:
            self.assertNotIn(state, currently_blocked)
        for state in blocked_states:
            self.assertIn(state, currently_blocked)

        # Change embargo - block Isle of Man too
        blocked_states.append('IM')
        cauth.embargoed_countries = 'US, AQ, IM'
        cauth.save()
        currently_blocked = EmbargoedState.current().embargoed_countries_list

        for state in good_states:
            self.assertNotIn(state, currently_blocked)
        for state in blocked_states:
            self.assertIn(state, currently_blocked)

    def test_ip_blocking(self):
        whitelist = '127.0.0.1'
        blacklist = '18.244.51.3'

        cwhitelist = IPFilter.current().whitelist_ips
        self.assertNotIn(whitelist, cwhitelist)
        cblacklist = IPFilter.current().blacklist_ips
        self.assertNotIn(blacklist, cblacklist)

        IPFilter(whitelist=whitelist, blacklist=blacklist).save()

        cwhitelist = IPFilter.current().whitelist_ips
        self.assertIn(whitelist, cwhitelist)
        cblacklist = IPFilter.current().blacklist_ips
        self.assertIn(blacklist, cblacklist)

    def test_ip_network_blocking(self):
        whitelist = '1.0.0.0/24'
        blacklist = '1.1.0.0/16'

        IPFilter(whitelist=whitelist, blacklist=blacklist).save()

        cwhitelist = IPFilter.current().whitelist_ips
        self.assertIn('1.0.0.100', cwhitelist)
        self.assertIn('1.0.0.10', cwhitelist)
        self.assertNotIn('1.0.1.0', cwhitelist)
        cblacklist = IPFilter.current().blacklist_ips
        self.assertIn('1.1.0.0', cblacklist)
        self.assertIn('1.1.0.1', cblacklist)
        self.assertIn('1.1.1.0', cblacklist)
        self.assertNotIn('1.2.0.0', cblacklist)


class RestrictedCourseTest(CacheIsolationTestCase):
    """Test RestrictedCourse model. """

    ENABLED_CACHES = ['default']

    def test_unicode_values(self):
        course_id = CourseLocator('abc', '123', 'doremi')
        restricted_course = RestrictedCourse.objects.create(course_key=course_id)
        self.assertEquals(
            unicode(restricted_course),
            unicode(course_id)
        )

    def test_restricted_course_cache_with_save_delete(self):
        course_id = CourseLocator('abc', '123', 'doremi')
        RestrictedCourse.objects.create(course_key=course_id)

        # Warm the cache
        with self.assertNumQueries(1):
            RestrictedCourse.is_restricted_course(course_id)
            RestrictedCourse.is_disabled_access_check(course_id)

        # it should come from cache
        with self.assertNumQueries(0):
            RestrictedCourse.is_restricted_course(course_id)
            RestrictedCourse.is_disabled_access_check(course_id)

        self.assertFalse(RestrictedCourse.is_disabled_access_check(course_id))

        # add new the course so the cache must get delete and again hit the db
        new_course_id = CourseLocator('def', '123', 'doremi')
        RestrictedCourse.objects.create(course_key=new_course_id, disable_access_check=True)
        with self.assertNumQueries(1):
            RestrictedCourse.is_restricted_course(new_course_id)
            RestrictedCourse.is_disabled_access_check(new_course_id)

        # it should come from cache
        with self.assertNumQueries(0):
            RestrictedCourse.is_restricted_course(new_course_id)
            RestrictedCourse.is_disabled_access_check(new_course_id)

        self.assertTrue(RestrictedCourse.is_disabled_access_check(new_course_id))

        # deleting an object will delete cache also.and hit db on
        # get the is_restricted course
        abc = RestrictedCourse.objects.get(course_key=new_course_id)
        abc.delete()
        with self.assertNumQueries(1):
            RestrictedCourse.is_restricted_course(new_course_id)

        # it should come from cache
        with self.assertNumQueries(0):
            RestrictedCourse.is_restricted_course(new_course_id)


class CountryTest(TestCase):
    """Test Country model. """

    def test_unicode_values(self):
        country = Country.objects.create(country='NZ')
        self.assertEquals(unicode(country), "New Zealand (NZ)")


class CountryAccessRuleTest(CacheIsolationTestCase):
    """Test CountryAccessRule model. """
    ENABLED_CACHES = ['default']

    def test_unicode_values(self):
        course_id = CourseLocator('abc', '123', 'doremi')
        country = Country.objects.create(country='NZ')
        restricted_course1 = RestrictedCourse.objects.create(course_key=course_id)
        access_rule = CountryAccessRule.objects.create(
            restricted_course=restricted_course1,
            rule_type=CountryAccessRule.WHITELIST_RULE,
            country=country
        )

        self.assertEquals(
            unicode(access_rule),
            u"Whitelist New Zealand (NZ) for {course_key}".format(course_key=course_id)
        )

        course_id = CourseLocator('def', '123', 'doremi')
        restricted_course1 = RestrictedCourse.objects.create(course_key=course_id)
        access_rule = CountryAccessRule.objects.create(
            restricted_course=restricted_course1,
            rule_type=CountryAccessRule.BLACKLIST_RULE,
            country=country
        )

        self.assertEquals(
            unicode(access_rule),
            u"Blacklist New Zealand (NZ) for {course_key}".format(course_key=course_id)
        )

    def test_unique_together_constraint(self):
        """
         Course with specific country can be added either as whitelist or blacklist
         trying to add with both types will raise error
        """
        course_id = CourseLocator('abc', '123', 'doremi')
        country = Country.objects.create(country='NZ')
        restricted_course1 = RestrictedCourse.objects.create(course_key=course_id)

        CountryAccessRule.objects.create(
            restricted_course=restricted_course1,
            rule_type=CountryAccessRule.WHITELIST_RULE,
            country=country
        )

        with self.assertRaises(IntegrityError):
            CountryAccessRule.objects.create(
                restricted_course=restricted_course1,
                rule_type=CountryAccessRule.BLACKLIST_RULE,
                country=country
            )

    def test_country_access_list_cache_with_save_delete(self):
        course_id = CourseLocator('abc', '123', 'doremi')
        country = Country.objects.create(country='NZ')
        restricted_course1 = RestrictedCourse.objects.create(course_key=course_id)

        course = CountryAccessRule.objects.create(
            restricted_course=restricted_course1,
            rule_type=CountryAccessRule.WHITELIST_RULE,
            country=country
        )

        # Warm the cache
        with self.assertNumQueries(1):
            CountryAccessRule.check_country_access(course_id, 'NZ')

        with self.assertNumQueries(0):
            CountryAccessRule.check_country_access(course_id, 'NZ')

        # Deleting an object will invalidate the cache
        course.delete()
        with self.assertNumQueries(1):
            CountryAccessRule.check_country_access(course_id, 'NZ')


class CourseAccessRuleHistoryTest(TestCase):
    """Test course access rule history. """

    def setUp(self):
        super(CourseAccessRuleHistoryTest, self).setUp()
        self.course_key = CourseLocator('edx', 'DemoX', 'Demo_Course')
        self.restricted_course = RestrictedCourse.objects.create(course_key=self.course_key)
        self.countries = {
            'US': Country.objects.create(country='US'),
            'AU': Country.objects.create(country='AU')
        }

    def test_course_access_history_no_rules(self):
        self._assert_history([])
        self.restricted_course.delete()
        self._assert_history_deleted()

    def test_course_access_history_with_rules(self):
        # Add one rule
        us_rule = CountryAccessRule.objects.create(
            restricted_course=self.restricted_course,
            country=self.countries['US'],
            rule_type=CountryAccessRule.WHITELIST_RULE
        )
        self._assert_history([('US', 'whitelist')])

        # Add another rule
        au_rule = CountryAccessRule.objects.create(
            restricted_course=self.restricted_course,
            country=self.countries['AU'],
            rule_type=CountryAccessRule.BLACKLIST_RULE
        )
        self._assert_history([
            ('US', 'whitelist'),
            ('AU', 'blacklist')
        ])

        # Delete the first rule
        us_rule.delete()
        self._assert_history([('AU', 'blacklist')])

        # Delete the second rule
        au_rule.delete()
        self._assert_history([])

    def test_course_access_history_delete_all(self):
        # Create a rule
        CountryAccessRule.objects.create(
            restricted_course=self.restricted_course,
            country=self.countries['US'],
            rule_type=CountryAccessRule.WHITELIST_RULE
        )

        # Delete the course (and, implicitly, all the rules)
        self.restricted_course.delete()
        self._assert_history_deleted()

    def test_course_access_history_change_message(self):
        # Change the message key
        self.restricted_course.enroll_msg_key = 'embargo'
        self.restricted_course.access_msg_key = 'embargo'
        self.restricted_course.save()

        # Expect a history entry with the changed keys
        self._assert_history([], enroll_msg='embargo', access_msg='embargo')

    def _assert_history(self, country_rules, enroll_msg='default', access_msg='default'):
        """Check the latest history entry.

        Arguments:
            country_rules (list): List of rules, each of which are tuples
                of the form `(country_code, rule_type)`.

        Keyword Arguments:
            enroll_msg (str): The expected enrollment message key.
            access_msg (str): The expected access message key.

        Raises:
            AssertionError

        """
        record = CourseAccessRuleHistory.objects.latest()

        # Check that the record is for the correct course
        self.assertEqual(record.course_key, self.course_key)

        # Load the history entry and verify the message keys
        snapshot = json.loads(record.snapshot)
        self.assertEqual(snapshot['enroll_msg'], enroll_msg)
        self.assertEqual(snapshot['access_msg'], access_msg)

        # For each rule, check that there is an entry
        # in the history record.
        for (country, rule_type) in country_rules:
            self.assertIn(
                {
                    'country': country,
                    'rule_type': rule_type
                },
                snapshot['country_rules']
            )

        # Check that there are no duplicate entries
        self.assertEqual(len(snapshot['country_rules']), len(country_rules))

    def _assert_history_deleted(self):
        """Check the latest history entry for a 'DELETED' placeholder.

        Raises:
            AssertionError

        """
        record = CourseAccessRuleHistory.objects.latest()
        self.assertEqual(record.course_key, self.course_key)
        self.assertEqual(record.snapshot, "DELETED")
