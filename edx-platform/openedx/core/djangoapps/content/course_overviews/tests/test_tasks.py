import mock

from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from ..tasks import enqueue_async_course_overview_update_tasks


class BatchedAsyncCourseOverviewUpdateTests(ModuleStoreTestCase):
    def setUp(self):
        super(BatchedAsyncCourseOverviewUpdateTests, self).setUp()
        self.course_1 = CourseFactory.create(default_store=ModuleStoreEnum.Type.mongo)
        self.course_2 = CourseFactory.create(default_store=ModuleStoreEnum.Type.mongo)
        self.course_3 = CourseFactory.create(default_store=ModuleStoreEnum.Type.mongo)

    @mock.patch('openedx.core.djangoapps.content.course_overviews.models.CourseOverview.update_select_courses')
    def test_enqueue_all_courses_in_single_batch(self, mock_update_courses):
        enqueue_async_course_overview_update_tasks(
            course_ids=[],
            force_update=True,
            all_courses=True
        )

        called_args, called_kwargs = mock_update_courses.call_args_list[0]
        self.assertEqual(sorted([self.course_1.id, self.course_2.id, self.course_3.id]), sorted(called_args[0]))
        self.assertEqual({'force_update': True}, called_kwargs)
        self.assertEqual(1, mock_update_courses.call_count)

    @mock.patch('openedx.core.djangoapps.content.course_overviews.models.CourseOverview.update_select_courses')
    def test_enqueue_specific_courses_in_two_batches(self, mock_update_courses):
        enqueue_async_course_overview_update_tasks(
            course_ids=[unicode(self.course_1.id), unicode(self.course_2.id)],
            force_update=True,
            chunk_size=1,
            all_courses=False
        )

        mock_update_courses.assert_has_calls([
            mock.call([self.course_1.id], force_update=True),
            mock.call([self.course_2.id], force_update=True)
        ])
