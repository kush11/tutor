"""
Views to render a learner's achievements.
"""

from django.template.loader import render_to_string
from lms.djangoapps.certificates import api as certificate_api
from openedx.core.djangoapps.certificates.api import certificates_viewable_for_course
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.plugin_api.views import EdxFragmentView
from web_fragments.fragment import Fragment


class LearnerAchievementsFragmentView(EdxFragmentView):
    """
    A fragment to render a learner's achievements.
    """
    def render_to_fragment(self, request, username=None, own_profile=False, **kwargs):
        """
        Renders the current learner's achievements.
        """
        course_certificates = self._get_ordered_certificates_for_user(request, username)
        context = {
            'course_certificates': course_certificates,
            'own_profile': own_profile,
            'disable_courseware_js': True,
        }
        if course_certificates or own_profile:
            html = render_to_string('learner_profile/learner-achievements-fragment.html', context)
            return Fragment(html)
        else:
            return None

    def _get_ordered_certificates_for_user(self, request, username):
        """
        Returns a user's certificates sorted by course name.
        """
        course_certificates = certificate_api.get_certificates_for_user(username)
        passing_certificates = []
        for course_certificate in course_certificates:
            if course_certificate.get('is_passing', False):
                course_key = course_certificate['course_key']
                try:
                    course_overview = CourseOverview.get_from_id(course_key)
                    course_certificate['course'] = course_overview
                    if certificates_viewable_for_course(course_overview):
                        passing_certificates.append(course_certificate)
                except CourseOverview.DoesNotExist:
                    # This is unlikely to fail as the course should exist.
                    # Ideally the cert should have all the information that
                    # it needs. This might be solved by the Credentials API.
                    pass
        passing_certificates.sort(key=lambda certificate: certificate['course'].display_name_with_default)
        return passing_certificates
