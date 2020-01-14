"""
Override admin configuration for django-oauth-toolkit
"""

from django.contrib.admin import ModelAdmin, site
from oauth2_provider import models

from .models import RestrictedApplication, ApplicationAccess, ApplicationOrganization


def reregister(model_class):
    """
    Remove the existing admin, and register it anew with the given ModelAdmin

    Usage:

        @reregister(ModelClass)
        class ModelClassAdmin(ModelAdmin):
            pass
    """
    def decorator(cls):
        """
        The actual decorator that does the work.
        """
        site.unregister(model_class)
        site.register(model_class, cls)
        return cls

    return decorator


@reregister(models.AccessToken)
class DOTAccessTokenAdmin(ModelAdmin):
    """
    Custom AccessToken Admin
    """
    date_hierarchy = u'expires'
    list_display = [u'token', u'user', u'application', u'expires']
    list_filter = [u'application']
    raw_id_fields = [u'user']
    search_fields = [u'token', u'user__username']


@reregister(models.RefreshToken)
class DOTRefreshTokenAdmin(ModelAdmin):
    """
    Custom AccessToken Admin
    """
    list_display = [u'token', u'user', u'application', u'access_token']
    list_filter = [u'application']
    raw_id_fields = [u'user', u'access_token']
    search_fields = [u'token', u'user__username', u'access_token__token']


@reregister(models.Grant)
class DOTGrantAdmin(ModelAdmin):
    """
    Custom Grant Admin
    """
    date_hierarchy = u'expires'
    list_display = [u'code', u'user', u'application', u'expires']
    list_filter = [u'application']
    raw_id_fields = [u'user']
    search_fields = [u'code', u'user__username']


@reregister(models.get_application_model())
class DOTApplicationAdmin(ModelAdmin):
    """
    Custom Application Admin
    """
    list_display = [u'name', u'user', u'client_type', u'authorization_grant_type', u'client_id']
    list_filter = [u'client_type', u'authorization_grant_type', u'skip_authorization']
    raw_id_fields = [u'user']
    search_fields = [u'name', u'user__username', u'client_id']


class ApplicationAccessAdmin(ModelAdmin):
    """
    ModelAdmin for ApplicationAccess
    """
    list_display = [u'application', u'scopes']


class ApplicationOrganizationAdmin(ModelAdmin):
    """
    ModelAdmin for ApplicationOrganization
    """
    list_display = [u'application', u'organization', u'relation_type']


class RestrictedApplicationAdmin(ModelAdmin):
    """
    ModelAdmin for the Restricted Application
    """
    list_display = [u'application']


site.register(ApplicationAccess, ApplicationAccessAdmin)
site.register(ApplicationOrganization, ApplicationOrganizationAdmin)
site.register(RestrictedApplication, RestrictedApplicationAdmin)
