"""
Decorators that can be used to interact with third_party_auth.
"""
from functools import wraps

from django.conf import settings
from django.shortcuts import redirect
from django.utils.decorators import available_attrs

from six.moves.urllib.parse import urlencode, urlparse
from third_party_auth.models import LTIProviderConfig
from third_party_auth.provider import Registry


def xframe_allow_whitelisted(view_func):
    """
    Modifies a view function so that its response has the X-Frame-Options HTTP header
    set to 'DENY' if the request HTTP referrer is not from a whitelisted hostname.
    """

    def wrapped_view(request, *args, **kwargs):
        """ Modify the response with the correct X-Frame-Options. """
        resp = view_func(request, *args, **kwargs)
        x_frame_option = 'DENY'
        if settings.FEATURES['ENABLE_THIRD_PARTY_AUTH']:
            referer = request.META.get('HTTP_REFERER')
            if referer is not None:
                parsed_url = urlparse(referer)
                hostname = parsed_url.hostname
                if LTIProviderConfig.objects.current_set().filter(lti_hostname=hostname, enabled=True).exists():
                    x_frame_option = 'ALLOW'
        resp['X-Frame-Options'] = x_frame_option
        return resp
    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)
