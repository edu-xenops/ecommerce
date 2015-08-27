import abc
import urllib

from bok_choy.page_object import PageObject
from bok_choy.promise import EmptyPromise
from selenium.webdriver.support.select import Select

from acceptance_tests.config import BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD, APP_SERVER_URL, LMS_URL


class EcommerceAppPage(PageObject):  # pylint: disable=abstract-method
    path = None

    @property
    def url(self):
        return self.page_url

    def __init__(self, browser, path=None):
        super(EcommerceAppPage, self).__init__(browser)
        path = path or self.path
        self.server_url = APP_SERVER_URL
        self.page_url = '{0}/{1}'.format(self.server_url, path)


class DashboardHomePage(EcommerceAppPage):
    path = 'dashboard'

    def is_browser_on_page(self):
        return self.browser.title.startswith('Dashboard | Oscar')


class LMSPage(PageObject):  # pylint: disable=abstract-method
    __metaclass__ = abc.ABCMeta

    def _build_url(self, path):
        url = '{0}/{1}'.format(LMS_URL, path)

        if BASIC_AUTH_USERNAME and BASIC_AUTH_PASSWORD:
            url = url.replace('://', '://{0}:{1}@'.format(BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD))

        return url

    def _is_browser_on_lms_dashboard(self):
        return lambda: self.browser.title.startswith('Dashboard')


class LMSLoginPage(LMSPage):
    def url(self, course_id=None):  # pylint: disable=arguments-differ
        url = self._build_url('login')

        if course_id:
            params = {'enrollment_action': 'enroll', 'course_id': course_id}
            url = '{0}?{1}'.format(url, urllib.urlencode(params))

        return url

    def is_browser_on_page(self):
        return self.q(css='form#login').visible

    def login(self, username, password):
        self.q(css='input#login-email').fill(username)
        self.q(css='input#login-password').fill(password)
        self.q(css='button.login-button').click()

        # Wait for LMS to redirect to the dashboard
        EmptyPromise(self._is_browser_on_lms_dashboard(), "LMS login redirected to dashboard").fulfill()


class LMSRegistrationPage(LMSPage):
    def url(self, course_id=None):  # pylint: disable=arguments-differ
        url = self._build_url('register')

        if course_id:
            params = {'enrollment_action': 'enroll', 'course_id': course_id}
            url = '{0}?{1}'.format(url, urllib.urlencode(params))

        return url

    def is_browser_on_page(self):
        return self.q(css='form#register').visible

    def register_and_login(self, username, name, email, password):
        self.q(css='input#register-username').fill(username)
        self.q(css='input#register-name').fill(name)
        self.q(css='input#register-email').fill(email)
        self.q(css='input#register-password').fill(password)

        select = Select(self.browser.find_element_by_css_selector('select#register-country'))
        select.select_by_value('US')

        self.q(css='input#register-honor_code').click()
        self.q(css='button.register-button').click()

        # Wait for LMS to redirect to the dashboard
        EmptyPromise(self._is_browser_on_lms_dashboard(), "LMS login redirected to dashboard").fulfill()


class LMSCourseModePage(LMSPage):
    def is_browser_on_page(self):
        return self.browser.title.lower().startswith('enroll in')

    @property
    def url(self):
        path = 'course_modes/choose/{}/'.format(urllib.quote_plus(self.course_id))
        return self._build_url(path)

    def __init__(self, browser, course_id):
        super(LMSCourseModePage, self).__init__(browser)
        self.course_id = course_id


class LMSDashboardPage(LMSPage):
    @property
    def url(self):
        return self._build_url('dashboard')

    def is_browser_on_page(self):
        return self.browser.title.startswith('Dashboard')
