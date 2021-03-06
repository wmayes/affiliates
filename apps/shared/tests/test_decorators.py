from django.conf import settings

from mock import patch
from nose.tools import eq_
from test_utils import TestCase

from badges.tests import LocalizingClient
from funfactory.urlresolvers import reverse


@patch.object(settings, 'LOGIN_VIEW_NAME', 'mock_login_view')
class TestLoginRequired(TestCase):
    client_class = LocalizingClient
    fixtures = ['registered_users']
    urls = 'shared.tests.urls'

    def test_basic(self):
        response = self.client.get(reverse('mock_view'))
        eq_(response.status_code, 302)
        eq_(response['Location'], 'http://testserver/en-US/mock_login_view')

    def test_logged_in(self):
        self.client.login(username='mkelly@mozilla.com', password='asdfasdf')
        response = self.client.get(reverse('mock_view'))
        eq_(response.status_code, 200)
