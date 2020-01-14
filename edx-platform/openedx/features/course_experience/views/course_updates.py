"""
Views that handle course updates.
"""
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.template.context_processors import csrf
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from opaque_keys.edx.keys import CourseKey
from web_fragments.fragment import Fragment

from courseware.courses import get_course_info_section_module, get_course_with_access
from lms.djangoapps.courseware.views.views import CourseTabView
from openedx.core.djangoapps.plugin_api.views import EdxFragmentView
from openedx.features.course_experience import default_course_url_name

from .. import USE_BOOTSTRAP_FLAG

STATUS_VISIBLE = 'visible'
STATUS_DELETED = 'deleted'


def get_ordered_updates(request, course):
    """
    Returns any course updates in reverse chronological order.
    """
    info_module = get_course_info_section_module(request, request.user, course, 'updates')

    updates = info_module.items if info_module else []
    info_block = getattr(info_module, '_xmodule', info_module) if info_module else None
    ordered_updates = [update for update in updates if update.get('status') == STATUS_VISIBLE]
    ordered_updates.sort(
        key=lambda item: (safe_parse_date(item['date']), item['id']),
        reverse=True
    )
    for update in ordered_updates:
        update['content'] = info_block.system.replace_urls(update['content'])
    return ordered_updates


def safe_parse_date(date):
    """
    Since this is used solely for ordering purposes, use today's date as a default
    """
    try:
        return datetime.strptime(date, '%B %d, %Y')
    except ValueError:  # occurs for ill-formatted date values
        return datetime.today()


class CourseUpdatesView(CourseTabView):
    """
    The course updates page.
    """
    @method_decorator(login_required)
    @method_decorator(cache_control(no_cache=True, no_store=True, must_revalidate=True))
    def get(self, request, course_id, **kwargs):
        """
        Displays the home page for the specified course.
        """
        return super(CourseUpdatesView, self).get(request, course_id, 'courseware', **kwargs)

    def uses_bootstrap(self, request, course, tab):
        """
        Returns true if the USE_BOOTSTRAP Waffle flag is enabled.
        """
        return USE_BOOTSTRAP_FLAG.is_enabled(course.id)

    def render_to_fragment(self, request, course=None, tab=None, **kwargs):
        course_id = unicode(course.id)
        updates_fragment_view = CourseUpdatesFragmentView()
        return updates_fragment_view.render_to_fragment(request, course_id=course_id, **kwargs)


class CourseUpdatesFragmentView(EdxFragmentView):
    """
    A fragment to render the updates page for a course.
    """
    def render_to_fragment(self, request, course_id=None, **kwargs):
        """
        Renders the course's home page as a fragment.
        """
        course_key = CourseKey.from_string(course_id)
        course = get_course_with_access(request.user, 'load', course_key, check_if_enrolled=True)
        course_url_name = default_course_url_name(course.id)
        course_url = reverse(course_url_name, kwargs={'course_id': unicode(course.id)})

        ordered_updates = get_ordered_updates(request, course)
        plain_html_updates = ''
        if ordered_updates:
            plain_html_updates = self.get_plain_html_updates(request, course)

        # Render the course home fragment
        context = {
            'csrf': csrf(request)['csrf_token'],
            'course': course,
            'course_url': course_url,
            'updates': ordered_updates,
            'plain_html_updates': plain_html_updates,
            'disable_courseware_js': True,
            'uses_pattern_library': True,
        }
        html = render_to_string('course_experience/course-updates-fragment.html', context)
        return Fragment(html)

    @classmethod
    def has_updates(self, request, course):
        return len(get_ordered_updates(request, course)) > 0

    @classmethod
    def get_plain_html_updates(self, request, course):
        """
        Returns any course updates in an html chunk. Used
        for older implementations and a few tests that store
        a single html object representing all the updates.
        """
        info_module = get_course_info_section_module(request, request.user, course, 'updates')
        info_block = getattr(info_module, '_xmodule', info_module)
        return info_block.system.replace_urls(info_module.data) if info_module else ''
