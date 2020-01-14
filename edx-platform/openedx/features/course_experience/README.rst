Course Experience
-----------------

This directory contains a Django application that provides the Course Home page
(or course landing page), and various resources in support of the landing
experience.

The course experience consists of a number of views:

1. **Course Home**

   The course home page is the landing page for the course. It presents
   the learner with information necessary to understand the purpose of the
   course, its content, and its milestones. It includes a "Course Tools"
   section that provides links to other tools associated with the course.
   For example, it includes tools such as reviews, updates and bookmarks.

2. **Welcome Message**

   The welcome message is a fragment view which is typically shown on the
   course home page. It provides the user with a description of the course
   and helps them to understand its requirements.

3. **Course Outline**

   The course outline is a fragment view which shows an outline of the content
   of the course.

4. **Course Dates**

   The course dates fragment is a view which shows users important dates for the
   course, such as the start and end dates.

5. **Course Sock**

   The course sock is a fragment view which is typically shown just above
   the footer of course pages (hence the name). The default implementation
   presents the users with a message encouraging them to purchase a verified
   certificate.

6. **Course Updates**

   The course updates page shows the user all of the course team's updates
   in a scrolling list. The updates page is also provided as a course tool.

7. **Course Reviews**

   This page shows the user reviews of the course from an external provider.
   The default provider is `CourseTalk`_. The reviews page is also provided
   as a course tool.

A number of the features in the course experience are controlled via Waffle
flags. For documentation, see `Waffle flag definitions`_.

.. _CourseTalk: https://www.coursetalk.com/
.. _Waffle flag definitions: https://github.com/edx/edx-platform/blob/master/openedx/features/course_experience/__init__.py
