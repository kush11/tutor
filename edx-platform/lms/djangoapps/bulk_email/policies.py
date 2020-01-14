
from edx_ace.policy import Policy, PolicyResult
from edx_ace.channel import ChannelType
from opaque_keys.edx.keys import CourseKey

from bulk_email.models import Optout


class CourseEmailOptout(Policy):

    def check(self, message):
        course_ids = message.context.get('course_ids')
        if not course_ids:
            return PolicyResult(deny=frozenset())

        course_keys = [CourseKey.from_string(course_id) for course_id in course_ids]
        if Optout.objects.filter(user__username=message.recipient.username, course_id__in=course_keys).count() == len(course_keys):
            return PolicyResult(deny={ChannelType.EMAIL})

        return PolicyResult(deny=frozenset())
