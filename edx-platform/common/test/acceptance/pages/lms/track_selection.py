"""Track selection page"""
from bok_choy.page_object import PageObject

from common.test.acceptance.pages.lms import BASE_URL
from common.test.acceptance.pages.lms.course_home import CourseHomePage
from common.test.acceptance.pages.lms.pay_and_verify import PaymentAndVerificationFlow


class TrackSelectionPage(PageObject):
    """Interact with the track selection page.

    This page can be accessed at `/course_modes/choose/{course_id}/`.
    """
    def __init__(self, browser, course_id):
        """Initialize the page.

        Arguments:
            browser (Browser): The browser instance.
            course_id (unicode): The course in which the user is enrolling.
        """
        super(TrackSelectionPage, self).__init__(browser)
        self._course_id = course_id

    @property
    def url(self):
        """Return the URL corresponding to the track selection page."""
        url = "{base}/course_modes/choose/{course_id}/".format(
            base=BASE_URL,
            course_id=self._course_id
        )

        return url

    def is_browser_on_page(self):
        """Check if the track selection page has loaded."""
        return self.q(css=".wrapper-register-choose").is_present()

    def enroll(self, mode="audit"):
        """Interact with one of the enrollment buttons on the page.

            Keyword Arguments:
                mode (str): Can be "audit" or "verified"

            Raises:
                ValueError
        """
        if mode == "verified":
            # Check the first contribution option, then click the enroll button
            self.q(css=".contribution-option > input").first.click()
            self.q(css="input[name='verified_mode']").click()
            return PaymentAndVerificationFlow(self.browser, self._course_id).wait_for_page()

        elif mode == "audit":
            self.q(css="input[name='audit_mode']").click()
            return CourseHomePage(self.browser, self._course_id).wait_for_page()

        else:
            raise ValueError("Mode must be either 'audit' or 'verified'.")
