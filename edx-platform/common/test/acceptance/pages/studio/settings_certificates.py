"""
Course Certificates page objects.
The methods in these classes are organized into several conceptual buckets:
    * Helpers: General utility methods used throughout, such as css selection helpers
    * Properties: Specific page/object field getters/setters (mainly for form inputs)
    * Wait Actions: EmptyPromises used to ensure element availabilty prior to performing an action
    * Click Actions: Specific element invocations -- mainly links/buttons but anything clickable
    * Workflows: Complex orchestrations involving any/all of the above

"""
import os

from bok_choy.promise import EmptyPromise
from selenium.webdriver import ActionChains

from common.test.acceptance.pages.studio.course_page import CoursePage
from common.test.acceptance.tests.helpers import disable_animations


class CertificatesPage(CoursePage):
    """
    Course Certificates page object wrapper
    Further below you will also find page objects for Certificates and Signatories
    """

    url_path = "certificates"
    certficate_css = ".certificates-list"

    ################
    # Helpers
    ################

    def refresh(self):
        """
        Refresh the certificate page
        """
        self.browser.refresh()

    def is_browser_on_page(self):
        """
        Verify that the browser is on the page and it is not still loading.
        """
        EmptyPromise(
            lambda: self.q(css='body.view-certificates').present,
            'On the certificates page'
        ).fulfill()

        EmptyPromise(
            lambda: not self.q(css='span.spin').visible,
            'Certificates are finished loading'
        ).fulfill()

        return True

    def get_first_signatory_title(self):
        """
        Return signatory title for the first signatory in certificate.
        """
        return self.q(css='.signatory-title-value').first.html[0]

    def get_course_number(self):
        """
        Return Course Number
        """
        return self.q(css='.actual-course-number .certificate-value').first.text[0]

    def get_course_number_override(self):
        """
        Return Course Number Override
        """
        return self.q(css='.course-number-override .certificate-value').first.text[0]

    def course_number_override(self):
        """
        Return Course Number Override selector
        """
        return self.q(css='.course-number-override')

    ################
    # Properties
    ################

    @property
    def certificates(self):
        """
        Return list of the certificates for the course.
        """
        css = self.certficate_css + ' .wrapper-collection'
        return [CertificateSectionPage(self, self.certficate_css, index) for index in xrange(len(self.q(css=css)))]

    @property
    def no_certificates_message_shown(self):
        """
        Returns whether or not no certificates created message is present.
        """
        return self.q(css='.wrapper-content ' + self.certficate_css + ' .no-content').present

    @property
    def no_certificates_message_text(self):
        """
        Returns text of .no-content container.
        """
        return self.q(css='.wrapper-content ' + self.certficate_css + ' .no-content').text[0]

    @property
    def new_certificate_link_text(self):
        """
        Returns text of new-button link .
        """
        return self.q(css='.wrapper-content ' + self.certficate_css + ' .no-content a.new-button').text[0]

    ################
    # Wait Actions
    ################

    def wait_for_confirmation_prompt(self):
        """
        Show confirmation prompt
        We can't use confirm_prompt because its wait_for_notification is flaky when asynchronous operation
        completed very quickly.
        """
        EmptyPromise(
            lambda: self.q(css='.prompt').present,
            'Confirmation prompt is displayed'
        ).fulfill()
        EmptyPromise(
            lambda: self.q(css='.prompt .action-primary').present,
            'Primary button is displayed'
        ).fulfill()
        EmptyPromise(
            lambda: self.q(css='.prompt .action-primary').visible,
            'Primary button is visible'
        ).fulfill()

    def wait_for_first_certificate_button(self):
        """
        Ensure the button is available for use
        """
        EmptyPromise(
            lambda: self.q(css=self.certficate_css + " .new-button").present,
            'Create first certificate button is displayed'
        ).fulfill()

    def wait_for_add_certificate_button(self):
        """
        Ensure the button is available for use
        """
        EmptyPromise(
            lambda: self.q(css=self.certficate_css + " .action-add").present,
            'Add certificate button is displayed'
        ).fulfill()

    ################
    # Click Actions
    ################

    def click_first_certificate_button(self):
        """
        Clicks the 'Create your first certificate' button, which is only displayed at zero state
        """
        self.wait_for_first_certificate_button()
        self.q(css=self.certficate_css + " .new-button").first.click()

    def click_add_certificate_button(self):
        """
        Clicks the 'Add new certificate' button, which is displayed when certificates already exist
        """
        self.wait_for_add_certificate_button()
        self.q(css=self.certficate_css + " .action-add").first.click()

    def click_confirmation_prompt_primary_button(self):
        """
        Clicks the main action presented by the prompt (such as 'Delete')
        """
        disable_animations(self)
        self.wait_for_confirmation_prompt()
        self.q(css='.prompt button.action-primary').first.click()
        self.wait_for_element_invisibility('.prompt', 'wait for pop up to disappear')
        self.wait_for_ajax()


class CertificateSectionPage(CertificatesPage):
    """
    CertificateSectionPage is the certificate section within Certificates page, There might be multiple certificates
    in a Certificates Page so this section object can be used to used to identify unique certificate and apply
    operations on it.
    """

    def __init__(self, container, prefix, index):
        """
        Initialize CertificateSection Page

        :param container: Container Page Object of the certificate section
        :param prefix: css selector of the container element
        :param index: index of section in the certificate list on the page

        :return:
        """
        self.selector = prefix + ' .certificates-list-item-{}'.format(index)
        self.index = index

        super(CertificateSectionPage, self).__init__(container.browser, **container.course_info)

    def is_browser_on_page(self):
        """
        Verify that the browser is on the page and it is not still loading.
        """
        return self.q(css=".certificates").present

    @property
    def url(self):
        """
        Construct a URL to the page section within the certificate page.
        """
        # This is a page section and can not be accessed directly
        return None

    ################
    # Helpers
    ################

    def get_selector(self, css=''):
        """
        Return selector fo certificate container
        """
        return ' '.join([self.selector, css])

    def find_css(self, css_selector):
        """
        Find elements as defined by css locator.
        """
        return self.q(css=self.get_selector(css=css_selector))

    def get_text(self, css):
        """
        Return text for the defined by css locator.
        """
        return self.find_css(css).first.text[0]

    ################
    # Properties
    ################

    @property
    def validation_message(self):
        """
        Return validation message.
        """
        return self.get_text('.message-status.error')

    @property
    def mode(self):
        """
        Return certificate mode.
        """
        if self.find_css('.collection-edit').present:
            return 'edit'
        elif self.find_css('.collection').present:
            return 'details'

    @property
    # pylint: disable=invalid-name
    def id(self):
        """
        Returns certificate id.
        """
        return self.get_text('.certificate-id .certificate-value')

    @property
    def name(self):
        """
        Return certificate name.
        """
        return self.get_text('.name')

    @name.setter
    def name(self, value):
        """
        Set certificate name.
        """
        self.find_css('.collection-name-input').first.fill(value)

    @property
    def description(self):
        """
        Return certificate description.
        """
        return self.get_text('.certificate-description')

    @description.setter
    def description(self, value):
        """
        Set certificate description.
        """
        self.find_css('.certificate-description-input').first.fill(value)

    @property
    def course_title(self):
        """
        Return certificate course title override field.
        """
        return self.get_text('.course-title-override .certificate-value')

    @course_title.setter
    def course_title(self, value):
        """
        Set certificate course title override field.
        """
        self.find_css('.certificate-course-title-input').first.fill(value)

    @property
    def signatories(self):
        """
        Return list of the signatories for the certificate.
        """
        css = self.selector + ' .signatory-' + self.mode
        return [SignatorySectionPage(self, self.selector, self.mode, index) for index in xrange(len(self.q(css=css)))]

    ################
    # Wait Actions
    ################

    def wait_for_certificate_delete_button(self):
        """
        Returns whether or not the certificate delete icon is present.
        """
        EmptyPromise(
            lambda: self.find_css('.actions .delete.action-icon').present,
            'Certificate delete button is displayed'
        ).fulfill()

    def wait_for_hide_details_toggle(self):
        """
        Certificate details are expanded.
        """
        EmptyPromise(
            lambda: self.find_css('a.detail-toggle.hide-details').present,
            'Certificate details are expanded'
        ).fulfill()

    ################
    # Click Actions
    ################

    def click_create_certificate_button(self):
        """
        Create a new certificate.
        """
        disable_animations(self)
        self.find_css('.action-primary').first.click()
        self.wait_for_ajax()

    def click_save_certificate_button(self):
        """
        Save certificate.
        """
        self.find_css('.action-primary').first.click()
        self.wait_for_ajax()

    def click_add_signatory_button(self):
        """
        Add signatory to certificate
        """
        self.find_css('.action-add-signatory').first.click()

    def click_edit_certificate_button(self):
        """
        Open editing view for the certificate.
        """
        self.find_css('.action-edit .edit').first.click()

    def click_cancel_edit_certificate(self):
        """
        Cancel certificate editing.
        """
        self.find_css('.action-secondary').first.click()

    def click_certificate_details_toggle(self):
        """
        Expand/collapse certificate configuration.
        """
        self.find_css('a.detail-toggle').first.click()

    def click_delete_certificate_button(self):
        """
        Remove the first (possibly the only) certificate from the set
        """
        self.wait_for_certificate_delete_button()
        self.find_css('.actions .delete.action-icon').first.click()


class SignatorySectionPage(CertificatesPage):
    """
    SignatorySectionPage is the signatory section within CertificatesSection, There might be multiple signatories
    in a certificate section so this section object can be used to used to identify unique section and apply
    operations on it.
    """
    def __init__(self, container, prefix, mode, index):
        """
        Initialize SignatorySection Page

        :param container: Container Section Page Object of the Signatory section
        :param prefix: css selector of the container element
        :param index: index of section in the signatory list on the page
        :param mode: 'details' or 'edit', showing whether signatory is being displayed or edited

        :return:
        """
        self.prefix = prefix
        self.index = index
        self.mode = mode

        super(SignatorySectionPage, self).__init__(container.browser, **container.course_info)

    def is_browser_on_page(self):
        """
        Verify that the browser is on the page and it is not still loading.
        """
        return self.q(css=self.prefix + " .signatory-details-list, .signatory-edit-list").present

    @property
    def url(self):
        """
        Construct a URL to the page section within the certificate section page.
        """
        # This is a page section and can not be accessed directly
        return None

    ################
    # Helpers
    ################

    @staticmethod
    def file_path(filename):
        """
        Construct file path to be uploaded from the data upload folder.

        Arguments:
            filename (str): asset filename

        """
        # Should grab common point between this page module and the data folder.
        return os.sep.join(__file__.split(os.sep)[:-4]) + '/data/uploads/' + filename

    def get_selector(self, css=''):
        """
        Return selector fo signatory container
        """
        selector = self.prefix + ' .signatory-{}-view-{}'.format(self.mode, self.index)
        return ' '.join([selector, css])

    def find_css(self, css_selector):
        """
        Find elements as defined by css locator.
        """
        return self.q(css=self.get_selector(css=css_selector))

    ################
    # Properties
    ################

    @property
    def name(self):
        """
        Return signatory name.
        """
        return self.find_css('.signatory-panel-body .signatory-name-value').first.text[0]

    @name.setter
    def name(self, value):
        """
        Set signatory name.
        """
        self.find_css('.signatory-name-input').first.fill(value)

    @property
    def title(self):
        """
        Return signatory title.
        """
        return self.find_css('.signatory-panel-body .signatory-title-value').first.text[0]

    @title.setter
    def title(self, value):
        """
        Set signatory title.
        """
        self.find_css('.signatory-title-input').first.fill(value)

    @property
    def organization(self):
        """
        Return signatory organization.
        """
        return self.find_css('.signatory-panel-body .signatory-organization-value').first.text[0]

    @organization.setter
    def organization(self, value):
        """
        Set signatory organization.
        """
        self.find_css('.signatory-organization-input').first.fill(value)

    ################
    # Workflows
    ################

    def edit(self):
        """
        Open editing view for the signatory.
        """
        element = self.q(css='.edit-signatory').results[0]
        mouse_hover_action = ActionChains(self.browser).move_to_element(element)
        mouse_hover_action.perform()
        self.wait_for_element_visibility('.edit-signatory', 'Edit button visibility')
        element.click()
        self.wait_for_signatory_edit_view()

    def delete_signatory(self):
        """
        Delete the signatory
        """
        self.wait_for_signatory_delete_icon()
        self.click_signatory_delete_icon()
        self.wait_for_signatory_delete_prompt()

        self.q(css='#prompt-warning a.button.action-primary').first.click()
        self.wait_for_ajax()

    def save(self):
        """
        Save signatory.
        """
        # Click on the save button.
        self.q(css='button.signatory-panel-save').click()
        self.mode = 'details'
        self.wait_for_ajax()
        self.wait_for_signatory_detail_view()

    def close(self):
        """
        Cancel signatory editing.
        """
        self.q(css='button.signatory-panel-close').click()
        self.mode = 'details'
        self.wait_for_signatory_detail_view()

    def upload_signature_image(self, image_filename):
        """
        Opens upload image dialog and upload given image file.
        """
        self.wait_for_signature_image_upload_button()
        self.find_css('.action-upload-signature').first.click()
        self.wait_for_signature_image_upload_prompt()

        asset_file_path = self.file_path(image_filename)
        self.q(
            css='.assetupload-modal .upload-dialog input[type="file"]'
        )[0].send_keys(asset_file_path)

        EmptyPromise(
            lambda: not self.q(
                css='.assetupload-modal a.action-upload.disabled'
            ).present,
            'Upload button is not disabled anymore'
        ).fulfill()

        self.q(css='.assetupload-modal a.action-upload').first.click()
        EmptyPromise(
            lambda: not self.q(css='.assetupload-modal .upload-dialog').visible,
            'Upload dialog is removed after uploading image'
        ).fulfill()

    ################
    # Wait Actions
    ################

    @property
    def wait_for_signatory_delete_icon(self):
        """
        Returns whether or not the delete icon is present.
        """
        EmptyPromise(
            lambda: self.q(css='.signatory-panel-delete').present,
            'Delete icon is displayed'
        ).fulfill()

    def wait_for_signatory_delete_prompt(self):
        """
        Promise to wait until signatory delete prompt is visible
        """
        EmptyPromise(
            lambda: self.q(css='a.button.action-primary').present,
            'Delete prompt is displayed'
        ).fulfill()

    def wait_for_signatory_edit_view(self):
        """
        Promise to wait until signatory edit view is loaded
        """
        EmptyPromise(
            lambda: self.find_css('.signatory-panel-body .signatory-name-input').present,
            'On signatory edit view'
        ).fulfill()

    def wait_for_signatory_detail_view(self):
        """
        Promise to wait until signatory details view is loaded
        """
        EmptyPromise(
            lambda: self.find_css('.signatory-panel-body .signatory-name-value').present,
            'On signatory details view'
        ).fulfill()

    def wait_for_signature_image_upload_prompt(self):
        """
        Promise to wait until signatory image upload prompt is visible
        """
        EmptyPromise(
            lambda: self.q(css='.assetupload-modal .action-upload').present,
            'Signature image upload dialog opened'
        ).fulfill()

    def wait_for_signature_image_upload_button(self):
        """
        Promise to wait until signatory image upload button is visible
        """
        EmptyPromise(
            lambda: self.q(css=".action-upload-signature").first.present,
            'Signature image upload button available'
        ).fulfill()

    @property
    def wait_for_signature_image(self):
        """
        Promise for the signature image to be displayed
        """
        EmptyPromise(
            lambda: self.q(css=".current-signature-image .signature-image").present,
            'Signature image available'
        ).fulfill()

    ################
    # Click Actions
    ################

    def click_signatory_delete_icon(self):
        """
        Clicks the signatory deletion icon/action
        """
        self.find_css('.signatory-panel-delete').first.click()
