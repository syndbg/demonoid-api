from sys import version_info
from unittest import TestCase

if version_info >= (3, 3):
    from unittest import mock
else:
    import mock

from lxml.html import HtmlElement
from requests import Session, HTTPError, Response

from demonoid.urls import Url


class UrlTests(TestCase):

    def test_init_default_parameter_values(self):
        u = Url()
        self.assertEqual(Url.DEFAULT_BASE_URL, u.base_url)
        self.assertEqual('', u.path)
        self.assertEqual({}, u.params)
        self.assertIsInstance(u._session, Session)
        self.assertIsNone(u._DOM)

    def test_init_with_given_values(self):
        url = 'http://potato.com'
        path = '/salad'
        params = {'kickstarter': 'genius'}
        u = Url(url, path, params)
        self.assertEqual(url, u.base_url)
        self.assertEqual(path, u.path)
        self.assertEqual(params, u.params)
        self.assertIsInstance(u._session, Session)
        self.assertIsNone(u._DOM)

    def test_add_params(self):
        u = Url()
        params = {'page': 7, 'category': 0}
        u.add_params(params)
        self.assertEqual(params, u.params)

    def test_add_param(self):
        u = Url()
        u.add_param('page', 7)
        self.assertEqual({'page': 7}, u.params)

    def test_url_property(self):
        u = Url(Url.DEFAULT_BASE_URL, 'files')
        self.assertEqual(Url.DEFAULT_BASE_URL + 'files', u.url)

    def test_combine_path_when_trailing_slash_base_url(self):
        u = Url(Url.DEFAULT_BASE_URL)
        self.assertEqual(Url.DEFAULT_BASE_URL + 'files', u.combine('files'))

    def test_combine_path_when_base_url_without_trailing_slash(self):
        base_url = 'http://demonoid.pw'
        u = Url(base_url)
        self.assertEqual(base_url + '/files', u.combine('files'))

    def test_combine_path_with_trailing_slash_and_url_with_preceding_slash(self):
        u = Url(Url.DEFAULT_BASE_URL)
        self.assertEqual(Url.DEFAULT_BASE_URL + 'files', u.combine('/files'))

    @mock.patch('demonoid.urls.Url.update_DOM')
    def test_DOM_property_updates_DOM_when_called_for_the_first_time(self, patched_method):
        u = Url(Url.DEFAULT_BASE_URL)
        self.assertFalse(patched_method.called)
        self.assertIsNone(u._DOM)

        self.assertIs(u.DOM, u._DOM)
        self.assertTrue(patched_method.called)

    @mock.patch('demonoid.urls.Url.update_DOM')
    def test_DOM_property_reuses_existing_DOM(self, patched_method):
        u = Url(Url.DEFAULT_BASE_URL)
        u.DOM
        self.assertEqual(1, patched_method.call_count)
        u._DOM = 'something'  # manually change it
        self.assertEqual(1, patched_method.call_count)

    def test_update_DOM(self):
        u = Url(Url.DEFAULT_BASE_URL)
        self.assertIs(u, u.update_DOM())
        self.assertIsInstance(u._DOM, HtmlElement)

    def test_fetch_when_base_url_404s(self):
        u = Url('http://httpbin.org/status/404')
        with self.assertRaises(HTTPError):
            u.fetch()

    def test_fetch_when_base_url_200s(self):
        u = Url(Url.DEFAULT_BASE_URL)
        response = u.fetch()
        self.assertIsInstance(response, Response)
        self.assertEqual(200, response.status_code)

    def test_string_representation(self):
        u = Url(Url.DEFAULT_BASE_URL)
        self.assertEqual(Url.DEFAULT_BASE_URL, str(u))
