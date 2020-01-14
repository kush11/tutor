"""
Platform plugins to support the course experience.

This includes any locally defined CourseTools.
"""
from django.urls import reverse
from django.utils.translation import ugettext as _

from courseware.courses import get_course_by_id
from student.models import CourseEnrollment

from . import SHOW_REVIEWS_TOOL_FLAG, UNIFIED_COURSE_TAB_FLAG
from .course_tools import CourseTool
from .views.course_reviews import CourseReviewsModuleFragmentView
from .views.course_updates import CourseUpdatesFragmentView


class CourseUpdatesTool(CourseTool):
    """
    The course updates tool.
    """
    @classmethod
    def analytics_id(cls):
        """
        Returns an analytics id for this tool, used for eventing.
        """
        return 'edx.updates'

    @classmethod
    def title(cls):
        """
        Returns the title of this tool.
        """
        return _('Updates')

    @classmethod
    def icon_classes(cls):
        """
        Returns icon classes needed to represent this tool.
        """
        return 'fa fa-newspaper-o'

    @classmethod
    def is_enabled(cls, request, course_key):
        """
        Returns True if the user should be shown course updates for this course.
        """
        if not UNIFIED_COURSE_TAB_FLAG.is_enabled(course_key):
            return False
        if not CourseEnrollment.is_enrolled(request.user, course_key):
            return False
        course = get_course_by_id(course_key)
        return CourseUpdatesFragmentView.has_updates(request, course)

    @classmethod
    def url(cls, course_key):
        """
        Returns the URL for this tool for the specified course key.
        """
        return reverse('openedx.course_experience.course_updates', args=[course_key])


class CourseReviewsTool(CourseTool):
    """
    The course reviews tool.
    """
    @classmethod
    def analytics_id(cls):
        """
        Returns an id to uniquely identify this tool in analytics events.
        """
        return 'edx.reviews'

    @classmethod
    def title(cls):
        """
        Returns the title of this tool.
        """
        return _('Reviews')

    @classmethod
    def icon_classes(cls):
        """
        Returns icon classes needed to represent this tool.
        """
        return 'fa fa-star'

    @classmethod
    def is_enabled(cls, request, course_key):
        """
        Returns True if this tool is enabled for the specified course key.
        """
        if not SHOW_REVIEWS_TOOL_FLAG.is_enabled(course_key):
            return False
        return CourseReviewsModuleFragmentView.is_configured()

    @classmethod
    def url(cls, course_key):
        """
        Returns the URL for this tool for the specified course key.
        """
        return reverse('openedx.course_experience.course_reviews', args=[course_key])
