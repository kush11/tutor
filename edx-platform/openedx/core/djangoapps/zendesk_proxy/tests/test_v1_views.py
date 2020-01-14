"""Tests for zendesk_proxy views."""
import json
from copy import deepcopy

import ddt
from django.urls import reverse
from django.test.utils import override_settings
from mock import MagicMock, patch

from openedx.core.djangoapps.zendesk_proxy.v1.views import ZendeskProxyThrottle
from openedx.core.lib.api.test_utils import ApiTestCase


@ddt.ddt
@override_settings(
    ZENDESK_URL="https://www.superrealurlsthataredefinitelynotfake.com",
    ZENDESK_OAUTH_ACCESS_TOKEN="abcdefghijklmnopqrstuvwxyz1234567890"
)
class ZendeskProxyTestCase(ApiTestCase):
    """Tests for zendesk_proxy views."""

    def setUp(self):
        self.url = reverse('zendesk_proxy_v1')
        self.request_data = {
            'requester': {
                'email': 'JohnQStudent@example.com',
                'name': 'John Q. Student'
            },
            'subject': 'Python Unit Test Help Request',
            'comment': {
                'body': "Help! I'm trapped in a unit test factory and I can't get out!",
            },
            'tags': ['python_unit_test'],
            'custom_fields': [
                {
                    'id': '001',
                    'value': 'demo-course'
                }
            ],
        }
        return super(ZendeskProxyTestCase, self).setUp()

    def test_post(self):
        with patch('requests.post', return_value=MagicMock(status_code=201)) as mock_post:
            response = self.request_without_auth(
                'post',
                self.url,
                data=json.dumps(self.request_data),
                content_type='application/json'
            )
            self.assertHttpCreated(response)
            (mock_args, mock_kwargs) = mock_post.call_args
            self.assertEqual(mock_args, ('https://www.superrealurlsthataredefinitelynotfake.com/api/v2/tickets.json',))
            self.assertEqual(
                mock_kwargs,
                {
                    'headers': {
                        'content-type': 'application/json',
                        'Authorization': 'Bearer abcdefghijklmnopqrstuvwxyz1234567890'
                    },
                    'data': '{"ticket": {"comment": {"body": "Help! I\'m trapped in a unit test factory and I can\'t get out!", "uploads": null}, "tags": ["python_unit_test"], "subject": "Python Unit Test Help Request", "custom_fields": [{"id": "001", "value": "demo-course"}], "requester": {"name": "John Q. Student", "email": "JohnQStudent@example.com"}}}'  # pylint: disable=line-too-long
                }
            )

    @ddt.data('requester', 'tags')
    def test_bad_request(self, key_to_delete):
        test_data = deepcopy(self.request_data)
        _ = test_data.pop(key_to_delete)

        response = self.request_without_auth(
            'post',
            self.url,
            data=json.dumps(test_data),
            content_type='application/json'
        )
        self.assertHttpBadRequest(response)

    @override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'zendesk_proxy',
            }
        }
    )
    def test_rate_limiting(self):
        """
        Confirm rate limits work as expected. Note that drf's rate limiting makes use of the default cache to enforce
        limits; that's why this test needs a "real" default cache (as opposed to the usual-for-tests DummyCache)
        """

        for _ in range(ZendeskProxyThrottle().num_requests):
            self.request_without_auth('post', self.url)
        response = self.request_without_auth('post', self.url)
        self.assertEqual(response.status_code, 429)
