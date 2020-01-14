"""
Test lti_provider management commands.
"""


from django.test import TestCase
from mock import patch
from opaque_keys.edx.keys import CourseKey, UsageKey

from lti_provider.management.commands import resend_lti_scores
from lti_provider.models import GradedAssignment, LtiConsumer, OutcomeService
from student.tests.factories import UserFactory
from xmodule.modulestore.tests.django_utils import SharedModuleStoreTestCase
from xmodule.modulestore.tests.utils import TEST_DATA_DIR
from xmodule.modulestore.xml_importer import import_course_from_xml


class CommandArgsTestCase(TestCase):
    """
    Test management command parses arguments properly.
    """
    shard = 4

    def _get_arg_parser(self):
        """
        Returns the argparse parser for the resend_lti_scores command.
        """
        cmd = resend_lti_scores.Command()
        return cmd.create_parser('./manage.py', 'resend_lti_scores')

    def test_course_keys(self):
        parser = self._get_arg_parser()
        args = parser.parse_args(['course-v1:edX+test_course+2525_fall', 'UBC/Law281/2015_T1'])
        self.assertEqual(len(args.course_keys), 2)
        key = args.course_keys[0]
        self.assertIsInstance(key, CourseKey)
        self.assertEqual(unicode(key), 'course-v1:edX+test_course+2525_fall')

    def test_no_course_keys(self):
        parser = self._get_arg_parser()
        args = parser.parse_args([])
        self.assertEqual(args.course_keys, [])


class CommandExecutionTestCase(SharedModuleStoreTestCase):
    """
    Test `manage.py resend_lti_scores` command.
    """
    shard = 4

    @classmethod
    def setUpClass(cls):
        super(CommandExecutionTestCase, cls).setUpClass()
        cls.course_key = cls.store.make_course_key(u'edX', u'lti_provider', u'3000')
        import_course_from_xml(
            cls.store,
            u'test_user',
            TEST_DATA_DIR,
            source_dirs=[u'simple'],
            static_content_store=None,
            target_id=cls.course_key,
            raise_on_failure=True,
            create_if_not_present=True,
        )
        cls.lti_block = u'block-v1:edX+lti_provider+3000+type@chapter+block@chapter_2'

    def setUp(self):
        super(CommandExecutionTestCase, self).setUp()
        self.user = UserFactory()
        self.user2 = UserFactory(username=u'anotheruser')
        self.client.login(username=self.user.username, password=u'test')

    def _configure_lti(self, usage_key):
        """
        Set up the lti provider configuration.
        """
        consumer = LtiConsumer.objects.create()
        outcome_service = OutcomeService.objects.create(
            lti_consumer=consumer,
            lis_outcome_service_url=u'https://lol.tools'
        )
        GradedAssignment.objects.create(
            user=self.user,
            course_key=self.course_key,
            usage_key=usage_key,
            outcome_service=outcome_service,
            lis_result_sourcedid=u'abc',
        )
        GradedAssignment.objects.create(
            user=self.user2,
            course_key=self.course_key,
            usage_key=usage_key,
            outcome_service=outcome_service,
            lis_result_sourcedid=u'xyz',
        )

    def _scores_sent_with_args(self, *args, **kwargs):
        """
        Return True if scores are sent to the LTI consumer when the command is
        called with the specified arguments.
        """
        cmd = resend_lti_scores.Command()
        self._configure_lti(UsageKey.from_string(self.lti_block))
        with patch(u'lti_provider.outcomes.send_score_update') as mock_update:
            cmd.handle(*args, **kwargs)
            return mock_update.called

    def test_command_with_no_course_keys(self):
        self.assertTrue(self._scores_sent_with_args(course_keys=[]))

    def test_command_with_course_key(self):
        self.assertTrue(self._scores_sent_with_args(course_keys=[self.course_key]))

    def test_command_with_wrong_course_key(self):
        fake_course_key = self.store.make_course_key(u'not', u'the', u'course')
        self.assertFalse(self._scores_sent_with_args(course_keys=[fake_course_key]))
