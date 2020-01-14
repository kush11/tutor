"""Models for cross-domain configuration. """
from config_models.models import ConfigurationModel
from django.db import models
from django.utils.translation import ugettext_lazy as _


class XDomainProxyConfiguration(ConfigurationModel):
    """Cross-domain proxy configuration.

    See `openedx.core.djangoapps.cors_csrf.views.xdomain_proxy` for an explanation of how this works.

    """

    whitelist = models.fields.TextField(
        help_text=_(
            u"List of domains that are allowed to make cross-domain "
            u"requests to this site.  Please list each domain on its own line."
        )
    )

    def __unicode__(self):
        return "XDomainProxyConfiguration()"
