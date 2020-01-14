#   Copyright (c) 2008 Mikeal Rogers
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging
from urlparse import urljoin

from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse
from django.template import engines

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.theming.helpers import is_request_in_themed_site

from . import Engines

log = logging.getLogger(__name__)


def marketing_link(name):
    """Returns the correct URL for a link to the marketing site
    depending on if the marketing site is enabled

    Since the marketing site is enabled by a setting, we have two
    possible URLs for certain links. This function is to decides
    which URL should be provided.
    """
    # link_map maps URLs from the marketing site to the old equivalent on
    # the Django site
    link_map = settings.MKTG_URL_LINK_MAP
    enable_mktg_site = configuration_helpers.get_value(
        'ENABLE_MKTG_SITE',
        settings.FEATURES.get('ENABLE_MKTG_SITE', False)
    )
    marketing_urls = configuration_helpers.get_value(
        'MKTG_URLS',
        settings.MKTG_URLS
    )

    if enable_mktg_site and name in marketing_urls:
        # special case for when we only want the root marketing URL
        if name == 'ROOT':
            return marketing_urls.get('ROOT')
        # Using urljoin here allows us to enable a marketing site and set
        # a site ROOT, but still specify absolute URLs for other marketing
        # URLs in the MKTG_URLS setting
        # e.g. urljoin('http://marketing.com', 'http://open-edx.org/about') >>> 'http://open-edx.org/about'
        return urljoin(marketing_urls.get('ROOT'), marketing_urls.get(name))
    # only link to the old pages when the marketing site isn't on
    elif not enable_mktg_site and name in link_map:
        # don't try to reverse disabled marketing links
        if link_map[name] is not None:
            return reverse(link_map[name])
    else:
        log.debug("Cannot find corresponding link for name: %s", name)
        return '#'


def is_any_marketing_link_set(names):
    """
    Returns a boolean if any given named marketing links are configured.
    """

    return any(is_marketing_link_set(name) for name in names)


def is_marketing_link_set(name):
    """
    Returns a boolean if a given named marketing link is configured.
    """

    enable_mktg_site = configuration_helpers.get_value(
        'ENABLE_MKTG_SITE',
        settings.FEATURES.get('ENABLE_MKTG_SITE', False)
    )
    marketing_urls = configuration_helpers.get_value(
        'MKTG_URLS',
        settings.MKTG_URLS
    )

    if enable_mktg_site:
        return name in marketing_urls
    else:
        return name in settings.MKTG_URL_LINK_MAP


def marketing_link_context_processor(request):
    """
    A django context processor to give templates access to marketing URLs

    Returns a dict whose keys are the marketing link names usable with the
    marketing_link method (e.g. 'ROOT', 'CONTACT', etc.) prefixed with
    'MKTG_URL_' and whose values are the corresponding URLs as computed by the
    marketing_link method.
    """
    marketing_urls = configuration_helpers.get_value(
        'MKTG_URLS',
        settings.MKTG_URLS
    )

    return dict(
        [
            ("MKTG_URL_" + k, marketing_link(k))
            for k in (
                settings.MKTG_URL_LINK_MAP.viewkeys() |
                marketing_urls.viewkeys()
            )
        ]
    )


def footer_context_processor(request):  # pylint: disable=unused-argument
    """
    Checks the site name to determine whether to use the edX.org footer or the Open Source Footer.
    """
    return dict(
        [
            ("IS_REQUEST_IN_MICROSITE", is_request_in_themed_site())
        ]
    )


def render_to_string(template_name, dictionary, namespace='main', request=None):
    """
    Render a Mako template to as a string.

    The following values are available to all templates:
        settings: the django settings object
        EDX_ROOT_URL: settings.EDX_ROOT_URL
        marketing_link: The :func:`marketing_link` function
        is_any_marketing_link_set: The :func:`is_any_marketing_link_set` function
        is_marketing_link_set: The :func:`is_marketing_link_set` function

    Arguments:
        template_name: The name of the template to render. Will be loaded
            from the template paths specified in configuration.
        dictionary: A dictionary of variables to insert into the template during
            rendering.
        namespace: The Mako namespace to find the named template in.
        request: The request to use to construct the RequestContext for rendering
            this template. If not supplied, the current request will be used.
    """
    if namespace == 'lms.main':
        engine = engines[Engines.PREVIEW]
    else:
        engine = engines[Engines.MAKO]
    template = engine.get_template(template_name)
    return template.render(dictionary, request)


def render_to_response(template_name, dictionary=None, namespace='main', request=None, **kwargs):
    """
    Returns a HttpResponse whose content is filled with the result of calling
    lookup.get_template(args[0]).render with the passed arguments.
    """

    dictionary = dictionary or {}
    return HttpResponse(render_to_string(template_name, dictionary, namespace, request), **kwargs)
