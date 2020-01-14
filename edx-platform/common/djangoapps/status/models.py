"""
Store status messages in the database.
"""

from config_models.admin import ConfigurationModelAdmin
from config_models.models import ConfigurationModel
from django.contrib import admin
from django.core.cache import cache
from django.db import models
from opaque_keys.edx.django.models import CourseKeyField


class GlobalStatusMessage(ConfigurationModel):
    """
    Model that represents the current status message.
    """
    message = models.TextField(
        blank=True,
        null=True,
        help_text='<p>The contents of this field will be displayed as a warning banner on all views.</p>'
                  '<p>To override the banner message for a specific course, refer to the Course Message configuration. '
                  'Course Messages will only work if the global status message is enabled, so if you only want to add '
                  'a banner to specific courses without adding a global status message, you should add a global status '
                  'message with <strong>empty</strong> message text.</p>'
                  '<p>Finally, disable the global status message by adding another empty message with "enabled" '
                  'unchecked.</p>')

    def full_message(self, course_key):
        """ Returns the full status message, including any course-specific status messages. """
        cache_key = "status_message.{course_id}".format(course_id=unicode(course_key))
        if cache.get(cache_key):
            return cache.get(cache_key)

        msg = self.message
        if course_key:
            try:
                course_home_message = self.coursemessage_set.get(course_key=course_key)
                # Don't override the message if course_home_message is blank.
                if course_home_message:
                    msg = u"{} <br /> {}".format(msg, course_home_message.message)
            except CourseMessage.DoesNotExist:
                # We don't have a course-specific message, so pass.
                pass
        cache.set(cache_key, msg)
        return msg

    def __unicode__(self):
        return "{} - {} - {}".format(self.change_date, self.enabled, self.message)


class CourseMessage(models.Model):
    """
    Model that allows the administrator to specify banner messages for individual courses.

    This is not a ConfigurationModel because using it's not designed to support multiple configurations at once,
    which would be problematic if separate courses need separate error messages.
    """
    global_message = models.ForeignKey(GlobalStatusMessage, on_delete=models.CASCADE)
    course_key = CourseKeyField(max_length=255, blank=True, db_index=True)
    message = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.course_key)


admin.site.register(GlobalStatusMessage, ConfigurationModelAdmin)
admin.site.register(CourseMessage)
