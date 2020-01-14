"""
Import celery, load its settings from the django settings
and auto discover tasks in all installed django apps.

Taken from: https://celery.readthedocs.org/en/latest/django/first-steps-with-django.html
"""
from __future__ import absolute_import

import os

from celery import Celery
from django.conf import settings

from openedx.core.lib.celery.routers import AlternateEnvironmentRouter

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')

APP = Celery('proj')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
APP.config_from_object('django.conf:settings')
APP.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


class Router(AlternateEnvironmentRouter):
    """
    An implementation of AlternateEnvironmentRouter, for routing tasks to non-cms queues.
    """

    @property
    def alternate_env_tasks(self):
        """
        Defines alternate environment tasks, as a dict of form { task_name: alternate_queue }
        """
        # The tasks below will be routed to the default lms queue.
        return {
            'completion_aggregator.tasks.update_aggregators': 'lms',
            'openedx.core.djangoapps.content.block_structure.tasks.update_course_in_cache': 'lms',
            'openedx.core.djangoapps.content.block_structure.tasks.update_course_in_cache_v2': 'lms',
        }

    @property
    def explicit_queues(self):
        """
        Defines specific queues for tasks to run in (typically outside of the cms environment),
        as a dict of form { task_name: queue_name }.
        """
        return {
            'lms.djangoapps.grades.tasks.compute_all_grades_for_course': settings.POLICY_CHANGE_GRADES_ROUTING_KEY,
        }
