"""Ensure emitted events contain the fields legacy processors expect to find."""

from collections import namedtuple

import ddt
from django.test.utils import override_settings
from mock import sentinel

from openedx.core.lib.tests.assertions.events import assert_events_equal

from . import FROZEN_TIME, EventTrackingTestCase
from .. import transformers
from ..shim import PrefixedEventProcessor

LEGACY_SHIM_PROCESSOR = [
    {
        'ENGINE': 'track.shim.LegacyFieldMappingProcessor'
    }
]

GOOGLE_ANALYTICS_PROCESSOR = [
    {
        'ENGINE': 'track.shim.GoogleAnalyticsProcessor'
    }
]


@override_settings(
    EVENT_TRACKING_PROCESSORS=LEGACY_SHIM_PROCESSOR,
)
class LegacyFieldMappingProcessorTestCase(EventTrackingTestCase):
    """Ensure emitted events contain the fields legacy processors expect to find."""

    def test_event_field_mapping(self):
        data = {sentinel.key: sentinel.value}

        context = {
            'accept_language': sentinel.accept_language,
            'referer': sentinel.referer,
            'username': sentinel.username,
            'session': sentinel.session,
            'ip': sentinel.ip,
            'host': sentinel.host,
            'agent': sentinel.agent,
            'path': sentinel.path,
            'user_id': sentinel.user_id,
            'course_id': sentinel.course_id,
            'org_id': sentinel.org_id,
            'client_id': sentinel.client_id,
        }
        with self.tracker.context('test', context):
            self.tracker.emit(sentinel.name, data)

        emitted_event = self.get_event()

        expected_event = {
            'accept_language': sentinel.accept_language,
            'referer': sentinel.referer,
            'event_type': sentinel.name,
            'name': sentinel.name,
            'context': {
                'user_id': sentinel.user_id,
                'course_id': sentinel.course_id,
                'org_id': sentinel.org_id,
                'path': sentinel.path,
            },
            'event': data,
            'username': sentinel.username,
            'event_source': 'server',
            'time': FROZEN_TIME,
            'agent': sentinel.agent,
            'host': sentinel.host,
            'ip': sentinel.ip,
            'page': None,
            'session': sentinel.session,
        }
        assert_events_equal(expected_event, emitted_event)

    def test_missing_fields(self):
        self.tracker.emit(sentinel.name)

        emitted_event = self.get_event()

        expected_event = {
            'accept_language': '',
            'referer': '',
            'event_type': sentinel.name,
            'name': sentinel.name,
            'context': {},
            'event': {},
            'username': '',
            'event_source': 'server',
            'time': FROZEN_TIME,
            'agent': '',
            'host': '',
            'ip': '',
            'page': None,
            'session': '',
        }
        assert_events_equal(expected_event, emitted_event)


@override_settings(
    EVENT_TRACKING_PROCESSORS=GOOGLE_ANALYTICS_PROCESSOR,
)
class GoogleAnalyticsProcessorTestCase(EventTrackingTestCase):
    """Ensure emitted events contain the fields necessary for Google Analytics."""

    def test_event_fields(self):
        """ Test that course_id is added as the label if present, and nonInteraction is set. """
        data = {sentinel.key: sentinel.value}

        context = {
            'path': sentinel.path,
            'user_id': sentinel.user_id,
            'course_id': sentinel.course_id,
            'org_id': sentinel.org_id,
            'client_id': sentinel.client_id,
        }
        with self.tracker.context('test', context):
            self.tracker.emit(sentinel.name, data)

        emitted_event = self.get_event()

        expected_event = {
            'context': context,
            'data': data,
            'label': sentinel.course_id,
            'name': sentinel.name,
            'nonInteraction': 1,
            'timestamp': FROZEN_TIME,
        }
        assert_events_equal(expected_event, emitted_event)

    def test_no_course_id(self):
        """ Test that a label is not added if course_id is not specified, but nonInteraction is still set. """
        data = {sentinel.key: sentinel.value}

        context = {
            'path': sentinel.path,
            'user_id': sentinel.user_id,
            'client_id': sentinel.client_id,
        }
        with self.tracker.context('test', context):
            self.tracker.emit(sentinel.name, data)

        emitted_event = self.get_event()

        expected_event = {
            'context': context,
            'data': data,
            'name': sentinel.name,
            'nonInteraction': 1,
            'timestamp': FROZEN_TIME,
        }
        assert_events_equal(expected_event, emitted_event)


@override_settings(
    EVENT_TRACKING_BACKENDS={
        '0': {
            'ENGINE': 'eventtracking.backends.routing.RoutingBackend',
            'OPTIONS': {
                'backends': {
                    'first': {'ENGINE': 'track.tests.InMemoryBackend'}
                },
                'processors': [
                    {
                        'ENGINE': 'track.shim.GoogleAnalyticsProcessor'
                    }
                ]
            }
        },
        '1': {
            'ENGINE': 'eventtracking.backends.routing.RoutingBackend',
            'OPTIONS': {
                'backends': {
                    'second': {
                        'ENGINE': 'track.tests.InMemoryBackend'
                    }
                }
            }
        }
    }
)
class MultipleShimGoogleAnalyticsProcessorTestCase(EventTrackingTestCase):
    """Ensure changes don't impact other backends"""

    def test_multiple_backends(self):
        data = {
            sentinel.key: sentinel.value,
        }

        context = {
            'path': sentinel.path,
            'user_id': sentinel.user_id,
            'course_id': sentinel.course_id,
            'org_id': sentinel.org_id,
            'client_id': sentinel.client_id,
        }
        with self.tracker.context('test', context):
            self.tracker.emit(sentinel.name, data)

        segment_emitted_event = self.tracker.backends['0'].backends['first'].events[0]
        log_emitted_event = self.tracker.backends['1'].backends['second'].events[0]

        expected_event = {
            'context': context,
            'data': data,
            'label': sentinel.course_id,
            'name': sentinel.name,
            'nonInteraction': 1,
            'timestamp': FROZEN_TIME,
        }
        assert_events_equal(expected_event, segment_emitted_event)

        expected_event = {
            'context': context,
            'data': data,
            'name': sentinel.name,
            'timestamp': FROZEN_TIME,
        }
        assert_events_equal(expected_event, log_emitted_event)


SequenceDDT = namedtuple('SequenceDDT', ['action', 'tab_count', 'current_tab', 'legacy_event_type'])


@ddt.ddt
class EventTransformerRegistryTestCase(EventTrackingTestCase):
    """
    Test the behavior of the event registry
    """

    def setUp(self):
        super(EventTransformerRegistryTestCase, self).setUp()
        self.registry = transformers.EventTransformerRegistry()

    @ddt.data(
        ('edx.ui.lms.sequence.next_selected', transformers.NextSelectedEventTransformer),
        ('edx.ui.lms.sequence.previous_selected', transformers.PreviousSelectedEventTransformer),
        ('edx.ui.lms.sequence.tab_selected', transformers.SequenceTabSelectedEventTransformer),
        ('edx.video.foo.bar', transformers.VideoEventTransformer),
    )
    @ddt.unpack
    def test_event_registry_dispatch(self, event_name, expected_transformer):
        event = {'name': event_name}
        transformer = self.registry.create_transformer(event)
        self.assertIsInstance(transformer, expected_transformer)

    @ddt.data(
        'edx.ui.lms.sequence.next_selected.what',
        'edx',
        'unregistered_event',
    )
    def test_dispatch_to_nonexistent_events(self, event_name):
        event = {'name': event_name}
        with self.assertRaises(KeyError):
            self.registry.create_transformer(event)


@ddt.ddt
class PrefixedEventProcessorTestCase(EventTrackingTestCase):
    """
    Test PrefixedEventProcessor
    """

    @ddt.data(
        SequenceDDT(action=u'next', tab_count=5, current_tab=3, legacy_event_type=u'seq_next'),
        SequenceDDT(action=u'next', tab_count=5, current_tab=5, legacy_event_type=None),
        SequenceDDT(action=u'previous', tab_count=5, current_tab=3, legacy_event_type=u'seq_prev'),
        SequenceDDT(action=u'previous', tab_count=5, current_tab=1, legacy_event_type=None),
    )
    def test_sequence_linear_navigation(self, sequence_ddt):
        event_name = u'edx.ui.lms.sequence.{}_selected'.format(sequence_ddt.action)

        event = {
            u'name': event_name,
            u'event': {
                u'current_tab': sequence_ddt.current_tab,
                u'tab_count': sequence_ddt.tab_count,
                u'id': u'ABCDEFG',
            }
        }

        process_event_shim = PrefixedEventProcessor()
        result = process_event_shim(event)

        # Legacy fields get added when needed
        if sequence_ddt.action == u'next':
            offset = 1
        else:
            offset = -1
        if sequence_ddt.legacy_event_type:
            self.assertEqual(result[u'event_type'], sequence_ddt.legacy_event_type)
            self.assertEqual(result[u'event'][u'old'], sequence_ddt.current_tab)
            self.assertEqual(result[u'event'][u'new'], sequence_ddt.current_tab + offset)
        else:
            self.assertNotIn(u'event_type', result)
            self.assertNotIn(u'old', result[u'event'])
            self.assertNotIn(u'new', result[u'event'])

    def test_sequence_tab_navigation(self):
        event_name = u'edx.ui.lms.sequence.tab_selected'
        event = {
            u'name': event_name,
            u'event': {
                u'current_tab': 2,
                u'target_tab': 5,
                u'tab_count': 9,
                u'id': u'block-v1:abc',
                u'widget_placement': u'top',
            }
        }

        process_event_shim = PrefixedEventProcessor()
        result = process_event_shim(event)
        self.assertEqual(result[u'event_type'], u'seq_goto')
        self.assertEqual(result[u'event'][u'old'], 2)
        self.assertEqual(result[u'event'][u'new'], 5)
