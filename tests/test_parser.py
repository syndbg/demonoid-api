from sys import version_info
from unittest import TestCase

from lxml.html import HtmlElement
from requests import Session, HTTPError, Response

from demonoid.parser import Parser
from demonoid.urls import Url


class OfflineParserTests(TestCase):
    """
        Test Parser against offline Demonoid HTML pages.
    """

    def setUp(self):
        pass

    def test_get_torrent_rows(self):
        pass

    def test_get_date_row(self):
        pass

    def test_get_params(self):
        pass

    def test_parse_date(self):
        pass

    def test_parse_first_row(self):
        pass

    def test_parse_second_row(self):
        pass

    def test_parse_category_subcategory_and_or_quality(self):
        pass

    def test_parse_torrent_link(self):
        pass

    def test_is_subcategory(self):
        pass

    def test_is_quality(self):
        pass

    def test_is_language(self):
        pass


class OnlineParserTests(TestCase):
    """
       Test Parser against the current online Demonoid web server.
    """

    def setUp(self):
        url = Url(path='files')
        self.dom = url.DOM

    def test_get_torrents_rows(self):
        rows = Parser.get_torrents_rows(self.dom)
        first_row = rows[0]
        last_row = rows[-1]
        self.assertIsInstance(rows, list)
        # manually confirm that it  captures correct range of torrent rows
        self.assertTrue('added_today' in first_row.getchildren()[0].get('class'))
        # however I noticed that some torrents may have no properties and this test will fail.
        # Lets hope Demonoid staff fixes that
        self.assertIsNotNone(last_row.find('./td/a[@class="subcategory"]'))
        # usual amount of torrent rows per page. Hacky assertion.
        self.assertEqual(101, len(rows))

    def test_get_date_row_when_theres_such(self):
        rows = Parser.get_torrents_rows(self.dom)
        self.assertIsInstance(Parser.get_date_row(rows[0]), HtmlElement)

    def test_get_date_when_theres_none(self):
        rows = Parser.get_torrents_rows(self.dom)
        self.assertIsNone(Parser.get_date_row(rows[1]))

    def test_get_params_with_absolute_url(self):
        url = 'http://www.demonoid.pw/files/?category=0&subcategory=0&quality=0&seeded=2&external=2&query=&sort='
        expected_params = {'category': 0, 'subcategory': 0, 'quality': 0, 'seeded': 2, 'external': 2, 'query': '', 'sort': ''}
        self.assertDictEqual(expected_params, Parser.get_params(url))

    def test_get_params_with_empty_url(self):
        pass

    def test_get_params_with_query_only(self):
        pass

    def test_parse_date(self):
        pass

    def test_parse_first_row(self):
        pass

    def test_parse_second_row(self):
        pass

    def test_parse_category_subcategory_and_or_quality(self):
        pass

    def test_parse_torrent_link(self):
        pass

    def test_is_subcategory(self):
        pass

    def test_is_quality(self):
        pass

    def test_is_language(self):
        pass

