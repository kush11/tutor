"""
Discussion API URLs
"""
from django.conf import settings
from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from discussion_api.views import CommentViewSet, CourseTopicsView, CourseView, ThreadViewSet, RetireUserView

ROUTER = SimpleRouter()
ROUTER.register("threads", ThreadViewSet, base_name="thread")
ROUTER.register("comments", CommentViewSet, base_name="comment")

urlpatterns = [
    url(
        r"^v1/courses/{}".format(settings.COURSE_ID_PATTERN),
        CourseView.as_view(),
        name="discussion_course"
    ),
    url(r"^v1/accounts/retire_forum", RetireUserView.as_view(), name="retire_discussion_user"),
    url(
        r"^v1/course_topics/{}".format(settings.COURSE_ID_PATTERN),
        CourseTopicsView.as_view(),
        name="course_topics"
    ),
    url("^v1/", include(ROUTER.urls)),
]
