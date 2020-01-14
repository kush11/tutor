"""
WE'RE USING MIGRATIONS!

If you make changes to this model, be sure to create an appropriate migration
file and check it in at the same time as your model changes. To do that,

1. Go to the edx-platform dir
2. ./manage.py lms schemamigration student --auto description_of_your_change
3. Add the migration file created in edx-platform/openedx/core/djangoapps/external_auth/migrations/
"""

from django.contrib.auth.models import User
from django.db import models


class ExternalAuthMap(models.Model):
    """
    Model class for external auth.
    """
    class Meta(object):
        app_label = "external_auth"
        unique_together = (('external_id', 'external_domain'), )

    external_id = models.CharField(max_length=255, db_index=True)
    external_domain = models.CharField(max_length=255, db_index=True)
    external_credentials = models.TextField(blank=True)  # JSON dictionary
    external_email = models.CharField(max_length=255, db_index=True)
    external_name = models.CharField(blank=True, max_length=255, db_index=True)
    user = models.OneToOneField(User, unique=True, db_index=True, null=True, on_delete=models.CASCADE)
    internal_password = models.CharField(blank=True, max_length=31)  	# randomly generated
    dtcreated = models.DateTimeField('creation date', auto_now_add=True)
    dtsignup = models.DateTimeField('signup date', null=True)		# set after signup

    def __unicode__(self):
        return "[%s] = (%s / %s)" % (self.external_id, self.external_name, self.external_email)
