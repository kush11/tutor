import logging

from celery import task
from celery_utils.persist_on_failure import LoggedPersistOnFailureTask
from django.conf import settings

from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


log = logging.getLogger(__name__)


DEFAULT_ALL_COURSES = False

DEFAULT_CHUNK_SIZE = 50

DEFAULT_FORCE_UPDATE = False


def chunks(sequence, chunk_size):
    return (sequence[index: index + chunk_size] for index in xrange(0, len(sequence), chunk_size))


def _task_options(routing_key):
    task_options = {}
    if getattr(settings, 'HIGH_MEM_QUEUE', None):
        task_options['routing_key'] = settings.HIGH_MEM_QUEUE
    if routing_key:
        task_options['routing_key'] = routing_key
    return task_options


def enqueue_async_course_overview_update_tasks(
        course_ids,
        all_courses=False,
        force_update=False,
        chunk_size=DEFAULT_CHUNK_SIZE,
        routing_key=None
):
    if all_courses:
        course_keys = [course.id for course in modulestore().get_course_summaries()]
    else:
        course_keys = [CourseKey.from_string(id) for id in course_ids]

    for course_key_group in chunks(course_keys, chunk_size):
        course_key_strings = [unicode(key) for key in course_key_group]

        options = _task_options(routing_key)
        async_course_overview_update.apply_async(
            args=course_key_strings,
            kwargs={'force_update': force_update},
            **options
        )


@task(base=LoggedPersistOnFailureTask)
def async_course_overview_update(*args, **kwargs):
    course_keys = [CourseKey.from_string(arg) for arg in args]
    CourseOverview.update_select_courses(course_keys, force_update=kwargs['force_update'])
